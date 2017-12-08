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


from core.exception import Exception
from flask import Blueprint
from flask import jsonify
from flask import request
from nfv import vnf
from server import content
from server.endpoints import VnsfoEndpoints as endpoints


nfvo_views = Blueprint("nfvo_vnf_views", __name__)


@nfvo_views.route(endpoints.VNSF_ACTION_STATUS, methods=["GET"])
@content.expect_json_content
def check_primitive_on_vnsf(vnsf_id, action_id):
    return jsonify({})


@nfvo_views.route(endpoints.VNSF_C_VNSFS, methods=["GET"])
def fetch_config_vnsfs():
    return jsonify(vnf.get_vnfr_config())


@nfvo_views.route(endpoints.VNSF_R_VNSFS, methods=["GET"])
def fetch_running_vnsfs():
    return jsonify(vnf.fetch_running_vnsfs())


@nfvo_views.route(endpoints.VNSF_VNSF_TENANT, methods=["GET"])
def fetch_running_vnsfs_per_tenant(tenant_id):
    return jsonify({})


@nfvo_views.route(endpoints.VNSF_ACTION_EXEC, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: \"{}\"".format(exp_ct))
    exp_params = ["vnsf_id", "action", "params"]
    if not content.data_in_request(
            request, exp_params):
        Exception.improper_usage("Missing parameters: \"{}\""
                                 .format(exp_params))
    # Extract params, respecting the specific ordering
    payload = vnf.submit_action_request(
        *[request.json.get(x) for x in exp_params])
    output = payload
    return jsonify(output)
