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
from core.log import setup_custom_logger
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import request
from infra.network import Network
from infra.node import Node
from infra.node import NodeSSHException
from server.endpoints import VnsfoEndpoints as endpoints
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse

import bson
import copy


LOGGER = setup_custom_logger(__name__)


nfvo_views = Blueprint("nfvo_infra_views", __name__)


@nfvo_views.route(endpoints.NFVI_NETWORK_C_FLOW, methods=["GET"])
@nfvo_views.route(endpoints.NFVI_NETWORK_C_FLOW_ID, methods=["GET"])
def get_network_device_config_flows(flow_id=None):
    """
    Config in the vNSFO: DB
    """
    flows = current_app.mongo.get_flows(
            {"flow_id": flow_id, "trusted": "True"})
    # Flows must be casted (from the initial queryset) to a list
    flows = list(flows)
    flows = process_flows_from_db(flows)
    flows_data = dict()
    flows_data["flow_id"] = flow_id
    if flow_id is not None and len(flows) == 1:
        flows = flows[0].get("flow")
    flows_data["flow"] = flows
    return HttpResponse.json(HttpCode.OK, flows_data)


@nfvo_views.route(endpoints.NFVI_NETWORK_R_FLOW, methods=["GET"])
@nfvo_views.route(endpoints.NFVI_NETWORK_R_FLOW_ID, methods=["GET"])
def get_network_device_running_flows(flow_id=None):
    """
    Config in the vNSFO: ODL
    """
    flows_data = Network().get_network_device_running_flows(flow_id)
    print("******* flows_data = " + str(flows_data))
    return HttpResponse.json(HttpCode.OK, flows_data)


@nfvo_views.route(endpoints.NFVI_NETWORK_C_FLOW, methods=["POST"])
@nfvo_views.route(endpoints.NFVI_NETWORK_C_FLOW_ID, methods=["POST"])
def store_network_device_config_flow(flow_id=None, flow=None, trusted=False,
                                     reply=None):
    """
    Config in the vNSFO: DB
    """
    exp_ct = "application/xml"
    header_ct = request.headers.get("Content-Type", "")
    # Internall calls will come from other methods and provide reply from them
    # In such situations, the Content-Type will be defined internally
    # Otherwise, it may be fille from a previous request and be wrong
    if reply is None and header_ct is not None and exp_ct not in header_ct:
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    flow = request.data
    if reply is not None:
        flow = reply
    print("store network device config flow ---> flow = " + str(flow))
    odl = Network().odl
    current_app.mongo.store_flows(odl.default_device, odl.default_table,
                                  flow_id, flow, trusted)
    flow_data = Network().store_network_device_config_flow(flow_id, flow)
    return HttpResponse.json(HttpCode.OK, flow_data)


@nfvo_views.route(endpoints.NFVI_NETWORK_R_FLOW, methods=["POST"])
@nfvo_views.route(endpoints.NFVI_NETWORK_R_FLOW_ID, methods=["POST"])
def store_network_device_running_flow(flow_id=None, flow=None, internal=False):
    """
    Running in the vNSFO: ODL
    """
    exp_ct = "application/xml"
    header_ct = request.headers.get("Content-Type", "")
    # Internall calls will come from other methods and provide a specific flag
    # In such situations, the Content-Type will be defined internally
    if not internal and header_ct is not None and exp_ct not in header_ct:
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    if not internal:
        flow = request.data
    Network().store_network_device_running_flow(flow_id, flow)
    # Trigger attestation right after SDN rules are inserted
    last_trusted_flow = get_last_network_device_config_flow().get("flow")
    attest_data = Network().attest_and_revert_switch(last_trusted_flow)
    # Save flows and indicate whether these keep the trusted state or not
    is_device_trusted = True if attest_data.get("result", "") == \
        "flow_trusted" else False
    flow_data = store_network_device_config_flow(
            flow_id, flow, is_device_trusted, last_trusted_flow)
    print("\n\n\n\nstore_network_device_running_flow --->")
    print("flow_data received = " + str(flow_data))
    return HttpResponse.json(HttpCode.OK, flow_data.response)


