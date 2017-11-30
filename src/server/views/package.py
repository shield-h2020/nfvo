#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.exception import Exception
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response
from nfv import package as pkg
from server import content
from server import endpoints


nfvo_views = Blueprint("nfvo_pkg_views", __name__)


@nfvo_views.route(endpoints.PKG_ONBOARD, methods=["POST"])
@content.expect_json_content
def onboard_package():
    if "multipart/form-data" not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: 'multipart/form-data'")
    if "multipart/form-data" not in request.headers.get("Content-Type", "") and \
        request.files is None:
        Exception.improper_usage("Missing file")
    try:
        file_path = None
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
        Exception.invalid_content_type("Expected: 'application/json' or 'multipart/form-data'")
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

