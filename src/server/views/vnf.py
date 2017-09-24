#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from nfv import vnf
from server import content
from server import endpoints


nfvo_views = Blueprint("nfvo_vnf_views", __name__)


@nfvo_views.route(endpoints.VNSF_ACTION_STATUS, methods=["GET"])
@content.expect_json_content
def check_primitive_on_vnsf(vnsf_id, action_id):
    return jsonify({})

@nfvo_views.route(endpoints.VNSF_VNSFS, methods=["GET"])
def fetch_running_vnsfs():
    return jsonify(vnf.fetch_running_vnsfs())

@nfvo_views.route(endpoints.VNSF_VNSF_TENANT, methods=["GET"])
def fetch_running_vnsfs_per_tenant(tenant_id):
    return jsonify({})

@nfvo_views.route(endpoints.VNSF_ACTION_EXEC, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf():
    try:
        if "application/json" not in request.headers.get("Content-Type", ""):
            abort(400)
        if content.data_not_in_request(request, ["vnsf_id", "action", "params"]):
            abort(418)
        payload = vnf.submit_action_request(request.json.get("vnsf_id"), request.json.get("action"),
            request.json.get("params"))
        output = payload
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)
