# -*- coding: utf-8 -*-

# Copyright 2019-present i2CAT
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

import configparser
import requests
import urllib3

from core.log import setup_custom_logger


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGGER = setup_custom_logger(__name__)
CONFIG_PATH = "./"


class ODLException(Exception):
    pass


class ODLCarbon():
    """
    OpenDayLight Carbon - API client (NBI)
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("{0}conf/sdn.conf".format(CONFIG_PATH))
        # Controller
        controller_category = config["controller"]
        self.base_url = "{0}://{1}:{2}".format(
            controller_category["protocol"],
            controller_category["host"],
            controller_category["port"])
        self.headers = {"Accept": "application/xml"}
        self.username = controller_category["username"]
        self.password = controller_category["password"]
        # Infrastructure
        infra_category = config["infrastructure"]
        # Infrastructure - default values
        self.default_device = infra_category["default_device"]
        self.default_table = infra_category["default_table"]
        # General
        general_category = config["general"]
        self.push_delay = int(general_category["push_delay"])
        # ODL endpoints
        self.flows_config_url = "/restconf/config/opendaylight-inventory" \
                                + ":nodes/node/{}/flow-node-inventory:table/{}"
        self.flow_config_url = "{}/flow/{}".format(self.flows_config_url, "{}")
        self.flows_oper_url = "/restconf/operational/opendaylight-inventory" \
                              + ":nodes/node/{}/flow-node-inventory:table/{}"
        self.flow_oper_url = "{}/flow/{}".format(self.flows_oper_url, "{}")

    def get_config_flows(self, flow_id=None):
        # Query information for all flows or for specific flow from ODL
        if flow_id is None:
            flows_config_url = self.flows_config_url.format(
                    self.default_device, self.default_table)
        else:
            flows_config_url = self.flow_config_url.format(
                    self.default_device, self.default_table, flow_id)
        flows_config_url = "{}{}".format(self.base_url, flows_config_url)
        response = requests.get(flows_config_url,
                                headers=self.headers,
                                auth=(self.username, self.password),
                                verify=False)
        flows = "" if "error-message" in response.text else response.text
        result = "success" if response.status_code == \
            requests.status_codes.codes.OK else "failure"
        details = response.text if "error-message" in response.text else ""
        return (flows, result, details)

    def get_running_flows(self, flow_id=None):
        # Query information for all flows or for specific flow from the switch
        if flow_id is None:
            flows_oper_url = self.flows_oper_url.format(
                    self.default_device, self.default_table)
        else:
            flows_oper_url = self.flow_oper_url.format(
                    self.default_device, self.default_table, flow_id)
        flows_oper_url = "{}{}".format(self.base_url, flows_oper_url)
        try:
            response = requests.get(flows_oper_url,
                                    headers=self.headers,
                                    auth=(self.username, self.password),
                                    verify=False)
            flows = "" if "error-message" in response.text else response.text
            result = "success" if response.status_code == \
                requests.status_codes.codes.OK else "failure"
            details = response.text if "error-message" in response.text else ""
            return (flows, result, details)
        except Exception as e:
            raise ODLException(e)

    def store_config_flow(self, flow_id, flow, device_id=None, table_id=None):
        flow_config_url = self.flow_config_url.format(
                self.default_device, self.default_table, flow_id)
        flow_config_url = "{}{}".format(self.base_url, flow_config_url)
        self.headers.update({"Content-Type": "application/xml"})
        try:
            response = requests.put(flow_config_url,
                                    headers=self.headers,
                                    data=flow,
                                    auth=(self.username, self.password),
                                    verify=False)
            result = "success" if response.status_code == \
                requests.status_codes.codes.CREATED else "failure"
            details = response.text or ""
            if response.status_code == requests.status_codes.codes.OK:
                details = "Flow is already installed"
            return (result, details)
        except Exception as e:
            raise ODLException(e)

    def delete_config_flows(self, flow_id=None):
        # Query information for all flows or for specific flow from the switch
        if flow_id is None:
            flows_config_url = self.flows_config_url.format(
                    self.default_device, self.default_table)
        else:
            flows_config_url = self.flow_config_url.format(
                    self.default_device, self.default_table, flow_id)
        flows_config_url = "{}{}".format(self.base_url, flows_config_url)
        try:
            response = requests.delete(
                    flows_config_url, headers=self.headers,
                    auth=(self.username, self.password), verify=False)
            result = "success" if response.status_code == \
                requests.status_codes.codes.OK else "failure"
            details = response.text or ""
            return (result, details)
        except Exception as e:
            raise ODLException(e)
