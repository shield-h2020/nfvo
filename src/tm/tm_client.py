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

from core.log import setup_custom_logger

import configparser
import json
import requests


LOGGER = setup_custom_logger(__name__)


class TMClient:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("conf/tm.conf")
        self.host = config["general"]["host"]
        self.port = config["general"]["port"]
        self.protocol = config["general"]["protocol"]
        self.default_node = config["general"]["default_node"]

    def get_attestation_info(self):
        url = "{0}://{1}:{2}/nfvi_attestation_info/".format(
            self.protocol, self.host, self.port)
        try:
            response = requests.get(url, verify=False)
            attestation_info = json.loads(response.text)
            nfvi_node = None
            for host in attestation_info["hosts"]:
                if host["node"] == self.default_node:
                    nfvi_node = host
            LOGGER.info(json.dumps(nfvi_node, sort_keys=True, indent=4))
            return nfvi_node["remediation"]
        except Exception as excp:
            LOGGER.error("Error getting attestation info")
            LOGGER.error(excp)

    def register_node(self, node_data):
        url = "{0}://{1}:{2}/register_node/".format(
            self.protocol, self.host, self.port)
        data = {"hostName": node_data["host_name"],
                "address": node_data["ip_address"],
                "distribution": node_data["distribution"],
                "pcr0": node_data["pcr0"],
                "driver": node_data["driver"]}
        try:
            response = requests.post(url, json=data, verify=False)
            LOGGER.info("Trust Monitor response {0}".format(response.text))
            return response
        except Exception as excp:
            LOGGER.error("Error registering node in trust-monitor")
            LOGGER.error(excp)

    def delete_node(self, host_name):
        url = "{0}://{1}:{2}/register_node/".format(
            self.protocol, self.host, self.port)
        data = {"hostName": host_name}
        try:
            response = requests.delete(url,
                                       verify=False,
                                       json=data)
            LOGGER.info("Trust Monitor response {0}".format(response.text))
            return response
        except Exception as excp:
            LOGGER.error("Error deleting node in trust-monitor")
            LOGGER.error(excp)