@nfvo_views.route(endpoints.NFVI_NETWORK_C_FLOW, methods=["DELETE"])
@nfvo_views.route(endpoints.NFVI_NETWORK_C_FLOW_ID, methods=["DELETE"])
def delete_network_device_flow(flow_id=None):
    odl = Network().odl
    current_app.mongo.delete_flows(odl.default_device, odl.default_table,
                                   flow_id)
    flow_data = Network().delete_network_device_flow(flow_id)
    return HttpResponse.json(HttpCode.OK, flow_data)


@nfvo_views.route(endpoints.NFVI_NODE_ID, methods=["DELETE"])
def delete_node(node_id):
    Node(node_id).delete()
    return ("", HttpCode.NO_CONTENT)


@nfvo_views.route(endpoints.NFVI_NODE, methods=["GET"])
@nfvo_views.route(endpoints.NFVI_NODE_ID, methods=["GET"])
def get_nodes(node_id=None):
    if node_id is not None:
        if bson.objectid.ObjectId.is_valid(node_id) is False:
            Exception.improper_usage("Bad node_id: {0}".format(node_id))
    nodes = current_app.mongo.get_nodes(node_id)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_PHYSICAL, methods=["GET"])
def get_nodes_physical():
    nodes = current_app.mongo.get_phys_virt_nodes(physical=True)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_PHYSICAL_ISOLATED, methods=["GET"])
def get_nodes_physical_isolated(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=True,
                                                  isolated=True)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_PHYSICAL_TRUSTED, methods=["GET"])
def get_nodes_physical_trusted(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=True,
                                                  isolated=False)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_VIRTUAL, methods=["GET"])
def get_nodes_virtual():
    nodes = current_app.mongo.get_phys_virt_nodes(physical=False)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_VIRTUAL_ISOLATED, methods=["GET"])
def get_nodes_virtual_isolated(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=False,
                                                  isolated=True)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_VIRTUAL_TRUSTED, methods=["GET"])
def get_nodes_virtual_trusted(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=False,
                                                  isolated=False)
    return HttpResponse.json(HttpCode.OK, nodes)


@nfvo_views.route(endpoints.NFVI_NODE_ISOLATE, methods=["POST"])
def isolate(node_id):
    try:
        Node(node_id).isolate()
    except NodeSSHException:
        abort(500)
    return ('', HttpCode.NO_CONTENT)


@nfvo_views.route(endpoints.NFVI_NODE_TERMINATE, methods=["POST"])
def terminate(node_id):
    try:
        Node(node_id).terminate()
    except NodeSSHException:
        abort(500)
    return ('', HttpCode.NO_CONTENT)


@nfvo_views.route(endpoints.NFVI_NODE_ID, methods=["PUT"])
def config_node(node_id):
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    config_data = request.get_json()
    fields = ["isolated", "disabled", "terminated"]
    action = None
    for field in fields:
        if field in config_data:
            action = field
    if action is None:
        Exception.improper_usage("Config should be isolated or disabled")
    if type(config_data[action]) is not bool:
        Exception.improper_usage("{0} should be bool".format(action))
    if action == "isolated" and config_data[action] is True:
        try:
            Node(node_id).isolate()
        except NodeSSHException:
            abort(500)
    elif config_data[action] is False:
        Exception.improper_usage("Automated isolation revert not supported")
    if action == "terminated" and config_data[action] is True:
        try:
            Node(node_id).terminate()
        except NodeSSHException:
            abort(500)
    elif config_data[action] is False:
        Exception.improper_usage("Automated termination revert not supported")
    if action == "disabled" and config_data[action] is True:
        Node(node_id).disable()
    return ('', HttpCode.NO_CONTENT)


