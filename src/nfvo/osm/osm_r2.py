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

from core.config import FullConfParser
from core import regex
from flask import current_app
from nfvi.vim import VnsfoVim as vim_s
from nfvo.osm import endpoints
from nfvo.osm import \
    NFVO_DEFAULT_KVM_DATACENTER, NFVO_DEFAULT_KVM_DATACENTER_NET
from nfvo.osm import \
    NFVO_DEFAULT_DOCKER_DATACENTER, NFVO_DEFAULT_DOCKER_DATACENTER_NET
from mimetypes import MimeTypes
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from templates import nfvo as nfvo_tmpl
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import ImmutableMultiDict

import json
import os
import requests
import shutil
import threading
import time
import urllib3
import uuid

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OSMR2():
    """
    OSM release 2 client
    """

    def __init__(self):
        self.config = FullConfParser()
        self.nfvo_mspl_category = self.config.get("nfvo.mspl.conf")
        self.mspl_monitoring = self.nfvo_mspl_category.get("monitoring")
        self.monitoring_timeout = int(self.mspl_monitoring.get("timeout"))
        self.monitoring_interval = int(self.mspl_monitoring.get("interval"))
        self.monitoring_target_status = self.\
            mspl_monitoring.get("target_status")
        self.vnfo_vim = vim_s()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get_ns_descriptors(self, ns_name=None):
        resp = requests.get(
                endpoints.NS_CATALOG_C,
                headers=endpoints.get_default_headers(),
                verify=False)
        # Yep, this could be insecure - but the output comes from NFVO
        catalog = eval(resp.text) if resp.text else []
        if ns_name is None:
            # Returning all ns_catalog_descriptors
            return self.format_ns_catalog_descriptors(catalog)
        else:
            # Filtering by name
            fcatalog = self.format_ns_catalog_descriptors(catalog)
            return [x for x in fcatalog["ns"] if x["ns_name"] == ns_name]

    def get_ns_descriptors_content(self):
        pass

    def get_pnf_descriptors(self):
        pass

    def post_ns_instance(self, instantiation_data):
        if "vim_id" not in instantiation_data:
            instantiation_data["vim_id"] = \
                NFVO_DEFAULT_KVM_DATACENTER
            if "virt_type" in instantiation_data:
                if instantiation_data["virt_type"] == "docker":
                    # Replacing instance_name in case it is
                    # a Docker deployment to avoid naming
                    # overlap
                    instantiation_data["instance_name"] = \
                        str(uuid.uuid4()).replace("-", "")
                    instantiation_data["vim_id"] = \
                        NFVO_DEFAULT_DOCKER_DATACENTER
        instantiation_data["om-datacenter"] = instantiation_data["vim_id"]
        if "vim_net" not in instantiation_data:
            instantiation_data["vim_net"] = \
                NFVO_DEFAULT_KVM_DATACENTER_NET
            if "virt_type" in instantiation_data:
                if instantiation_data["virt_type"] == "docker":
                    instantiation_data["vim_net"] = \
                        NFVO_DEFAULT_DOCKER_DATACENTER_NET
        instantiation_data["vim-network-name"] = instantiation_data["vim_net"]
        nsr_data = self.build_nsr_data(instantiation_data)
        resp = requests.post(
            endpoints.NS_INSTANTIATE,
            headers=endpoints.get_default_headers(),
            verify=False,
            json=nsr_data)
        print("BODY")
        print(nsr_data)
        print("BODY END")
        if resp.status_code in(200, 201, 202):
            success_msg = {"instance_name": nsr_data["nsr"][0]["name"],
                           "instance_id": nsr_data["nsr"][0]["id"],
                           "ns_name": nsr_data["nsr"][0]["nsd"]["id"],
                           "vim_id": nsr_data["nsr"][0]["om-datacenter"],
                           "result": "success"}
            self.apply_mspl_action(nsr_data["nsr"][0]["id"],
                                   instantiation_data)
            return success_msg
        else:
            error_msg = {"result": "error",
                         "error_response": resp}
            return error_msg

    def delete_ns_instance(self, instance_id):
        url = "{0}/{1}".format(endpoints.NS_RUNNING, instance_id)
        headers = endpoints.get_default_headers()
        resp = requests.delete(url,
                               headers=headers,
                               verify=False)
        if resp.status_code in(200, 201, 202):
            success_msg = {"instance_id": instance_id,
                           "action": "delete",
                           "result": "success"}
            return success_msg
        else:
            error_msg = {"result": "error",
                         "error_response": resp}
            return error_msg

    def get_ns_instances(self, instance_id=None):
        resp = requests.get(
                endpoints.NS_OPERATIONAL,
                headers=endpoints.get_default_headers(),
                verify=False)
        if resp.status_code == 204:
            return {"ns": []}
        if instance_id is None:
            return {
                "ns": [x for x in
                       self.format_nsr_running_data(json.loads(resp.text))]
            }
        if regex.uuid4(instance_id) is not None:
            return {
                "ns": [x for x in
                       self.format_nsr_running_data(json.loads(resp.text))
                       if x.get("instance_id", "") == instance_id]
            }
        else:
            return {
                "ns": [x for x in
                       self.format_nsr_running_data(json.loads(resp.text))
                       if x.get("instance_name", "") == instance_id]
            }

    def format_vnsf_catalog_records(self, catalog):
        output = {"vnsf": list()}
        vnsfs = output.get("vnsf")
        vim_list = self.vnfo_vim.get_vim_list()
        if len(catalog.keys()) == 0:
            return output
        for vnf in catalog["collection"]["vnfr:vnfr"]:
            # Parse content of vnf-data first
            vnf_name = vnf.get("name")
            ns_name = vnf_name.split("__")
            if len(ns_name) >= 1:
                ns_name = ns_name[0]
            else:
                ns_name = vnf_name
            vim_name = self.vnfo_vim.get_vim_name_by_uuid(
                vim_list, vnf.get("om-datacenter"))
            ip_address = ""
            if "connection-point" in vnf.keys()\
                    and len(vnf.get("connection-point")) > 0\
                    and "ip-address" in vnf.get("connection-point")[0].keys():
                ip_address = vnf.get("connection-point")[0].get("ip-address")
            vnsf_dict = {
                "config_status": vnf.get("config-status"),
                "ip": ip_address,
                "ns_id": vnf.get("nsr-id-ref"),
                "ns_name": ns_name,
                "operational_status": vnf.get("operational-status"),
                "vendor": vnf.get("vendor"),
                "vnfr_id": vnf.get("id"),
                "vnfd_id": vnf.get("vnfd").get("id"),
                "vnfr_name": vnf_name,
                "vim": vim_name,
            }
            vnsfs.append(vnsf_dict)
        return output

    def get_vnf_instances(self):
        catalog = self.__get_vnfr_running()
        return self.format_vnsf_catalog_records(catalog)

    def __get_vnfr_running(self):
        resp = requests.get(
                endpoints.VNF_CATALOG_O,
                headers=endpoints.get_default_headers(),
                verify=False)
        return json.loads(resp.text) if resp.text else {}

    def format_nsr_running_data(self, data):
        nsrs = data["collection"]["nsr:nsr"]
        config_agent_job_map = self.build_config_agent_job_map(nsrs)
        return [{
            "config_status": x["config-status"],
            "operational_status": x["operational-status"],
            "instance_name": x["name-ref"],
            "ns_name": x["nsd-name-ref"],
            "instance_id": x["ns-instance-config-ref"],
            "nsd_id": x["nsd-ref"],
            "constituent_vnf_instances":
            [self.join_vnfr_with_config_jobs(y, config_agent_job_map)
                for y in self.get_vnf_instances().get("vnsf", "")
                if y.get("vnfr_id", "")
                in [z.get("vnfr-id", "")
                    for z in x.get("constituent-vnfr-ref", "")]],
            "vlrs": [
                {"vlr_id": y["vlr-ref"],
                 "vim_id": y["om-datacenter"]} for y in
                x.get("vlr", [])]
        } for x in nsrs if "config-status" in x]

    def format_ns_catalog_descriptors(self, catalog):
        output = {"ns": list()}
        nss = output.get("ns")
        for n in catalog:
            for nd in n["descriptors"]:
                constituent_vnfs = nd.get("constituent-vnfd", None)
                if constituent_vnfs is not None:
                    nss.append({
                        "constituent_vnfs": constituent_vnfs,
                        "description": nd.get("description"),
                        "ns_name": nd.get("name"),
                        "vendor": nd.get("vendor"),
                        "version": nd.get("version"),
                        "vld": nd.get("vld")
                    })
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

    def build_config_agent_job_map(self, data):
        config_map = {}
        for nsr in data:
            if "config-agent-job" in nsr:
                for config_job in nsr["config-agent-job"]:
                    if "vnfr" in config_job:
                        for vnfr_job in config_job["vnfr"]:
                            data_record = {
                                "triggered_by":
                                config_job["triggered-by"],
                                "create_time":
                                config_job["create-time"],
                                "job_status":
                                config_job["job-status"],
                                "job_id":
                                config_job["job-id"],
                                "primitives":
                                [{
                                    "execution_status":
                                    x["execution-status"],
                                    "name":
                                    x["name"],
                                    "execution_id":
                                    x["execution-id"]
                                } for x in vnfr_job["primitive"]]}
                            if vnfr_job["id"] in config_map:
                                config_map[vnfr_job["id"]].append(data_record)
                            else:
                                config_map[vnfr_job["id"]] = [data_record]
        return config_map

    def join_vnfr_with_config_jobs(self, vnfr, config_map):
        if vnfr["vnfr_id"] in config_map:
            vnfr["config_jobs"] = config_map[vnfr["vnfr_id"]]
        else:
            vnfr["config_jobs"] = []
        return vnfr

    def __fetch_indexes(self, catalog, vnfr_id, primitive):
        nsr_id = None
        vnf_idx = None
        vnf_prim_idx = None
        for vnf in catalog["collection"]["vnfr:vnfr"]:
            if vnfr_id == vnf["id"]:
                nsr_id = vnf["nsr-id-ref"]
                vnf_idx = vnf["member-vnf-index-ref"]
                prims = vnf["vnf-configuration"]["service-primitive"]
                for pos, prim in enumerate(prims):
                    if prim["name"] == primitive:
                        vnf_prim_idx = pos
                        break
        return [nsr_id, vnf_idx, vnf_prim_idx]

    def exec_action_on_vnf(self, payload):
        # JSON
        # resp = requests.post(
        #        endpoints.VNF_ACTION_EXEC,
        #        headers=endpoints.post_default_headers(),
        #        data=json.dumps(payload),
        #        verify=False)

        # Encoded
        # payload = payload.replace('\\"', '"').strip()
        resp = requests.post(
                endpoints.VNF_ACTION_L_EXEC,
                headers=endpoints.post_encoded_headers(),
                data=payload,
                verify=False)

        # output = json.loads(resp.text)
        output = resp.text
        return output

    def fill_vnf_action_request(self, vnfr_id=None,
                                primitive=None, params=None):
        exec_tmpl = json.loads(nfvo_tmpl.exec_action)
        exec_tmpl_vnf = json.loads(nfvo_tmpl.exec_action_vnf)
        if vnfr_id:
            exec_tmpl_vnf["vnfr-id-ref"] = vnfr_id
        if primitive:
            exec_tmpl_vnf["vnf-primitive"][0]["name"] = primitive
    #    if description:
    #        exec_tmpl_vnf["name"] = description
        if params:
            exec_tmpl_vnf["vnf-primitive"][0]["parameter"] = []
            for key, val in params.items():
                d = {"name": key, "value": val}
                exec_tmpl_vnf["vnf-primitive"][0]["parameter"].append(d)
        exec_tmpl["input"]["vnf-list"] = [exec_tmpl_vnf]
        catalog = self.orchestrator.__get_vnfr_running()
        nsr_id, vnf_idx, vnf_prim_idx = self.__fetch_indexes(
            catalog, vnfr_id, primitive)
        exec_tmpl["input"]["nsr_id_ref"] = nsr_id
        exec_tmpl["input"]["vnf-list"][0]["member_vnf_index_ref"] = vnf_idx
        exec_tmpl["input"]["vnf-list"][0]["vnf-primitive"][0]["index"] = \
            vnf_prim_idx
        return exec_tmpl

    def format_vnsf_catalog_descriptors(self, catalog):
        output = {"vnsf": list()}
        vnsfs = output.get("vnsf")
        for n in catalog:
            for nd in n["descriptors"]:
                if "constituent-vnfd" not in nd.keys():
                    charm = {}
                    if "vnf-configuration" in nd:
                        charm = nd.get("vnf-configuration")\
                                   .get("juju").get("charm")
                    vnsfs.append({
                        "charm": charm,
                        "description": nd.get("description"),
                        "ns_name": nd.get("name"),
                        "vendor": nd.get("vendor"),
                        "version": nd.get("version"),
                    })
        return output

    def build_nsr_data(self, instantiation_data):
        nsr_id = str(uuid.uuid4())
        # Need to retrieve vnfds of the nsd
        configuration = self.get_ns_descriptors(instantiation_data["ns_name"])
        if len(configuration) == 0 or configuration is None:
            # In case payload is None rift.io will throw a 404
            return None
        # Filtering by start-by-default (field seems to be there for this)
        vnfss = [{"vnfd-id-ref": x["vnfd-id-ref"],
                  "member-vnf-index": x["member-vnf-index"]} for
                 x in configuration[0]["constituent_vnfs"]
                 if x["start-by-default"] == "true"]
        if "vim_net" in instantiation_data:
            # In case it is already specified inside request
            # apply vim_net on mgmt
            vlds = [{"id": x["id"],
                     "mgmt-network": x["mgmt-network"],
                     "name": x["name"],
                     "type": x["type"],
                     "vnfd-connection-point-ref":
                     x["vnfd-connection-point-ref"],
                     "vim-network-name": instantiation_data["vim_net"]}
                    for x in configuration[0]["vld"]
                    if x.get("mgmt-network", "") == "true"]
            # Add vld information, wether explicit or not
            non_managed_vlds = [{"id": x["id"],
                                 "mgmt-network": "false",
                                 "vnfd-connection-point-ref":
                                 x["vnfd-connection-point-ref"],
                                 "name": x["name"]}
                                for x in configuration[0]["vld"]
                                if x.get("mgmt-network", "") == "false"]
            vlds = vlds + non_managed_vlds
            print("----------------------------------------------------")
            print(configuration[0]["vld"])
            print("----------------------------------------------------")
            print(vlds)
            print("----------------------------------------------------")
        else:
            # By default, include virtual links configuration only if
            # specific vim-network-name is defined
            vlds = [{"id": x["id"],
                     "mgmt-network": x["mgmt-network"],
                     "name": x["name"],
                     "type": x["type"],
                     "vim-network-name": x["vim-network-name"]}
                    for x in configuration[0]["vld"]
                    if "vim-network-name" in x]
            # Add vld information, whether explicit or not
            non_managed_vlds = [{"id": x["id"],
                                 "mgmt-network": "false",
                                 "name": x["name"]}
                                for x in configuration[0]["vld"]
                                if "vim-network-name" not in x]
            vlds = vlds + non_managed_vlds
        return nfvo_tmpl.instantiation_data_msg(
                nsr_id, instantiation_data, vnfss, vlds)

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
            nss = self.get_ns_instances(instance_id)
            if timeout < 0:
                print("Timeout reached, aborting thread")
                break
            if len(nss["ns"]) < 1:
                print("No instance found, aborting thread")
                break
            operational_status = nss["ns"][0].get("operational_status", "")
            if operational_status == "failed":
                print("Instance failed, aborting")
                break
            if operational_status == target_status and \
               "constituent_vnf_instances" in nss["ns"][0]:
                # Perform action on all vnf instances?
                for vnsf_instance in nss["ns"][0]["constituent_vnf_instances"]:
                    exec_tmpl = self.fill_vnf_action_request_encoded(
                        vnsf_instance["vnfr_id"], action, params)
                    output = self.exec_action_on_vnf(exec_tmpl)
                    if action is not None:
                        app.mongo.store_vnf_action(vnsf_instance["vnfr_id"],
                                                   action,
                                                   params,
                                                   json.loads(output))
                        print("Action performed and stored, exiting thread")
                    action_submitted = True
            else:
                print("Operational status: {0}, waiting ...".
                      format(operational_status))
        return

    def fill_vnf_action_request_encoded(self, vnfr_id=None,
                                        primitive=None, params=None):
        exec_tmpl = nfvo_tmpl.exec_action_encoded.strip()
        exec_tmpl_vnf = ""
        catalog = self.__get_vnfr_running()
        nsr_id, vnf_idx, vnf_prim_idx = self.__fetch_indexes(
            catalog, vnfr_id, primitive)

        i = 0
        for key, val in params.items():
            exec_tmpl_param = nfvo_tmpl.exec_action_vnf_encoded.strip()
            val = val.replace("\"", '\\"')
            exec_tmpl_vnf += exec_tmpl_param.format(
                    idx=i,
                    param_name=key,
                    param_value=val)
            i += 1

        # Data from the vNSF to be replaced in the template of the action
        values = {
                "name": "",
                "action_data": "{action_data}",
                "ns_id": nsr_id,
                "vnf_id": vnfr_id,
                "vnf_index": vnf_idx,
                "action_name": primitive,
                "action_idx": vnf_prim_idx
                }

        exec_tmpl = exec_tmpl.format(**values)
        exec_tmpl = exec_tmpl.format(action_data=exec_tmpl_vnf)
        return exec_tmpl

    def get_vnf_descriptors(self):
        catalog = self.__get_vnfr_config()
        print(catalog)
        return self.format_vnsf_catalog_descriptors(catalog)

    def __get_vnfr_config(self):
        resp = requests.get(
                endpoints.VNF_CATALOG_C,
                headers=endpoints.get_default_headers(),
                verify=False)
        # Yep, this could be insecure - but the output comes from NFVO
        return eval(resp.text) if resp.text else []

    def post_content(self, bin_file, release=None):
        data_file = ImmutableMultiDict([("package", bin_file)])
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        resp = requests.post(
            endpoints.PKG_ONBOARD,
            headers=endpoints.get_default_headers(),
            files=data_file,
            verify=False)
        output = json.loads(resp.text)
        output.update({"package": bin_file.filename})
        return output

    def onboard_package(self, pkg_path, release=None):
        remove_after = False
        fp = None
        bin_file = None
        output = None
        if type(pkg_path) == FileStorage:
            bin_file = pkg_path
        else:
            if not os.path.isfile(pkg_path):
                remove_after = True
            if os.path.isfile(pkg_path):
                fp = open(pkg_path, "rb")
                filename = os.path.basename(pkg_path)
                mime = MimeTypes()
                content_type = mime.guess_type(pkg_path)
                bin_file = FileStorage(fp, filename, "package", content_type)
        if bin_file is not None:
            output = self.post_content(bin_file)
        if fp is not None:
            fp.close()
        if remove_after:
            pkg_dir = os.path.dirname(pkg_path)
            shutil.rmtree(pkg_dir)
        return output


if __name__ == "__main__":
    OSM = OSMR2()
    print(OSM.get_ns_descriptors())
    print(OSM.get_ns_instances())
    # NSD_IDS = [x["_id"] for x in OSM.get_ns_descriptors()]
    # print(random.choice(NSD_IDS))
    # NSR = OSM.post_ns_instance("833bb02c-92e4-4fdb-ac55-cc927acfd2e7",
    #                            "Test",
    #                            "Test instance")
    # print(OSM.get_ns_instance(NSR["id"]))
    # time.sleep(180)
    # OSM.delete_ns_instance(NSR["id"])
