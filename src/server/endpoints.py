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
    NFVI_FLOW = "{}/flowtable".format(NFVI)
    NFVI_NODE = "{}/node".format(NFVI)
    NFVI_TOPO = "{}/network".format(NFVI)
    # - Nodes
    NFVI_NODE_ID = "{}/<node_id>".format(NFVI_NODE)
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
    # Package
    PKG = "/package"
    PKG_ONBOARD = "{}/onboard".format(PKG)
    PKG_STATUS = "{}/<transaction_id>/status".format(PKG)
    PKG_ONBOARD_REMOTE = "{}/remote".format(PKG_ONBOARD)
    PKG_REMOVE = "{}/<vnsf_name>".format(PKG)
    # Network function
    VNSF = "/vnsf"
    VNSF_ACTION_EXEC = "{}/action".format(VNSF)
    VNSF_C_VNSFS = "{}/config".format(VNSF)
    VNSF_R_VNSFS = "{}/running".format(VNSF)
    VNSF_VNSF_TENANT = "{}/<tenant_id>".format(VNSF_R_VNSFS)

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
