#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from nfvi import vim as vim_s
from server import content
from server import endpoints
from server import useragent


nfvo_views = Blueprint("nfvo_vim_views", __name__)


@nfvo_views.route(endpoints.VIM_LIST, methods=["GET"])
@content.expect_json_content
def get_vim_list():
    try:
        output = vim_s.get_vim_list()
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)

@nfvo_views.route(endpoints.VIM_IMAGE, methods=["POST"])
@content.expect_json_content
def register_vnf_image():
    try:
        if content.data_not_in_request(request, ["img_url", "img_checksum"]):
            abort(418)
        output = vim_s.fill_vim_template(request.json.get("img_url"), request.json.get("img_checksum"))
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)
