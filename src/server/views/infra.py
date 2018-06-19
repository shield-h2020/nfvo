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
from flask import current_app
from flask import request
from server.endpoints import VnsfoEndpoints as endpoints
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse


nfvo_views = Blueprint("nfvo_infra_views", __name__)


@nfvo_views.route(endpoints.NODE_ID, methods=["DELETE"])
def delete_node(node_id):
    current_app.mongo.delete_node(node_id)
    return ('', HttpCode.NO_CONTENT)


@nfvo_views.route(endpoints.NODE, methods=["POST"])
def register_node():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    node_data = request.get_json()
    missing_params = check_node_params(node_data)
    if len(missing_params) > 0:
        Exception.improper_usage("Missing node parameters: {0}".format(
            ", ".join(missing_params)))
    missing_auth_params = check_auth_params(node_data["authentication"])
    if len(missing_auth_params) > 0:
        Exception.improper_usage("Missing auth parameters: {0}".format(
            ", ".join(missing_auth_params)))
    missing_isolation_params = check_isolation_params(
        node_data["isolation_policy"])
    if len(missing_isolation_params) > 0:
        Exception.improper_usage("Missing isolation parameters: {0}".format(
            ", ".join(missing_isolation_params)))
    node_id = current_app.mongo.store_node_information(node_data)
    # TODO: register node in trust-monitor
    return HttpResponse.json(HttpCode.OK, {"node_id": node_id})


@nfvo_views.route(endpoints.NFVI_FLOW, methods=["GET"])
def fetch_devices_flowtable():
    Exception.not_implemented()


@nfvo_views.route(endpoints.NFVI_TOPO, methods=["GET"])
def fetch_network_topology():
    Exception.not_implemented()


@nfvo_views.route(endpoints.NFVI_NODES, methods=["GET"])
def fetch_physical_nodes():
    Exception.not_implemented()


def check_isolation_params(isolation_policy):
    params = ["name", "type"]
    missing_params = []
    for param in params:
        if param not in isolation_policy:
            missing_params.append(param)
            return missing_params
    if isolation_policy["type"] not in ("ifdown", "delflow", "shutdown"):
        Exception.\
            improper_usage("isol. type should be ifdown, delflow or shutdown")
    if isolation_policy["type"] == "ifdown":
        if "interface_name" not in isolation_policy:
            missing_params.append("interface_name")
    if isolation_policy["type"] == "delflow":
        df_params = ["flow_id", "rule"]
        for param in df_params:
            if param not in isolation_policy:
                missing_params.append(param)
    if isolation_policy["type"] == "shutdown":
        if "command" not in isolation_policy:
            missing_params.append("command")
    return missing_params


def check_auth_params(auth_data):
    params = ["username", "type"]
    missing_params = []
    for param in params:
        if param not in auth_data:
            missing_params.append(param)
            return missing_params
    if auth_data.get("type", "") not in ("password", "private_key"):
        Exception.\
            improper_usage("Auth type should be password or private_key")
    if auth_data["type"] == "password":
        if "password" not in auth_data:
            missing_params.append("password")
    if auth_data["type"] == "private_key":
        if "private_key" not in auth_data:
            missing_params.append("private_key")
    return missing_params


def check_node_params(node_data):
    params = ["host_name", "ip_address", "pcr0", "driver",
              "analysis_type", "authentication",
              "isolation_policy", "distribution"]
    missing_params = []
    for param in params:
        if param not in node_data:
            missing_params.append(param)
    return missing_params
