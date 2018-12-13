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


import json

from core.exception import Exception
from flask import Blueprint
from flask import request
from nfv.vnf import VnsfoVnsf
from server.http import content
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from server.endpoints import VnsfoEndpoints as endpoints

nfvo_views = Blueprint("nfvo_vnf_views", __name__)


@nfvo_views.route(endpoints.VNSF_C_VNSFS, methods=["GET"])
@nfvo_views.route(endpoints.VNSF_C_VNSFS_R2, methods=["GET"])
def fetch_config_vnsfs():
    vnf_object = VnsfoVnsf()
    return HttpResponse.json(HttpCode.OK, vnf_object.get_vnfr_config())


@nfvo_views.route(endpoints.VNSF_C_VNSFS_R4, methods=["GET"])
def fetch_config_vnsfs_r4():
    vnf_object = VnsfoVnsf(4)
    return HttpResponse.json(HttpCode.OK, vnf_object.get_vnfr_config())


@nfvo_views.route(endpoints.VNSF_R_VNSFS, methods=["GET"])
@nfvo_views.route(endpoints.VNSF_R_VNSFS_R2, methods=["GET"])
def fetch_running_vnsfs():
    vnf_object = VnsfoVnsf()
    return HttpResponse.json(HttpCode.OK, vnf_object.get_vnfr_running())


@nfvo_views.route(endpoints.VNSF_R_VNSFS_R4, methods=["GET"])
def fetch_running_vnsfs_r4():
    vnf_object = VnsfoVnsf(4)
    return HttpResponse.json(HttpCode.OK, vnf_object.get_vnfr_running())


@nfvo_views.route(endpoints.VNSF_VNSF_TENANT, methods=["GET"])
@nfvo_views.route(endpoints.VNSF_VNSF_TENANT_R2, methods=["GET"])
def fetch_running_vnsfs_per_tenant(tenant_id):
    Exception.not_implemented()


@nfvo_views.route(endpoints.VNSF_VNSF_TENANT_R4, methods=["GET"])
def fetch_running_vnsfs_per_tenant_r4(tenant_id):
    Exception.not_implemented()


@nfvo_views.route(endpoints.VNSF_ACTION_EXEC, methods=["POST"])
@nfvo_views.route(endpoints.VNSF_ACTION_EXEC_R2, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf():
    vnf_object = VnsfoVnsf()
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    exp_params = ["vnsf_id", "action", "params"]
    if not content.data_in_request(
            request, exp_params):
        Exception.improper_usage("Missing parameters: any of {}"
                                 .format(exp_params))
    # Extract params, respecting the specific ordering
    payload = vnf_object.submit_action_request(
        *[request.json.get(x) for x in exp_params])
    try:
        payload_data = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return HttpResponse.json(HttpCode.INTERNAL_ERROR,
                                 "{0} bad json".format(payload))
    if "statusCode" in payload_data:
        return HttpResponse.json(payload_data["statusCode"], payload)
    else:
        return HttpResponse.json(HttpCode.ACCEPTED, payload)


@nfvo_views.route(endpoints.VNSF_ACTION_EXEC_R4, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf_r4():
    vnf_object = VnsfoVnsf(4)
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    exp_params = ["vnsf_id", "action", "params"]
    if not content.data_in_request(
            request, exp_params):
        Exception.improper_usage("Missing parameters: any of {}"
                                 .format(exp_params))
    # Extract params, respecting the specific ordering
    payload = vnf_object.submit_action_request(
        *[request.json.get(x) for x in exp_params])
    try:
        payload_data = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return HttpResponse.json(HttpCode.INTERNAL_ERROR,
                                 "{0} bad json".format(payload))
    if "statusCode" in payload_data:
        return HttpResponse.json(payload_data["statusCode"], payload)
    else:
        return HttpResponse.json(HttpCode.ACCEPTED, payload)
