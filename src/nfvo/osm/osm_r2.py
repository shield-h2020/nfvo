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
from nfvo.osm import endpoints
from nfvo.osm import \
    NFVO_DEFAULT_KVM_DATACENTER, NFVO_DEFAULT_KVM_DATACENTER_NET
from nfvo.osm import \
    NFVO_DEFAULT_DOCKER_DATACENTER, NFVO_DEFAULT_DOCKER_DATACENTER_NET
from nfv.vnf import VnsfoVnsf
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from templates import nfvo as nfvo_tmpl

import json
import requests
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
        self.res_key = "ns"
        self.config = FullConfParser()
        self.nfvo_mspl_category = self.config.get("nfvo.mspl.conf")
        self.mspl_monitoring = self.nfvo_mspl_category.get("monitoring")
        self.monitoring_timeout = int(self.mspl_monitoring.get("timeout"))
        self.monitoring_interval = int(self.mspl_monitoring.get("interval"))
        self.monitoring_target_status = self.\
            mspl_monitoring.get("target_status")
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
        pass

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

    def format_nsr_running_data(self, data):
        nsrs = data["collection"]["nsr:nsr"]
        config_agent_job_map = self.build_config_agent_job_map(nsrs)
        vnsf = VnsfoVnsf()
        return [{
            "config_status": x["config-status"],
            "operational_status": x["operational-status"],
            "instance_name": x["name-ref"],
            "ns_name": x["nsd-name-ref"],
            "instance_id": x["ns-instance-config-ref"],
            "nsd_id": x["nsd-ref"],
            "constituent_vnf_instances":
            [self.join_vnfr_with_config_jobs(y, config_agent_job_map)
                for y in vnsf.get_vnfr_running().get("vnsf", "")
                if y.get("vnfr_id", "")
                in [z.get("vnfr-id", "")
                    for z in x.get("constituent-vnfr-ref", "")]],
            "vlrs": [
                {"vlr_id": y["vlr-ref"],
                 "vim_id": y["om-datacenter"]} for y in
                x.get("vlr", [])]
        } for x in nsrs if "config-status" in x]

    def format_ns_catalog_descriptors(self, catalog):
        output = {self.res_key: list()}
        nss = output.get(self.res_key)
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
                    vnsf = VnsfoVnsf()
                    exec_tmpl = vnsf.fill_vnf_action_request_encoded(
                        vnsf_instance["vnfr_id"], action, params)
                    output = vnsf.exec_action_on_vnf(exec_tmpl)
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