@nfvo_views.route(endpoints.NFVI_NODE, methods=["POST"])
def register_node():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        Exception.invalid_content_type("Expected: {}".format(exp_ct))
    node_data = request.get_json(silent=True)
    print("node_data = " + str(node_data))
    if node_data is None:
        Exception.improper_usage("Body content does not follow type: {0}"
                                 .format(exp_ct))
    missing_params = check_node_params(node_data)
    if len(missing_params) > 0:
        Exception.improper_usage("Missing node parameters: {0}".format(
            ", ".join(missing_params)))
    missing_auth_params = check_auth_params(node_data["authentication"])
    if len(missing_auth_params) > 0:
        Exception.improper_usage(
            "Missing authentication parameters: {0}".format(
                ", ".join(missing_auth_params)))
    missing_isolation_params = check_isolation_params(
        node_data["isolation_policy"])
    if len(missing_isolation_params) > 0:
        Exception.improper_usage("Missing isolation parameters: {0}".format(
            ", ".join(missing_isolation_params)))
    missing_termination_params = check_isolation_params(
        node_data["termination_policy"])
    if len(missing_termination_params) > 0:
        Exception.improper_usage("Missing termination parameters: {0}".format(
            ", ".join(missing_termination_params)))
    node_id = current_app.mongo.store_node_information(node_data)
    print("FLOWS BEFORE UNTRUSTED CHANGE --> ")
    print(str(get_network_device_running_flows().response))
    # Save the proper flows in order to revert
    # XXX REMOVE (REMOVING & INSERTING BAD FLOWS BEFORE TO FORCE TRUST=FALSE)
    # THIS WOULD BE DONE MANUALLY
    delete_network_device_flow("L2switch-0")
    # XXX IGNORE AND THEN REMOVE
    store_network_device_running_flow("L2switch-0", '<flow xmlns="urn:opendaylight:flow:inventory"><id>L2switch-0</id><hard-timeout>10</hard-timeout><idle-timeout>5</idle-timeout><cookie>3098476543630901248</cookie><instructions><instruction><order>0</order><apply-actions><action><order>0</order><output-action><max-length>65535</max-length><output-node-connector>NORMAL</output-node-connector></output-action></action></apply-actions></instruction></instructions><priority>10000</priority><flow-statistics xmlns="urn:opendaylight:flow:statistics"><packet-count>0</packet-count><byte-count>0</byte-count><duration><nanosecond>42111111</nanosecond><second>2064</second></duration></flow-statistics><table_id>0</table_id></flow>', True)
    print("FLOWS AFTER UNTRUSTED CHANGE --> ")
    print(str(get_network_device_running_flows().response))
    if "switch" in node_data.get("driver", "").lower():
        Network().attest_and_revert_switch()
    return HttpResponse.json(HttpCode.OK, {"node_id": node_id})


def get_last_network_device_config_flow():
    flows = current_app.mongo.get_flows({"trusted": "True"})
    flow = flows[0] if len(flows) > 0 else None
    flow_data = dict()
    flow_data["flow_id"] = flow.flow_id
    flow_data["flow"] = flow.flow
    return flow_data


def process_flows_from_db(flows):
    def object_to_dictionary(flow):
        return {
            "date": str(flow.date),
            "device_id": flow.device_id,
            "table_id": flow.table_id,
            "flow_id": flow.flow_id,
            "flow": flow.flow,
            "trusted": str(flow.trusted),
        }
    # Avoid modification of passed flows
    flows_c = copy.deepcopy(flows)
    if not flows_c:
        return []
    if isinstance(flows_c, list):
        if len(flows_c) > 0:
            flow = flows_c.pop()
            return [object_to_dictionary(flow)] + \
                process_flows_from_db(flows_c)
    elif isinstance(flows_c, str):
        return [object_to_dictionary(flows_c)]


def check_isolation_params(isolation_policy):
    params = ["name", "type"]
    missing_params = []
    for param in params:
        if param not in isolation_policy:
            missing_params.append(param)
            return missing_params
    if isolation_policy["type"] not in ("ifdown", "delflow", "shutdown"):
        msg = "Isolation type should be ifdown, delflow or shutdown"
        LOGGER.info(msg)
        Exception.\
            improper_usage(msg)
    if isolation_policy["type"] == "ifdown":
        if "interface_name" not in isolation_policy:
            missing_params.append("interface_name")
    if isolation_policy["type"] == "delflow":
        df_params = ["switch", "target_filter"]
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
        msg = "Authentication type should be password or private_key"
        LOGGER.info(msg)
        Exception.\
            improper_usage(msg)
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
              "isolation_policy", "termination_policy", "distribution"]
    missing_params = []
    for param in params:
        if param not in node_data:
            missing_params.append(param)
    return missing_params
