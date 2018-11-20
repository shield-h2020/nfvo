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
from flask import current_app
from nfv.vnf import VnsfoVnsf
from nfvo.osm import endpoints as osm_eps
from nfvo.osm import \
    NFVO_DEFAULT_KVM_DATACENTER, NFVO_DEFAULT_KVM_DATACENTER_NET
from nfvo.osm import \
    NFVO_DEFAULT_DOCKER_DATACENTER, NFVO_DEFAULT_DOCKER_DATACENTER_NET
from nfvo.osm.osm_r2 import OSMR2
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.ns import MockNs as ns_m
from templates import nfvo as nfvo_tmpl

import json
import requests
import threading
import time
import uuid


class VnsfoNs:

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
        self.orchestrator = OSMR2()

    @content.on_mock(ns_m().get_nsr_config_mock)
    def get_nsr_config(self, ns_name=None):
        return self.orchestrator.get_ns_descriptors(ns_name)

    @content.on_mock(ns_m().get_nsr_running_mock)
    def get_nsr_running(self, instance_id=None):
        return self.orchestrator.get_ns_instances(instance_id)

    def build_nsr_data(self, instantiation_data):
        nsr_id = str(uuid.uuid4())
        # Need to retrieve vnfds of the nsd
        configuration = self.get_nsr_config(instantiation_data["ns_name"])
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
            nss = self.get_nsr_running(instance_id)
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

    @content.on_mock(ns_m().post_nsr_instantiate_mock)
    def instantiate_ns(self, instantiation_data):
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
            osm_eps.NS_INSTANTIATE,
            headers=osm_eps.get_default_headers(),
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

    @content.on_mock(ns_m().delete_nsr_mock)
    def delete_ns(self, instance_id):
        url = "{0}/{1}".format(osm_eps.NS_RUNNING, instance_id)
        headers = osm_eps.get_default_headers()
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

    def fetch_config_nss(self):
        catalog = self.get_nsr_config()
        return catalog
