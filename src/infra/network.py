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

from core.exception import HttpCode
from core.log import setup_custom_logger
from sdn.odl.carbon import ODLCarbon
from tm.tm_client import TMClient

import re
import time


LOGGER = setup_custom_logger(__name__)


class Network:

    def __init__(self):
        self._odl = ODLCarbon()

    def get_network_device_running_flows(self, flow_id=None):
        #flows, result, details = self._odl.get_config_flows(flow_id)
        flows, result, details = self._odl.get_running_flows(flow_id)
        flows_data = dict()
        flows_data["flow_id"] = flow_id
        flows_data["flow"] = flows
        flows_data["result"] = result
        flows_data["details"] = details
        return flows_data

    def delete_network_device_flow(self, flow_id=None):
        result, details = self._odl.delete_config_flows(flow_id)
        flow_data = dict()
        flow_data["flow_id"] = flow_id
        flow_data["result"] = result
        flow_data["details"] = details
        return flow_data

    def attest_and_revert_switch(self, trusted_flow=None):
        trust_monitor_client = TMClient()
        # Get initial data for newcomer attestation
        attestation_info = trust_monitor_client.get_attestation_info()
        attestation_info_sdn = attestation_info.get("sdn", {})
        flow = None
        flow_data = dict()
        for attest_sdn_switch in attestation_info_sdn:
            print("Switch to check for trust => " + str(attest_sdn_switch))
            # If attestation determines the node is not trusted; then restore the flows
            if not attest_sdn_switch.get("trust"):
                flow_data["result"] = "flow_untrusted"
                if trusted_flow is None:
                    trusted_flow = self.get_network_device_running_flows().response
                trusted_flow_id = self.get_flow_id_from_flow(trusted_flow)
                print("last_trusted_flow_id = " + str(trusted_flow))
                print("last_trusted_flow = " + str(trusted_flow_id))
                print("TRUSTed switch trust=" + str(attest_sdn_switch.get("trust")))
                print("FLOWS BEFORE DELETE --> " + str(self.get_network_device_running_flows().response))
                self.delete_network_device_flow()
                flow_data["details"] = "Flow removed: {}".format(flow)
                reply = self.store_network_device_running_flow(trusted_flow_id, trusted_flow)
                print("FLOWS AFTER DELETE AND REVERT --> " + str(self.get_network_device_running_flows().response))
                # Important: only one switch is in place to be remediated
                # If a specific controller is expected (for a specific switch), then
                # the 'attest_sdn_switch.get("node")' should be used and data should
                # be retrieved from 'conf/isolation.conf'
                break
        flow_data["flow_id"] = None
        flow_data["result"] = "flow_trusted"
        flow_data["details"] = "Flow stored in DB: {}".format(flow)
        return flow_data

    def store_network_device_config_flow(self, flow_id=None, flow=None, reply=None):
        """
        Config in the vNSFO: DB
        """
        flow_data = dict()
        # Get the flow ID from the flow passed in the body
        if flow_id is None:
            flow_id = self.get_flow_id_from_flow(flow)
        flow_data["flow_id"] = flow_id if flow_id else ""
        if reply:
            flow_data["result"] = reply[0]
            flow_data["details"] = reply[1]
        else:
            flow_data["result"] = "installed"
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
        # Storing the flows as part of the running configuration also saves these into the DB
        print("prior to storing flows -> flow_id = " + str(flow_id))
        print("prior to storing flows -> flow = " + str(flow))
        result, details = self._odl.store_config_flow(flow_id, flow, self._odl.default_device,
                                                        self._odl.default_table)
        print("\n\n\n\n\nCHANGED FLOWS... RESULT = " + str(result) + ", DETAILS = " + str(details))
        # Wait for some time between pushing the SDN rules and any future attestation
        time.sleep(self._odl.push_delay / 1000.0)
        flow_data = dict()
        flow_data["flow_id"] = flow_id if flow_id else ""
        flow_data["result"] = result
        flow_data["details"] = details
        return flow_data

    def get_flow_id_from_flow(self, flow):
        """
        Obtain the flow ID to be inserted into ODL from the XML itself
        """
        flow_id_flow = re.match(".*<flow.*><id>(.*)</id>.*", str(flow), re.MULTILINE|re.DOTALL)
        return flow_id_flow.groups()[0] if flow_id_flow else None

