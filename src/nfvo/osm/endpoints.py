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


from nfvo.osm import NFVO_ENDPOINT
from nfvo.osm import NFVO_PKG_ENDPOINT
from nfvo.osm import NFVO_PKG_PORT
from nfvo.osm import NFVO_PORT
from nfvo.osm import NFVO_RO_ENDPOINT
from nfvo.osm import NFVO_RO_PORT


BASE = "http://{}:{}/{}"
S_BASE = BASE.replace("http:", "https:")

# Package
PKG_NS_REMOVE_EP = "composer/api/catalog/nsd/{}?api_server=https://localhost"
PKG_NS_REMOVE = S_BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT,
                              PKG_NS_REMOVE_EP)

PKG_ONBOARD_EP = "composer/upload?api_server=https://localhost"
PKG_ONBOARD = S_BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, PKG_ONBOARD_EP)

# PKG_VNF_REMOVE_EP = "/api/config/vnfd-catalog/vnfd/{}"
PKG_VNF_REMOVE_EP = "composer/api/catalog/vnfd/{}?api_server=https://localhost"
PKG_VNF_REMOVE = S_BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT,
                               PKG_VNF_REMOVE_EP)

# Network service
# NS_CATALOG_C_EP = "api/config/nsd-catalog/nsd"
# NS_CATALOG_C = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT, NS_CATALOG_C_EP)
NS_CATALOG_C_EP = "composer/api/catalog?api_server=https://localhost"
NS_CATALOG_C = S_BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, NS_CATALOG_C_EP)

NS_CATALOG_O_EP = "api/operational/nsd-catalog/nsd"
NS_CATALOG_O = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT, NS_CATALOG_O_EP)

NS_INSTANTIATE_EP = "api/operational/ns-instance-config/nsr"
NS_INSTANTIATE = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT, NS_INSTANTIATE_EP)

# Infrastructure
VIM_DC_EP = "api/operational/datacenters"
VIM_DC = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT, VIM_DC_EP)
VIM_IMG_EP = "openmano/{}/vim/{}/images"
VIM_IMG = BASE.format(NFVO_RO_ENDPOINT, NFVO_RO_PORT, VIM_IMG_EP)
VIM_TENANT_EP = "openmano/tenants"
VIM_TENANT = BASE.format(NFVO_RO_ENDPOINT, NFVO_RO_PORT, VIM_TENANT_EP)

# Virtual network
VNF_ACTION_EXEC_EP = "api/operations/exec-ns-service-primitive"
VNF_ACTION_EXEC = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT, VNF_ACTION_EXEC_EP)

VNF_ACTION_L_EXEC_EP = "launchpad/api/exec-ns-service-primitive?" + \
                       "api_server=https://localhost"
VNF_ACTION_L_EXEC = S_BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT,
                                  VNF_ACTION_L_EXEC_EP)

# VNF_CATALOG_C = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT,
#                             "api/config/vnfr-catalog/vnfr")
VNF_CATALOG_C_EP = "composer/api/catalog?api_server=https://localhost"
VNF_CATALOG_C = S_BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT,
                              VNF_CATALOG_C_EP)
VNF_CATALOG_O_EP = "api/operational/vnfr-catalog/vnfr"
VNF_CATALOG_O = S_BASE.format(NFVO_ENDPOINT, NFVO_PORT, VNF_CATALOG_O_EP)


def get_default_headers():
    headers = rest_auth_headers()
    headers.update({"Accept": "application/vnd.yang.collection+json"})
    return headers


def post_default_headers():
    headers = rest_auth_headers()
    headers.update({"Content-Type": "application/vnd.yang.data+json",
                    "Accept": "application/vnd.yang.data+json"})
    return headers


def post_encoded_headers():
    headers = rest_auth_headers()
    headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    return headers


def rest_auth_headers():
    return {"Authorization": "Basic YWRtaW46YWRtaW4="}
