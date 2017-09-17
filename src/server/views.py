#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request

import methods

nfvo_views = Blueprint("nfvo_views", __name__)

NFVI_EP = "/nfvi/"
NFVI_C_EP = "{}config/".format(NFVI_EP)
NFVI_R_EP = "{}running/".format(NFVI_EP)
VIM_EP = "/vim/"
VNSF_EP = "/vnsf/"


# Common

@nfvo_views.route("/", methods=["GET"])
def entry():
    endpoints = methods.get_endpoints(current_app)
    output = dict()
    output["endpoints"] = endpoints
    #return methods.parse_output_json(output)
    return jsonify(output)


# NFVI (TODO)

@nfvo_views.route(NFVI_R_EP + "flowtable", methods=["GET"])
def fetch_devices_flowtable():
    return jsonify({})

@nfvo_views.route(NFVI_EP + "topology", methods=["GET"])
def fetch_network_topology():
    return jsonify({})

@nfvo_views.route(NFVI_EP + "nodes", methods=["GET"])
def fetch_physical_nodes():
    return jsonify({})

@nfvo_views.route(NFVI_C_EP + "nss", methods=["GET"])
def fetch_config_nss():
    return jsonify(methods.fetch_config_nss())

#@nfvo_views.route(NFVI_R_EP + "nss", methods=["GET"])
#def fetch_running_nss():
#    return jsonify(methods.fetch_running_nss())

#@nfvo_views.route(NFVI_C_EP + "vnsfs", methods=["GET"])
#def fetch_config_vnsfs():
#    return jsonify(methods.fetch_config_vnsfs())

@nfvo_views.route(NFVI_R_EP + "vnsfs", methods=["GET"])
def fetch_running_vnsfs():
    return jsonify(methods.fetch_running_vnsfs())

@nfvo_views.route(NFVI_R_EP + "vnsfs/<tenant_id>", methods=["GET"])
def fetch_running_vnsfs_per_tenant(tenant_id):
    return jsonify({})


# VIM (TODO)

@nfvo_views.route(VIM_EP + "vnsf_image", methods=["POST"])
@methods.expect_json_content
def register_vnf_image():
    try:
        if methods.data_not_in_request(request, ["img_url", "img_checksum"]):
            abort(418)
        output = methods.fill_vim_template(request.json.get("img_url"), request.json.get("img_checksum"))
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)


# vNSF

#@nfvo_views.route("/vnsf/policies/<vnsfr_id>", methods=["GET"])
#def fetch_policies(vnsfr_id):
#    try:
#        output = methods.fill_template(vnsfr_id)
#        return jsonify(output)
#    except Exception as e:
#        return "Error: %s" % str(e)

@nfvo_views.route(VNSF_EP + "action", methods=["POST"])
@methods.expect_json_content
def exec_primitive_on_vnsf():
    try:
        if "application/json" not in request.headers.get("Content-Type", ""):
            abort(400)
        if methods.data_not_in_request(request, ["vnsf_id", "action", "params"]):
            abort(418)
        payload = methods.submit_action_request(request.json.get("vnsf_id"), request.json.get("action"),
            request.json.get("params"))
        output = payload
        return jsonify(output)
    except Exception as e:
        return "Error: %s" % str(e)

@nfvo_views.route(VNSF_EP + "<vnsf_id>/action/<action_id>", methods=["GET"])
@methods.expect_json_content
def check_primitive_on_vnsf(vnsf_id, action_id):
    return jsonify({})
