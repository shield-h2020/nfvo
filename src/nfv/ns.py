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


from nfv import vnf
from nfvo.osm import endpoints as osm_eps

import json
import requests


def get_nsr_config():
    resp = requests.get(
            osm_eps.NS_CATALOG_C,
            headers=osm_eps.get_default_headers(),
            verify=False)
    # Yep, this could be insecure - but the output comes from NFVO
    catalog = eval(resp.text) if resp.text else []
    output = list()
    for n in catalog:
        for nd in n["descriptors"]:
            constituent_vnfs = nd.get("constituent-vnfd", None)
            if constituent_vnfs is not None:
                output.append({
                    "constituent_vnfs": constituent_vnfs,
                    "description": nd.get("description"),
                    "ns_name": nd.get("name"),
                    "vendor": nd.get("vendor"),
                    "version": nd.get("version"),
                })
    return output


def get_nsr_running():
    resp = requests.get(
            osm_eps.NS_CATALOG_O,
            headers=osm_eps.get_default_headers(),
            verify=False)
    output = json.loads(resp.text)
    return output


def fetch_config_nss():
    catalog = get_nsr_config()
    # return format_ns_catalog(catalog)
    return catalog


def fetch_running_vnsfs():
    catalog = vnf.get_vnfr_running()
    return vnf.format_vnsf_catalog(catalog)


def format_ns_catalog(catalog):
    nss = []
    for ns in catalog["collection"]["nsd:nsd"]:
        ns_dict = {
            "config_status": ns.get("config-status"),
            "ns_id": ns.get("id", None),
            "name": ns.get("name"),
            "vendor": ns.get("vendor")}
        nss.append(ns_dict)
    return nss
