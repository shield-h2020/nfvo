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

from core.config import FullConfParser
from core.log import setup_custom_logger
from flask import current_app
from sdn.odl.carbon import ODLCarbon
from tm.tm_client import TMClient

import copy
import re
import time


LOGGER = setup_custom_logger(__name__)


class NetworkConnectException(BaseException):
    pass


class Network:

    def __init__(self):
        self.odl = ODLCarbon()
        config = FullConfParser()
        self.sdn_flow_reference = config.get("tm.sdn.reference.json")

    def get_network_reference_flows(self):
        reference_structure = dict()
        reference_static_flows = self.sdn_flow_reference
        reference_structure.update(reference_static_flows)
        # TODO Besides taking the internal flows from the file, this should
        # retrieve flows from the database and format these appropriately
        # (possibly converting from XML to JSON using the method
        # "convert_xml_flow_to_json", available in the sdn/odl/carbon module)
        return reference_structure

    def get_network_device_config_flows(self, flow_id=None):
        filters = {"trusted": True}
        if flow_id is not None:
            filters.update({"flow_id": flow_id})
        flows = current_app.mongo.get_flows(filters)
        # Flows must be casted (from the initial queryset) to a list
        flows = list(flows)
        flows = self.process_flows_from_db(flows)
        flows_data = dict()
        if not flows:
            flows_data["flow_id"] = None
        else:
            flows_data["flow_id"] = flows[0].get("flow_id")
            if flow_id is not None and len(flows) == 1:
                flows = flows[0].get("flow")
        flows_data["flow"] = flows
        return flows_data

    def get_last_network_device_config_flow(self, flow_id=None):
        """
        Get the list of the most up-to-date flows in the internal config.
        """
        flows = self.get_network_device_config_flows(flow_id)
        flow = None
        # TODO Should return the last copy (in time) of each flow
        # from the database that is trusted (i.e., added manually)
        if "flow" in flows.keys() and len(flows.get("flow")) > 0:
            if isinstance(flows.get("flow"), list):
                flow = flows.get("flow")[-1]
                if "flow" in flow:
                    flow = flow.get("flow")
                    flows["flow"] = flow
        return flows

    def get_network_device_running_flows(self, flow_id=None):
        flows, result, details = self.odl.get_running_flows(flow_id)
        flows_data = dict()
        flows_data["flow_id"] = flow_id
        flows_data["flow"] = flows
        flows_data["result"] = result
        flows_data["details"] = details
        return flows_data

    def delete_network_device_config_flow(self, flow_id=None):
        current_app.mongo.delete_flows(
                self.odl.default_device, str(self.odl.default_table), flow_id)
        flow_data = dict()
        flow_data["flow_id"] = flow_id
        flow_data["result"] = "deleted"
        flow_data["details"] = ""
        return flow_data

    def delete_network_device_config_flow_untrusted(self, flow_id=None):
        current_app.mongo.delete_flows_untrusted(
                self.odl.default_device, str(self.odl.default_table))
        flow_data = dict()
        flow_data["flow_id"] = flow_id
        flow_data["result"] = "deleted"
        flow_data["details"] = ""
        return flow_data

    def delete_network_device_running_flow(self, flow_id=None):
        result, details = self.odl.delete_config_flows(flow_id)
        flow_data = dict()
        flow_data["flow_id"] = flow_id
        flow_data["result"] = result
        flow_data["details"] = details
        return flow_data

    def attest_and_revert_switch(self, trusted_flow=None):
        trust_monitor_client = TMClient()
        # Get initial data for newcomer attestation
        attestation_info_sdn = trust_monitor_client.get_sdn_attestation()
        if not attestation_info_sdn:
            raise NetworkConnectException("Cannot request attestation status")
        flow = None
        flow_data = None
        # If node is not trusted after attestation; then restore the flows
        sdn_status = attestation_info_sdn.get("trust")
        LOGGER.info("Status of SDN attestation: {}".format(str(sdn_status)))
        if not sdn_status:
            flow_data = dict()
            flow_data["result"] = "flow_untrusted"
            if trusted_flow is None:
                # If installed flow in the operational side of ODL has produced
                # an invalid attestation status, revert from internal DB/config
                trusted_flow_data = self.get_last_network_device_config_flow()
                if trusted_flow_data.get("flow"):
                    trusted_flow = trusted_flow_data.get("flow")
                if trusted_flow_data.get("id"):
                    trusted_flow_id = trusted_flow_data.get("id")
            trusted_flow_id = self.get_flow_id_from_flow(trusted_flow)
            LOGGER.info("Proceeding to delete all running flows in the switch")
            # Delete all untrusted config flows
            # self.delete_network_device_config_flow_untrusted()
            # Delete all running flows
            self.delete_network_device_running_flow()
            flow_data["details"] = "Flow removed"
            # Insert the ones previously stored and marked as trusted
            LOGGER.info("Reverting to internal status with flow: {}\n"
                        .format(str(trusted_flow)))
            flow_data = self.store_network_device_running_flow(
                    trusted_flow_id, trusted_flow)
            # Important: only one switch is in place to be remediated
            # If specific controller is expected (for some switch), then
            # use 'attest_sdn_switch.get("node")' and data should be
            # retrieved from 'conf/isolation.conf'
            if flow_data is None:
                flow_data = dict()
                flow_data["flow_id"] = None
                flow_data["result"] = "flow_trusted"
                flow_data["details"] = "Flow stored in DB: {}".format(flow)
        return flow_data

    def store_network_device_config_flow(
            self, flow_id=None, flow=None, trusted=False, install=False):
        """
        Config in the vNSFO: DB
        """
        # By default, externally added rules are marked as untrusted
        if install and flow_id is not None and \
                (flow is not None or len(flow) == 0):
            current_app.mongo.store_flows(self.odl.default_device,
                                          str(self.odl.default_table),
                                          flow_id, flow, trusted)
        result = "installed" if install else "not_installed"
        flow_data = dict()
        # Get the flow ID from the flow passed in the body
        if flow_id is None:
            flow_id = self.get_flow_id_from_flow(flow)
        flow_data["flow_id"] = flow_id if flow_id else ""
        flow_data["result"] = result
        flow_data["details"] = ""
        return flow_data

    def store_network_device_running_flow(self, flow_id=None, flow=None):
        """
        Running in the vNSFO: ODL
        """
        if flow_id is None and flow is None:
            flow = self.get_network_device_running_flows()
        # Get the flow ID from the flow passed in the body
        flow_id = self.get_flow_id_from_flow(flow)
        # Storing the flows in the running configuration and also into our DB
        LOGGER.info("Pushing flow to switch and waiting for it. Flow: {}"
                    .format(str(flow)))
        result, details = self.odl.store_config_flow(
                flow_id, flow, self.odl.default_device,
                str(self.odl.default_table))
        # Wait after pushing the SDN rules, before any future attestation
        time.sleep(self.odl.push_delay / 1000.0)
        flow_data = dict()
        flow_data["flow_id"] = flow_id if flow_id else ""
        flow_data["result"] = result
        flow_data["details"] = details
        return flow_data

    def get_flow_id_from_flow(self, flow):
        """
        Obtain the flow ID to be inserted into ODL from the XML itself
        """
        flow_id_flow = re.match(".*<flow.*><id>(.*)</id>.*", str(flow),
                                re.MULTILINE | re.DOTALL)
        return flow_id_flow.groups()[0] if flow_id_flow else None

    def process_flows_from_db(self, flows):
        def object_to_dictionary(flow):
            return {
                "date": str(flow.date),
                "device_id": flow.device_id,
                "table_id": flow.table_id,
                "flow_id": flow.flow_id,
                "flow": flow.flow,
                "trusted": flow.trusted,
            }
        # Avoid modification of passed flows
        flows_c = copy.deepcopy(flows)
        if not flows_c:
            return []
        if isinstance(flows_c, list):
            if len(flows_c) > 0:
                flow = flows_c.pop()
                return [object_to_dictionary(flow)] + \
                    self.process_flows_from_db(flows_c)
        elif isinstance(flows_c, str):
            return [object_to_dictionary(flows_c)]
