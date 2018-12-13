# -*- coding: utf-8 -*-

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import configparser
import json
import random
import requests
import threading
import time
import urllib3
import uuid

from core.log import setup_custom_logger
from db.manager import DBManager
from flask import current_app

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGGER = setup_custom_logger(__name__)
CONFIG_PATH = "./"


class OSMException(Exception):
    pass


def check_authorization(f):
    """
    Decorator to validate authorization prior API call
    """
    def wrapper(*args):
        response = requests.get(args[0].ns_descriptors_url,
                                headers=args[0].headers,
                                verify=False)
        if response.status_code in (401, 500):
            args[0].new_token(args[0].username,
                              args[0].password)
        return f(*args)
    return wrapper


class OSMR4():
    """
    OSM release 4 northbound API client (NBI)
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('{0}conf/nfvo.conf'.format(CONFIG_PATH))
        self.base_url = "{0}://{1}:{2}".format(
            config["nbi"]["protocol"],
            config["nbi"]["host"],
            config["nbi"]["port"])
        nfvo_mspl_category = configparser.ConfigParser()
        nfvo_mspl_category.read("{0}conf/nfvo.mspl.conf".format(CONFIG_PATH))
        mspl_monitoring = nfvo_mspl_category["monitoring"]
        self.monitoring_timeout = int(mspl_monitoring["timeout"])
        self.monitoring_interval = int(mspl_monitoring["interval"])
        self.monitoring_target_status = mspl_monitoring["target_status"]
        self.default_kvm_datacenter = \
            config["nbi"]["default_kvm_datacenter"]
        self.default_docker_datacenter = \
            config["nbi"]["default_docker_datacenter"]
        self.default_flavor = config["nbi"]["default_flavor"]
        self.token_url = "{0}/osm/admin/v1/tokens".format(self.base_url)
        self.ns_descriptors_url = "{0}/osm/nsd/v1/ns_descriptors".\
                                  format(self.base_url)
        self.ns_descriptors_content_url = \
            "{0}/osm/nsd/v1/ns_descriptors_content".\
            format(self.base_url)
        self.vnf_descriptors_url = "{0}/osm/vnfpkgm/v1/vnf_packages".\
                                   format(self.base_url)
        self.vnf_instances_url = "{0}/osm/nslcm/v1/vnfrs".\
                                 format(self.base_url)
        self.instantiate_url = "{0}/osm/nslcm/v1/ns_instances".\
                               format(self.base_url)
        self.vim_accounts_url = "{0}/osm/admin/v1/vim_accounts".\
                                format(self.base_url)
        self.exec_action_url = \
            "{0}/osm/nslcm/v1/ns_instances/<ns_instance_id>/action".\
            format(self.base_url)
        self.headers = {"Accept": "application/json"}
        self.token = None
        self.username = config["nbi"]["username"]
        self.password = config["nbi"]["password"]

    def new_token(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        response = requests.post(self.token_url,
                                 json={"username": self.username,
                                       "password": self.password},
                                 headers=self.headers,
                                 verify=False)
        token = json.loads(response.text).get("id")
        self.headers.update({"Authorization": "Bearer {0}".format(token)})
        return token

    @check_authorization
    def get_ns_descriptor_id(self, ns_name):
        response = requests.get(self.ns_descriptors_url,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        for nsd in nsds:
            if nsd["name"] == ns_name:
                return nsd["_id"]
        return

    @check_authorization
    def get_ns_r4__descriptors(self, ns_name=None):
        response = requests.get(self.ns_descriptors_url,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        if ns_name:
            return {"ns": [x for x in nsds
                           if x["name"] == ns_name]}
        return {"ns": [x for x in nsds]}

    @check_authorization
    def get_ns_descriptors(self, ns_name=None):
        response = requests.get(self.ns_descriptors_url,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        if ns_name:
            return {"ns": [self.translate_ns_descriptor(x) for x in nsds
                           if x["name"] == ns_name]}
        return {"ns": [self.translate_ns_descriptor(x) for x in nsds]}

    @check_authorization
    def get_vnf_descriptors(self, vnf_name=None):
        response = requests.get(self.vnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        vnfs = json.loads(response.text)
        if vnf_name:
            return {"vnsf": [self.translate_vnf_descriptor(x) for x in vnfs
                             if x["name"] == vnf_name]}
        return {"vnsf": [self.translate_vnf_descriptor(x) for x in vnfs]}

    def translate_ns_descriptor(self, nsd):
        tnsd = {}
        tnsd["constituent_vnfs"] = []
        for cvnf in nsd["constituent-vnfd"]:
            cvnf["member-vnf-index"] = int(cvnf["member-vnf-index"])
            cvnf.update({"start-by-default": "true"})
            tnsd["constituent_vnfs"].append(cvnf)
        tnsd["description"] = nsd["description"]
        tnsd["ns_name"] = nsd["name"]
        tnsd["vendor"] = nsd.get("vendor", None)
        tnsd["version"] = nsd.get("version", None)
        tnsd["id"] = nsd["id"]
        tnsd["vld"] = [self.translate_virtual_link_descriptor(x,
                                                              tnsd["vendor"],
                                                              tnsd["version"])
                       for x in nsd["vld"]]
        return tnsd

    def translate_vnf_descriptor(self, vnf):
        tvnfd = {}
        tvnfd["charm"] = ""
        tvnfd["description"] = vnf["description"]
        tvnfd["vendor"] = vnf.get("vendor", None)
        tvnfd["version"] = vnf.get("version", None)
        tvnfd["charm"] = {}
        if vnf["vnf-configuration"].get("juju", None):
            tvnfd["charm"] = \
                vnf["vnf-configuration"].get("juju", None)["charm"]
        nss = self.get_ns_descriptors()
        tvnfd["ns_name"] = None
        for ns in nss["ns"]:
            for cvnf in ns["constituent_vnfs"]:
                if cvnf["vnfd-id-ref"] == vnf["name"]:
                    tvnfd["ns_name"] = ns["ns_name"]
        return tvnfd

    def translate_virtual_link_descriptor(self, vld, vendor, version):
        tvld = {}
        tvld["id"] = vld["id"]
        tvld["description"] = vld["name"]
        tvld["mgmt-network"] = vld.get("mgmt-network", "false")
        tvld["short-name"] = vld.get("shortname", vld["name"])
        tvld["name"] = vld["name"]
        tvld["type"] = vld["type"]
        tvld["version"] = version
        tvld["vendor"] = vendor
        tvld["vnfd-connection-point-ref"] = []
        for cpref in vld["vnfd-connection-point-ref"]:
            cpref["member-vnf-index-ref"] = int(cpref["member-vnf-index-ref"])
            tvld["vnfd-connection-point-ref"].append(cpref)
        return tvld

    @check_authorization
    def get_ns_descriptors_content(self):
        response = requests.get(self.ns_descriptors_content_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    @check_authorization
    def get_pnf_descriptors(self):
        response = requests.get(self.pnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    def apply_mspl_action(self, instance_id, instantiation_data):
        if ("action" not in instantiation_data) or ("params"
                                                    not in instantiation_data):
            return
        print("Configuring instance, starting thread ...")
        target_status = None
        if "target_status" in instantiation_data:
            target_status = instantiation_data["target_status"]
        # Passing also current_app._get_current_object() (flask global context)
        t = threading.Thread(target=self.deployment_monitor_thread,
                             args=(instance_id,
                                   instantiation_data["action"],
                                   instantiation_data["params"],
                                   current_app._get_current_object(),
                                   target_status))
        t.start()

    def deployment_monitor_thread(self, instance_id, action,
                                  params, app, target_status=None):
        timeout = self.monitoring_timeout
        action_submitted = False
        if target_status is None:
            target_status = self.monitoring_target_status
        while not action_submitted:
            time.sleep(self.monitoring_interval)
            timeout = timeout-self.monitoring_interval
            print("Checking {0} {1} {2}".format(instance_id, action, params))
            try:
                nss = self.get_ns_r4_instances(instance_id)
            except OSMException:
                LOGGER.info("No instance found, aborting configuration")
                break
            if timeout < 0:
                print("Timeout reached, aborting thread")
                break
            if not nss:
                print("No instance found, aborting thread")
                break
            operational_status = nss.get("operational-status", "")
            if operational_status == "failed":
                print("Instance failed, aborting")
                break
            if operational_status == target_status and \
               "constituent-vnfr-ref" in nss:
                # Perform action on all vnf instances?
                for vnsf_instance in nss["constituent-vnfr-ref"]:
                    # exec_tmpl = self.fill_vnf_action_request_encoded(
                    #     vnsf_instance["vnfr_id"], action, params)
                    payload = {"action": action,
                               "params": params}
                    output = self.exec_action_on_vnf(payload)
                    output = "{}"
                    if action is not None:
                        app.mongo.store_vnf_action(vnsf_instance,
                                                   action,
                                                   params,
                                                   json.loads(output))
                        LOGGER.info(
                            "Action performed and stored, exiting thread")
                        LOGGER.info(output)
                    action_submitted = True
            else:
                print("Operational status: {0}, waiting ...".
                      format(operational_status))
        return

    @check_authorization
    def post_ns_instance(self, instantiation_data):
        if "vim_id" not in instantiation_data:
            vim_account_id = self.default_kvm_datacenter
            if "virt_type" in instantiation_data:
                if instantiation_data["virt_type"] == "docker":
                    # Replacing instance_name in case it is
                    # a Docker deployment to avoid naming
                    # overlap
                    instantiation_data["instance_name"] = \
                        str(uuid.uuid4()).replace("-", "")
                    instantiation_data["vim_id"] = \
                        vim_account_id = self.default_docker_datacenter
        if "description" not in instantiation_data:
            description = instantiation_data["ns_name"]
        if "nsd_id" not in instantiation_data:
            nsd_id = self.get_ns_descriptor_id(instantiation_data["ns_name"])
        ns_data = {"nsdId": nsd_id,
                   "nsName": instantiation_data["ns_name"],
                   "nsDescription": description,
                   "vimAccountId": vim_account_id}
        response = requests.post(self.instantiate_url,
                                 headers=self.headers,
                                 verify=False,
                                 json=ns_data)
        response_data = json.loads(response.text)
        inst_url = "{0}/{1}/instantiate".format(self.instantiate_url,
                                                response_data["id"])
        resp = requests.post(inst_url,
                             headers=self.headers,
                             verify=False,
                             json=ns_data)
        if resp.status_code in(200, 201, 202):
            success_msg = {"instance_name":
                           instantiation_data["instance_name"],
                           "instance_id": response_data["id"],
                           "ns_name": instantiation_data["ns_name"],
                           "vim_id": vim_account_id,
                           "result": "success"}
            self.apply_mspl_action(response_data["id"],
                                   instantiation_data)
            return success_msg
        else:
            error_msg = {"result": "error",
                         "error_response": resp}
            return error_msg

    @check_authorization
    def delete_ns_instance(self, nsr_id):
        inst_url = "{0}/{1}".format(self.instantiate_url,
                                    nsr_id)
        requests.post("{0}/terminate".format(inst_url),
                      headers=self.headers,
                      verify=False)
        requests.delete("{0}".format(inst_url),
                        headers=self.headers,
                        verify=False)
        # Uncomment next lines in case asynchronous behavior is preferred
        # t = threading.Thread(target=self.monitor_ns_deletion,
        #                      args=(nsr_id,
        #                            current_app._get_current_object()))
        # t.start()
        # Comment next line in case you want asynchronous behavior
        self.monitor_ns_deletion(nsr_id, current_app._get_current_object())
        success_msg = {"instance_id": nsr_id,
                       "action": "delete",
                       "result": "success"}
        return success_msg

    @check_authorization
    def monitor_ns_deletion(self, ns_instance_id, app):
        timeout = 90
        inst_url = "{0}/{1}".format(self.instantiate_url,
                                    ns_instance_id)
        while timeout > 0:
            try:
                ns_status = self.get_ns_r4_instances(ns_instance_id)
                status = ns_status["operational-status"]
                LOGGER.info("Operational Status = {0}".format(status))
                if status == "terminated":
                    LOGGER.info("Terminated already")
                    break
            except OSMException:
                break
            timeout -= 1
            time.sleep(1)
        delete = requests.delete(inst_url,
                                 headers=self.headers,
                                 verify=False)
        LOGGER.info("Terminating {0}".format(delete.text))

    @check_authorization
    def get_ns_r4_instances(self, nsr_id=None):
        if nsr_id is not None:
            inst_url = "{0}/{1}".format(self.instantiate_url,
                                        nsr_id)
        else:
            inst_url = "{0}".format(self.instantiate_url)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        if response.status_code not in (200, 201, 202):
            raise OSMException
        return json.loads(response.text)

    @check_authorization
    def get_ns_instance_name(self, nsr_id):
        inst_url = "{0}/{1}".format(self.instantiate_url,
                                    nsr_id)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        ns_instances = json.loads(response.text)
        iparams = ns_instances.get("instantiate_params", None)
        if iparams:
            return iparams.get("nsName", None)
        else:
            return None

    @check_authorization
    def get_ns_instances(self, nsr_id=None):
        if nsr_id is not None:
            inst_url = "{0}/{1}".format(self.instantiate_url,
                                        nsr_id)
        else:
            inst_url = "{0}".format(self.instantiate_url)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        ns_instances = json.loads(response.text)
        ns_data = {"ns":
                   [self.translate_ns_instance(x) for x in ns_instances]}
        return ns_data

    def translate_ns_instance(self, nsi):
        tnsi = {}
        tnsi["config_status"] = nsi["config-status"]
        tnsi["constituent_vnf_instances"] = []
        vnfis = self.get_vnf_instances(nsi["_id"])
        for vnfi in vnfis:
            vnfi.update({"ns_name": nsi.get("ns_name", nsi.get("name"))})
            vnfi.update({"vnfr_name": "{0}__{1}__1".format(nsi["nsd-name-ref"],
                                                           vnfi["vnfd_id"])})
            # Reminder: populate existing config jobs from the model
            dbm = DBManager()
            vnfi.update({"config_jobs": dbm.get_vnf_actions(vnfi["vnfr_id"])})
            tnsi["constituent_vnf_instances"].append(vnfi)
        tnsi["instance_id"] = nsi["id"]
        tnsi["instance_name"] = nsi["name"]
        # tnsi["name"] = nsi["name"]
        tnsi["ns_name"] = nsi["nsd-name-ref"]
        tnsi["nsd_id"] = nsi["nsd-ref"]
        tnsi["operational_status"] = nsi["operational-status"]
        if tnsi["operational_status"] == "ACTIVE":
            tnsi["operational_status"] = "running"
        tnsi["vlrs"] = vnfis[0].get("vlrs", [])
        return tnsi

    @check_authorization
    def get_vnf_instances(self, ns_instance_id=None):
        if ns_instance_id is None:
            nss = self.get_ns_instances()
            nss_ids = [x["instance_id"] for x in nss["ns"]]
            vnsfs = []
            for ns_instance_id in nss_ids:
                url = "{0}?nsr-id-ref={1}".format(
                    self.vnf_instances_url, ns_instance_id)
                response = requests.get(url,
                                        headers=self.headers,
                                        verify=False)
                for vnsf in json.loads(response.text):
                    vnsfs.append(vnsf)
            return {"vnsf":
                    [self.translate_vnf_instance(x)
                     for x in vnsfs]}
        url = "{0}?nsr-id-ref={1}".format(
            self.vnf_instances_url, ns_instance_id)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vnfis = json.loads(response.text)
        return [self.translate_vnf_instance(x) for x in vnfis]

    @check_authorization
    def translate_vnf_instance(self, vnfi):
        tvnfi = {}
        vdur = {}
        if len(vnfi["vdur"]) > 0:
            vdur = vnfi["vdur"][0]
        tvnfi["operational_status"] = vdur.get("status", "null")
        if tvnfi["operational_status"] == "ACTIVE":
            tvnfi["operational_status"] = "running"
        tvnfi["config_status"] = "config-not-needed"
        tvnfi["ip"] = vdur.get("ip-address", "null")
        tvnfi["ns_id"] = vnfi.get("nsr-id-ref")
        vnfd = self.get_vnf_descriptor(vnfi.get("vnfd-ref", "null"))
        if vnfd:
            tvnfi["vendor"] = vnfd["vendor"]
        else:
            tvnfi["vendor"] = None
        vim = self.get_vim_account(vnfi.get("vim-account-id"))
        if vim:
            tvnfi["vim"] = vim["name"]
        else:
            tvnfi["vim"] = None
        tvnfi["vnfd_id"] = vnfi["vnfd-ref"]
        tvnfi["vnfr_name"] = vnfi["vnfd-ref"]
        tvnfi["vnfr_id"] = vnfi["id"]
        tvnfi["ns_name"] = self.get_ns_instance_name(tvnfi["ns_id"])
        return tvnfi

    @check_authorization
    def get_vnf_descriptor(self, vnf_name):
        url = "{0}?name={1}".format(
            self.vnf_descriptors_url, vnf_name)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vnfds = json.loads(response.text)
        target_vnfd = None
        for vnfd in vnfds:
            if vnfd["name"] == vnf_name:
                target_vnfd = vnfd
        return target_vnfd

    @check_authorization
    def get_vim_account(self, vim_account_id):
        url = "{0}".format(self.vim_accounts_url)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vims = json.loads(response.text)
        target_vim = None
        for vim in vims:
            if str(vim["_id"]) == str(vim_account_id):
                target_vim = vim
        return target_vim

    @check_authorization
    def exec_action_on_vnf(self, payload):
        # JSON
        # resp = requests.post(
        #        endpoints.VNF_ACTION_EXEC,
        #        headers=endpoints.post_default_headers(),
        #        data=json.dumps(payload),
        #        verify=False)

        # Encoded
        # payload = payload.replace('\\"', '"').strip()
        # Find out which ns_id holds the vnf:
        nsis = self.get_ns_instances()["ns"]
        nsi_id = None
        for nsi in nsis:
            for vnfi in nsi["constituent_vnf_instances"]:
                print(vnfi)
                if vnfi["vnfr_id"] == payload["vnfr_id"]:
                    nsi_id = nsi["instance_id"]
        url = self.exec_action_url
        url.replace("<ns_instance_id>", nsi_id)
        r4_payload = {
            "primitive": payload["action"],
            "primitive_params": payload["params"]}
        resp = requests.post(
            url,
            headers=self.headers,
            data=r4_payload,
            verify=False)
        # output = json.loads(resp.text)
        output = resp.text
        return output

    def submit_action_request(self, vnfr_id=None, action=None, params=list()):
        params_exist = all(map(lambda x: x is not None,
                               [vnfr_id, action, params]))
        if not params_exist:
            return {"Error": "Missing argument"}
        exec_tmpl = self.fill_vnf_action_request_encoded(
            vnfr_id, action, params)
        output = self.exec_action_on_vnf(exec_tmpl)
        try:
            output_dict = json.loads(output)
        except Exception:
            return {"Error": "SO-ub output is not valid JSON",
                    "output": output}
        # Keep track of remote action per vNSF
        if action is not None:
            current_app.mongo.store_vnf_action(vnfr_id,
                                               action,
                                               params,
                                               output_dict)
        return output


if __name__ == "__main__":
    OSM = OSMR4()
    NSD_IDS = [x["_id"] for x in OSM.get_ns_descriptors()]
    print(random.choice(NSD_IDS))
    NSR = OSM.post_ns_instance("833bb02c-92e4-4fdb-ac55-cc927acfd2e7",
                               "Test",
                               "Test instance")
    print(OSM.get_ns_instance(NSR["id"]))
    time.sleep(180)
    OSM.delete_ns_instance(NSR["id"])
