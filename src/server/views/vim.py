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


from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from nfvi import vim as vim_s
from server import content
from server import endpoints


nfvo_views = Blueprint("nfvo_vim_views", __name__)


@nfvo_views.route(endpoints.VIM_LIST, methods=["GET"])
@content.expect_json_content
def get_vim_list():
    try:
        output = vim_s.get_vim_list()
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)


@nfvo_views.route(endpoints.VIM_IMAGE, methods=["GET"])
@content.expect_json_content
def get_vim_images():
    try:
        output = vim_s.get_vim_img_list()
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)


@nfvo_views.route(endpoints.VIM_IMAGE, methods=["POST"])
@content.expect_json_content
def register_vnf_image():
    try:
        if not content.data_in_request(request, ["img_url", "img_checksum"]):
            abort(418)
        output = vim_s.fill_vim_template(
                request.json.get("img_url"),
                request.json.get("img_checksum"))
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)
