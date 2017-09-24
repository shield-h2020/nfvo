#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
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
    try:
        if "application/json" not in request.headers.get("Content-Type", ""):
            abort(400)
        if content.data_not_in_request(request, ["path"]):
            abort(418)
        payload = pkg.onboard_package(request.json.get("path"))
        output = payload
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)
