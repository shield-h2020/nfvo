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
from core.log import setup_custom_logger
from flask import Blueprint
from flask import request
from nfv.ns import VnsfoNs
from server.endpoints import VnsfoEndpoints as endpoints
from server.http import content
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from server.views.infra import check_auth_params
from server.views.infra import check_isolation_params


LOGGER = setup_custom_logger(__name__)


nfvo_views = Blueprint("nfvo_ns_views", __name__)


@nfvo_views.route(endpoints.NS_C_NSS, methods=["GET"])
@nfvo_views.route(endpoints.NS_C_NSS_R2, methods=["GET"])
def fetch_config_nss():
    ns_object = VnsfoNs()
    return HttpResponse.json(HttpCode.OK, ns_object.fetch_config_nss())


@nfvo_views.route(endpoints.NS_C_NSS_R4, methods=["GET"])
def fetch_config_nss_r4():
    ns_object = VnsfoNs(4)
    return HttpResponse.json(HttpCode.OK,
                             ns_object.fetch_config_nss())


@nfvo_views.route(endpoints.NS_INSTANTIATE, methods=["POST"])
@nfvo_views.route(endpoints.NS_INSTANTIATE_R2, methods=["POST"])
@content.expect_json_content
def instantiate_ns():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    instantiation_data = request.get_json()
    exp_params = ["ns_name", "instance_name"]
    if not content.data_in_request(request, exp_params):
        Exception.improper_usage("Missing parameters: any of {}"
                                 .format(exp_params))
    if "authentication" in instantiation_data:
        missing_params = check_auth_params(
            instantiation_data["authentication"])
        if len(missing_params) > 0:
            msg = "Missing authentication parameters {0}".format(
                ", ".join(missing_params))
            LOGGER.info(msg)
            Exception.improper_usage(msg)
    if "isolation_policy" in instantiation_data:
        missing_params = check_isolation_params(
            instantiation_data["isolation_policy"])
        if len(missing_params) > 0:
            msg = "Missing isolation policy parameters {0}".format(
                    ", ".join(missing_params))
            LOGGER.info(msg)
            Exception.improper_usage(msg)
    if "termination_policy" in instantiation_data:
        missing_params = check_isolation_params(
            instantiation_data["termination_policy"])
        if len(missing_params) > 0:
            msg = "Missing termination policy parameters {0}".format(
                    ", ".join(missing_params))
            LOGGER.info(msg)
            Exception.improper_usage(msg)
    ns_object = VnsfoNs()
    result = ns_object.instantiate_ns(instantiation_data)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)


@nfvo_views.route(endpoints.NS_INSTANTIATE_R4, methods=["POST"])
@content.expect_json_content
def instantiate_ns_r4():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    instantiation_data = request.get_json()
    exp_params = ["ns_name", "instance_name"]
    if not content.data_in_request(request, exp_params):
        Exception.improper_usage("Missing parameters: any of {}"
                                 .format(exp_params))
    ns_object = VnsfoNs(4)
    result = ns_object.instantiate_ns(instantiation_data)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)


@nfvo_views.route(endpoints.NS_R_NSS, methods=["GET"])
@nfvo_views.route(endpoints.NS_R_NSS_ID, methods=["GET"])
@nfvo_views.route(endpoints.NS_R_NSS_R2, methods=["GET"])
@nfvo_views.route(endpoints.NS_R_NSS_ID_R2, methods=["GET"])
def fetch_running_nss(instance_id=None):
    ns_object = VnsfoNs()
    nss = ns_object.get_nsr_running(instance_id)
    return HttpResponse.json(HttpCode.OK, nss)


@nfvo_views.route(endpoints.NS_R_NSS_R4, methods=["GET"])
@nfvo_views.route(endpoints.NS_R_NSS_ID_R4, methods=["GET"])
def fetch_running_nss_r4(instance_id=None):
    ns_object = VnsfoNs(4)
    nss = ns_object.get_nsr_running(instance_id)
    return HttpResponse.json(HttpCode.OK, nss)


@nfvo_views.route(endpoints.NS_R_NSS)
@nfvo_views.route(endpoints.NS_R_NSS_ID, methods=["DELETE"])
@nfvo_views.route(endpoints.NS_R_NSS_R2)
@nfvo_views.route(endpoints.NS_R_NSS_ID_R2, methods=["DELETE"])
def delete_ns(instance_id=None):
    ns_object = VnsfoNs()
    result = ns_object.delete_ns(instance_id)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)


@nfvo_views.route(endpoints.NS_R_NSS_R4)
@nfvo_views.route(endpoints.NS_R_NSS_ID_R4, methods=["DELETE"])
def delete_ns_r4(instance_id=None):
    ns_object = VnsfoNs(4)
    result = ns_object.delete_ns(instance_id)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)
