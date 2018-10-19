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
from nfv import package as pkg
from nfv.package import PackageStatusException
from server.http import content
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from server.endpoints import VnsfoEndpoints as endpoints

nfvo_views = Blueprint("nfvo_pkg_views", __name__)


@nfvo_views.route(endpoints.PKG_ONBOARD, methods=["POST"])
@content.expect_json_content
def onboard_package():
    exp_ct = "multipart/form-data"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    form_param = "package"
    if not(len(request.files) > 0 and form_param in request.files.keys()):
        Exception.improper_usage("Missing file")
    pkg_bin = request.files.get(form_param)
    return HttpResponse.json(HttpCode.ACCEPTED, pkg.onboard_package(pkg_bin))


@nfvo_views.route(endpoints.PKG_ONBOARD_REMOTE, methods=["POST"])
@content.expect_json_content
def onboard_package_remote():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    if not content.data_in_request(request, ["path"]):
        Exception.improper_usage("Missing argument: path")
    file_path = request.json.get("path")
    return HttpResponse.json(HttpCode.ACCEPTED,
                             pkg.onboard_package_remote(file_path))


@nfvo_views.route(endpoints.PKG_REMOVE, methods=["DELETE"])
def remove_package(vnsf_name):
    return HttpResponse.json(HttpCode.ACCEPTED, pkg.remove_package(vnsf_name))


@nfvo_views.route(endpoints.PKG_STATUS, methods=["GET"])
def get_package_status(transaction_id):
    try:
        return HttpResponse.json(HttpCode.ACCEPTED,
                                 pkg.get_package_status(transaction_id))
    except PackageStatusException:
        Exception.improper_usage(
            "Package Status Exception, check transaction_id")
