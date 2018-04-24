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


from flask import current_app
from nfvi.vim import VnsfoVim as vim_s
from nfvo.osm import endpoints as osm_eps
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.vnf import MockVnsf as vnfs_m
from templates import nfvo as nfvo_tmpl

import json
import requests


class VnsfoVnsf:

    def __init__(self):
        self.res_key = "vnsf"
        self.vnfo_vim = vim_s()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def __get_vnfr_config(self):
        resp = requests.get(
                osm_eps.VNF_CATALOG_C,
                headers=osm_eps.get_default_headers(),
                verify=False)
        # Yep, this could be insecure - but the output comes from NFVO
        return eval(resp.text) if resp.text else []

    @content.on_mock(vnfs_m().get_vnfr_config_mock)
    def get_vnfr_config(self):
        catalog = self.__get_vnfr_config()
        return self.format_vnsf_catalog_descriptors(catalog)

    def __get_vnfr_running(self):
        resp = requests.get(
                osm_eps.VNF_CATALOG_O,
                headers=osm_eps.get_default_headers(),
                verify=False)
        return json.loads(resp.text) if resp.text else {}

    @content.on_mock(vnfs_m().get_vnfr_running_mock)
    def get_vnfr_running(self):
        catalog = self.__get_vnfr_running()
        return self.format_vnsf_catalog_records(catalog)

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
        catalog = self.__get_vnfr_running()
        nsr_id, vnf_idx, vnf_prim_idx = self.__fetch_indexes(
            catalog, vnfr_id, primitive)
        exec_tmpl["input"]["nsr_id_ref"] = nsr_id
        exec_tmpl["input"]["vnf-list"][0]["member_vnf_index_ref"] = vnf_idx
        exec_tmpl["input"]["vnf-list"][0]["vnf-primitive"][0]["index"] = \
            vnf_prim_idx
        return exec_tmpl

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

    def format_vnsf_catalog_descriptors(self, catalog):
        output = {self.res_key: list()}
        vnsfs = output.get(self.res_key)
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

    def format_vnsf_catalog_records(self, catalog):
        output = {self.res_key: list()}
        vnsfs = output.get(self.res_key)
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
                "vnf_id": vnf.get("id"),
                "vnf_name": vnf_name,
                "vim": vim_name,
            }
            vnsfs.append(vnsf_dict)
        return output

    @content.on_mock(vnfs_m().exec_action_on_vnf_mock)
    def exec_action_on_vnf(self, payload):
        # JSON
        # resp = requests.post(
        #        osm_eps.VNF_ACTION_EXEC,
        #        headers=osm_eps.post_default_headers(),
        #        data=json.dumps(payload),
        #        verify=False)

        # Encoded
        # payload = payload.replace('\\"', '"').strip()
        resp = requests.post(
                osm_eps.VNF_ACTION_L_EXEC,
                headers=osm_eps.post_encoded_headers(),
                data=payload,
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
