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
from nfvo.osm import endpoints
from nfv.vnf import VnsfoVnsf
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import json
import requests
import urllib3
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

    def post_ns_instance(self, nsd_id, name, description,
                         vim_account_id=None, flavor=None):
        pass

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
