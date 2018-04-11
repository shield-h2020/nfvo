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


import uuid
from nfvo.osm import endpoints as osm_eps
from nfvo.osm import NFVO_DEFAULT_OM_DATACENTER
from templates import nfvo as nfvo_tmpl
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.ns import MockNs as ns_m

import json
import requests


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
        # Yep, this could be insecure - but the output comes from NFVO
        catalog = eval(resp.text) if resp.text else []
        if ns_name is None:
            # returning all ns_catalog_descriptors
            return self.format_ns_catalog_descriptors(catalog)
        else:
            # filtering by name
            fcatalog = self.format_ns_catalog_descriptors(catalog)
            return [x for x in fcatalog["ns"] if x["ns_name"] == ns_name]

    def get_nsr_running(self):
        resp = requests.get(
                osm_eps.NS_CATALOG_O,
                headers=osm_eps.get_default_headers(),
                verify=False)
        output = json.loads(resp.text)
        return output

    def build_nsr_data(self, instantiation_data):
        nsr_id = str(uuid.uuid4())
        # need to retrieve vnfds of the nsd
        configuration = self.get_nsr_config(instantiation_data["ns_id"])
        if len(configuration) == 0 or configuration is None:
            # in case payload is None rift.io will throw a 404
            return None
        # filtering by start-by-default (field seems to be there for this)
        vnfss = [{"vnfd-id-ref": x["vnfd-id-ref"],
                  "member-vnf-index": x["member-vnf-index"]} for
                 x in configuration[0]["constituent_vnfs"]
                 if x["start-by-default"] == "true"]
        return nfvo_tmpl.instantiation_data_msg(
                nsr_id, instantiation_data, vnfss)

    def instantiate_ns(self, instantiation_data):
        if "om-datacenter" not in instantiation_data:
            instantiation_data["om-datacenter"] = NFVO_DEFAULT_OM_DATACENTER
        nsr_data = self.build_nsr_data(instantiation_data)
        resp = requests.post(
            osm_eps.NS_INSTANTIATE,
            headers=osm_eps.get_default_headers(),
            verify=False,
            json=nsr_data)
        return resp

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
                    })
        return output
