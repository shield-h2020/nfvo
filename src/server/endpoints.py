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
from flask import request
from flask import url_for
from gui import swagger
from server.http import content
from server.http import useragent
from server.mocks.endpoints import MockEndpoints as endpoints_m


class VnsfoEndpoints:

    # Endpoints
    # Generic
    ROOT = "/"
    # Infrastructure
    NFVI = "/nfvi"
    NFVI_NETWORK = "{}/network".format(NFVI)
    NFVI_NODE = "{}/node".format(NFVI)
    # - Network
    NFVI_NETWORK_C = "{}/config".format(NFVI_NETWORK)
    NFVI_NETWORK_C_FLOW = "{}/flows".format(NFVI_NETWORK_C)
    NFVI_NETWORK_C_FLOW_ID = "{}/flows/<flow_id>".format(NFVI_NETWORK_C)
    NFVI_NETWORK_R = "{}/running".format(NFVI_NETWORK)
    NFVI_NETWORK_R_FLOW = "{}/flows".format(NFVI_NETWORK_R)
    NFVI_NETWORK_R_FLOW_ID = "{}/flows/<flow_id>".format(NFVI_NETWORK_R)
    NFVI_NETWORK_TOPO = "{}/nodes".format(NFVI_NETWORK)
    # - Nodes
    NFVI_NODE_ID = "{}/<node_id>".format(NFVI_NODE)
    NFVI_NODE_ISOLATE = "{}/isolate".format(NFVI_NODE_ID)
    NFVI_NODE_TERMINATE = "{}/terminate".format(NFVI_NODE_ID)
    NFVI_NODE_PHYSICAL = "{}/physical".format(NFVI_NODE)
    NFVI_NODE_PHYSICAL_ISOLATED = "{}/isolated".format(NFVI_NODE_PHYSICAL)
    NFVI_NODE_PHYSICAL_TRUSTED = "{}/trusted".format(NFVI_NODE_PHYSICAL)
    NFVI_NODE_VIRTUAL = "{}/virtual".format(NFVI_NODE)
    NFVI_NODE_VIRTUAL_ISOLATED = "{}/isolated".format(NFVI_NODE_VIRTUAL)
    NFVI_NODE_VIRTUAL_TRUSTED = "{}/trusted".format(NFVI_NODE_VIRTUAL)
    # Infrastructure manager
    VIM = "/vim"
    VIM_IMAGE = "{}/image".format(VIM)
    VIM_IMAGE_UPLOAD = "{}/<vim_id>".format(VIM_IMAGE)
    VIM_LIST = VIM
    # Network service
    NS = "/ns"
    NS_C_NSS = "{}/config".format(NS)
    NS_INSTANTIATE = "{}/instantiate".format(NS)
    NS_DELETE = "{}/running/<instance_id>".format(NS)
    NS_R_NSS = "{}/running".format(NS)
    NS_R_NSS_ID = "{}/<instance_id>".format(NS_R_NSS)
    # Network service (explicit release 2)
    NS_R2 = "/ns/r2"
    NS_C_NSS_R2 = "{}/config".format(NS_R2)
    NS_C_NSS_R2 = "{}/config".format(NS_R2)
    NS_INSTANTIATE_R2 = "{}/instantiate".format(NS_R2)
    NS_DELETE_R2 = "{}/running/<instance_id>".format(NS_R2)
    NS_R_NSS_R2 = "{}/running".format(NS_R2)
    NS_R_NSS_ID_R2 = "{}/<instance_id>".format(NS_R_NSS_R2)
    # Network service (release 4)
    NS_R4 = "/ns/r4"
    NS_C_NSS_R4 = "{}/config".format(NS_R4)
    NS_C_NSS_R4 = "{}/config".format(NS_R4)
    NS_INSTANTIATE_R4 = "{}/instantiate".format(NS_R4)
    NS_DELETE_R4 = "{}/running/<instance_id>".format(NS_R4)
    NS_R_NSS_R4 = "{}/running".format(NS_R4)
    NS_R_NSS_ID_R4 = "{}/<instance_id>".format(NS_R_NSS_R4)
    # Package
    PKG = "/package"
    PKG_ONBOARD = "{}/onboard".format(PKG)
    PKG_ONBOARD_REMOTE = "{}/remote".format(PKG_ONBOARD)
    PKG_REMOVE = "{}/<vnsf_name>".format(PKG)
    # Package (explicit release 2)
    PKG_R2 = "/package/r2"
    PKG_ONBOARD_R2 = "{}/onboard".format(PKG_R2)
    PKG_ONBOARD_REMOTE_R2 = "{}/remote".format(PKG_ONBOARD_R2)
    PKG_REMOVE_R2 = "{}/<vnsf_name>".format(PKG_R2)
    # Package (release 4)
    PKG_R4 = "/package/r4"
    PKG_ONBOARD_R4 = "{}/onboard".format(PKG_R4)
    PKG_ONBOARD_REMOTE_R4 = "{}/remote".format(PKG_ONBOARD_R4)
    PKG_REMOVE_R4 = "{}/<vnsf_name>".format(PKG_R4)
    # Network function
    VNSF = "/vnsf"
    VNSF_ACTION_EXEC = "{}/action".format(VNSF)
    VNSF_C_VNSFS = "{}/config".format(VNSF)
    VNSF_R_VNSFS = "{}/running".format(VNSF)
    VNSF_VNSF_TENANT = "{}/<tenant_id>".format(VNSF_R_VNSFS)
    # Network function (explicit release 2)
    VNSF_R2 = "/vnsf/r2"
    VNSF_ACTION_EXEC_R2 = "{}/action".format(VNSF_R2)
    VNSF_C_VNSFS_R2 = "{}/config".format(VNSF_R2)
    VNSF_R_VNSFS_R2 = "{}/running".format(VNSF_R2)
    VNSF_VNSF_TENANT_R2 = "{}/<tenant_id>".format(VNSF_R_VNSFS_R2)
    # Network function (release 4)
    VNSF_R4 = "/vnsf/r4"
    VNSF_ACTION_EXEC_R4 = "{}/action".format(VNSF_R4)
    VNSF_C_VNSFS_R4 = "{}/config".format(VNSF_R4)
    VNSF_R_VNSFS_R4 = "{}/running".format(VNSF_R4)
    VNSF_VNSF_TENANT_R4 = "{}/<tenant_id>".format(VNSF_R_VNSFS_R4)

    def __init__(self):
        self.get_api_endpoints_mock = endpoints_m().get_api_endpoints_mock

    def api_endpoints(self):
        """
        Return endpoints in a formatted way, depending on the client.
        1) cURL will return a list of endpoints and method types
        2) Every other client will return the Swagger docs
        """
        if "curl" in useragent.get_user_agent(request):
            return self.get_endpoints(current_app)
        else:
            return swagger.generate_swagger_docs()

    @content.on_mock(endpoints_m().get_api_endpoints_mock)
    def get_endpoints(self, app):
        links = {"endpoints": []}
        for rule in app.url_map.iter_rules():
            if "static" in rule.endpoint:
                break
            if content.has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
            else:
                url = rule.rule
            links.get("endpoints").append({
                "endpoint": url,
                "methods": content.filter_actions(rule.methods)})
        return links
