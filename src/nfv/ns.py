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


from core import regex
from nfv.vnf import VnsfoVnsf
from nfvo.osm import endpoints as osm_eps
from nfvo.osm import NFVO_DEFAULT_OM_DATACENTER, NFVO_DEFAULT_OM_DATACENTER_NET
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.ns import MockNs as ns_m
from templates import nfvo as nfvo_tmpl

import json
import requests
import uuid


class VnsfoNs:

    def __init__(self):
        self.res_key = "ns"
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    @content.on_mock(ns_m().get_nsr_config_mock)
    def get_nsr_config(self, ns_name=None):
        resp = requests.get(
                osm_eps.NS_CATALOG_C,
                headers=osm_eps.get_default_headers(),
                verify=False)
        # yep, this could be insecure - but the output comes from NFVO
        catalog = eval(resp.text) if resp.text else []
        if ns_name is None:
            # returning all ns_catalog_descriptors
            return self.format_ns_catalog_descriptors(catalog)
        else:
            # filtering by name
            fcatalog = self.format_ns_catalog_descriptors(catalog)
            return [x for x in fcatalog["ns"] if x["ns_name"] == ns_name]

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
        if vnfr["vnf_id"] in config_map:
            vnfr["config_jobs"] = config_map[vnfr["vnf_id"]]
        else:
            vnfr["config_jobs"] = []
        return vnfr

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
            "constituent_vnf_instances":
            [self.join_vnfr_with_config_jobs(y, config_agent_job_map)
                for y in vnsf.get_vnfr_running().get("vnsf", "")
                if y.get("vnf_id", "")
                in [z.get("vnfr-id", "")
                    for z in x.get("constituent-vnfr-ref", "")]],
            "vlrs": [
                {"vlr_id": y["vlr-ref"],
                 "vim_id": y["om-datacenter"]} for y in
                x.get("vlr", [])]
        } for x in nsrs]

    @content.on_mock(ns_m().get_nsr_running_mock)
    def get_nsr_running(self, instance_id=None):
        resp = requests.get(
                osm_eps.NS_RUNNING,
                headers=osm_eps.get_default_headers(),
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

    def build_nsr_data(self, instantiation_data):
        nsr_id = str(uuid.uuid4())
        # need to retrieve vnfds of the nsd
        configuration = self.get_nsr_config(instantiation_data["ns_name"])
        if len(configuration) == 0 or configuration is None:
            # in case payload is None rift.io will throw a 404
            return None
        # filtering by start-by-default (field seems to be there for this)
        vnfss = [{"vnfd-id-ref": x["vnfd-id-ref"],
                  "member-vnf-index": x["member-vnf-index"]} for
                 x in configuration[0]["constituent_vnfs"]
                 if x["start-by-default"] == "true"]
        if "vim_net" in instantiation_data:
            # In case it's already specified inside request
            # apply vim_net on mgmt
            vlds = [{"id": x["id"],
                     "mgmt-network": x["mgmt-network"],
                     "name": x["name"],
                     "type": x["type"],
                     "vim-network-name": instantiation_data["vim_net"]}
                    for x in configuration[0]["vld"]
                    if x.get("mgmt-network", "") == "true"]
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
        return nfvo_tmpl.instantiation_data_msg(
                nsr_id, instantiation_data, vnfss, vlds)

    @content.on_mock(ns_m().post_nsr_instantiate_mock)
    def instantiate_ns(self, instantiation_data):
        if "vim_id" not in instantiation_data:
            instantiation_data["vim_id"] = NFVO_DEFAULT_OM_DATACENTER
        instantiation_data["om-datacenter"] = instantiation_data["vim_id"]
        if "vim_net" not in instantiation_data:
            instantiation_data["vim_net"] = NFVO_DEFAULT_OM_DATACENTER_NET
        instantiation_data["vim-network-name"] = instantiation_data["vim_net"]
        nsr_data = self.build_nsr_data(instantiation_data)
        resp = requests.post(
            osm_eps.NS_INSTANTIATE,
            headers=osm_eps.get_default_headers(),
            verify=False,
            json=nsr_data)
        if resp.status_code in(200, 201, 202):
            success_msg = {"instance_name": nsr_data["nsr"][0]["name"],
                           "instance_id": nsr_data["nsr"][0]["id"],
                           "ns_name": nsr_data["nsr"][0]["nsd"]["id"],
                           "vim_id": nsr_data["nsr"][0]["om-datacenter"],
                           "result": "success"}
            return success_msg
        else:
            error_msg = {"result": "error",
                         "error_response": resp}
            return error_msg

    def fetch_config_nss(self):
        catalog = self.get_nsr_config()
        return catalog

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
