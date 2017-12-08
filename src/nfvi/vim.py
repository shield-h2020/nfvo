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
from server import content
from server.mocks.vim import MockVim as vim_m

import json
import requests


def get_vim_name_by_uuid(vim_list, uuid):
    for dc in vim_list:
        if dc.get("uuid") == uuid:
            return dc.get("name")
    return ""


@content.on_mock(vim_m().get_vim_list_mock)
def get_vim_list():
    resp = requests.get(
            osm_eps.VIM_DC,
            headers=osm_eps.get_default_headers(),
            verify=False)
    output = json.loads(resp.text)
    output = output.get("collection") \
                   .get("rw-launchpad:datacenters")[0] \
                   .get("ro-accounts")[0] \
                   .get("datacenters")
    return output


@content.on_mock(vim_m().get_vim_img_list_mock)
def get_vim_img_list():
    tenant_list = get_vim_tenant_list()
    output = {}
    for tenant in tenant_list["tenants"]:
        tenant_uuid = tenant.get("uuid")
        tenant_name = get_vim_name_by_uuid(tenant_list["tenants"], tenant_uuid)
        output[tenant_name] = {}
        dc_list = get_vim_list()
        for datacenter in dc_list:
            dc_uuid = datacenter.get("uuid")
            dc_name = get_vim_name_by_uuid(dc_list, dc_uuid)
            vim_img_list_ep = osm_eps.VIM_IMG.format(tenant_uuid, dc_uuid)
            resp = requests.get(
                    vim_img_list_ep,
                    verify=False)
            imgs = json.loads(resp.text)
            imgs = filter(lambda x: x.get("visibility") == "public",
                          imgs.get("images"))
            output[tenant_name][dc_name] = imgs
    return output


def get_vim_tenant_list():
    resp = requests.get(
            osm_eps.VIM_TENANT,
            verify=False)
    output = json.loads(resp.text)
    return output


@content.on_mock(vim_m().register_vdu_mock)
def register_vdu(dc_uuid, vdu_name, vdu_img):
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
