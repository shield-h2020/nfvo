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
from nfv import package as pkg
from server import content
from server import endpoints


nfvo_views = Blueprint("nfvo_pkg_views", __name__)


@nfvo_views.route(endpoints.PKG_ONBOARD, methods=["POST"])
@content.expect_json_content
def onboard_package():
    if "multipart/form-data" not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: 'multipart/form-data'")
    if "multipart/form-data" not in request.headers\
            .get("Content-Type", "") and \
            request.files is None:
        Exception.improper_usage("Missing file")
    try:
        data = request.files
        if data is not None:
            pkg_bin = data.get("package")
        output = pkg.onboard_package(pkg_bin)
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)


@nfvo_views.route(endpoints.PKG_ONBOARD_REMOTE, methods=["POST"])
@content.expect_json_content
def onboard_package_remote():
    if "application/json" not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type(
                "Expected: 'application/json' or 'multipart/form-data'")
    if "application/json" in request.headers.get("Content-Type", "") and \
            not content.data_in_request(request, ["path"]):
        Exception.improper_usage("Missing argument: 'path'")
    try:
        file_path = None
        if content.data_in_request(request, ["path"]):
            file_path = request.json.get("path")
        output = pkg.onboard_package_remote(file_path)
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)


@nfvo_views.route(endpoints.PKG_REMOVE, methods=["DELETE"])
def remove_package(vnsf_name):
    payload = pkg.remove_package(vnsf_name)
    output = payload
    return jsonify(output)
