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
from flask import request
from nfv.ns import VnsfoNs as ns_s
from server.endpoints import VnsfoEndpoints as endpoints
from server.http import content
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse

nfvo_views = Blueprint("nfvo_ns_views", __name__)
nfvo_ns = ns_s()


@nfvo_views.route(endpoints.NS_C_NSS, methods=["GET"])
def fetch_config_nss():
    return HttpResponse.json(HttpCode.OK, nfvo_ns.fetch_config_nss())


@nfvo_views.route(endpoints.NS_INSTANTIATE, methods=["POST"])
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
    result = nfvo_ns.instantiate_ns(instantiation_data)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)
