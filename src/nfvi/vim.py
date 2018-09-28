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


from nfvi.openstack.connector import OpenStackConnector
from nfvi.openstack.glance import OpenStackGlance
from nfvo.osm import endpoints as osm_eps
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.vim import MockVim as vim_m

import json
import requests


class VnsfoVim:

    def __init__(self):
        self.res_key = "vim"
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get_vim_name_by_uuid(self, vim_list, uuid):
        if isinstance(vim_list, dict):
            vim_list = vim_list.get(self.res_key)
        for dc in vim_list:
            if dc.get("uuid") == uuid:
                return dc.get("name")
        return ""

    def __get_vim_list(self):
        resp = requests.get(
                osm_eps.VIM_DC,
                headers=osm_eps.get_default_headers(),
                verify=False)
        return json.loads(resp.text)

    @content.on_mock(vim_m().get_vim_list_mock)
    def get_vim_list(self):
        output = self.__get_vim_list()
        output = output.get("collection") \
                       .get("rw-launchpad:datacenters")[0] \
                       .get("ro-accounts")[0] \
                       .get("datacenters")
        return self.format_vim_list(output)

    @content.on_mock(vim_m().get_vim_img_list_mock)
    def get_vim_img_list(self):
        tenant_list = self.__get_vim_tenant_list()
        return self.format_vim_img_list(tenant_list)

    def __get_vim_tenant_list(self):
        resp = requests.get(
                osm_eps.VIM_TENANT,
                verify=False)
        output = json.loads(resp.text)
        return output

    @content.on_mock(vim_m().register_vdu_mock)
    def register_vdu(self, dc_uuid, vdu_name, vdu_img):
        os_details = {"osm":
                      {"datacenter": dc_uuid}}
        os_conn = OpenStackConnector(**os_details)
        glance_client = OpenStackGlance(os_conn)
        status, glance_image = glance_client.upload_image(vdu_name, vdu_img)
        status = "{}registered".format(
                "" if status == "success" else "not ")
        glance_image_d = {}
        if glance_image is not None:
            glance_image_d = {
                    "name": glance_image.name, "uuid": glance_image.id,
                    "checksum": glance_image.checksum,
                    "container_format": glance_image.container_format,
                    "disk_format": glance_image.disk_format}
        output = {"status": status, "image": glance_image_d}
        return output

    def format_vim_list(self, vim_list):
        return {self.res_key: vim_list}

    def format_vim_img_list(self, tenant_list):
        output = {self.res_key: list()}
        img_vims = output.get(self.res_key)
        # img_vims.append({})
        img_vims_cfg = {}
        for tenant in tenant_list["tenants"]:
            tenant_uuid = tenant.get("uuid")
            tenant_name = self.get_vim_name_by_uuid(
                tenant_list["tenants"], tenant_uuid)
            img_vims_cfg[tenant_name] = {}
            dc_list = self.get_vim_list().get(self.res_key)
            for datacenter in dc_list:
                dc_uuid = datacenter.get("uuid")
                dc_name = self.get_vim_name_by_uuid(dc_list, dc_uuid)
                vim_img_list_ep = osm_eps.VIM_IMG.format(tenant_uuid, dc_uuid)
                resp = requests.get(
                        vim_img_list_ep,
                        verify=False)
                imgs = json.loads(resp.text)
                imgs = [x for x in
                        filter(lambda x: x.get("visibility") == "public",
                               imgs.get("images", []))]
                img_vims_cfg[tenant_name][dc_name] = imgs
            img_vims.append(img_vims_cfg)
        return output
