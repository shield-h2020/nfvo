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


from common.rest_cfg import api_url
from common.test_utils import TestUtils
from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.http.http_code import HttpCode
from src.server.mocks.infra import MockInfra as infra_m

import json
import requests
import unittest


class TestInfraRealtime(unittest.TestCase):

    def setUp(self):
        self.post_node = endpoints_s.NFVI_NODE
        self.delete_node = endpoints_s.NFVI_NODE_ID
        self.virtual_url = "{0}{1}".format(api_url,
                                           endpoints_s.NFVI_NODE_VIRTUAL)
        self.virtual_isolated_url = "{0}{1}".format(
            api_url,
            endpoints_s.NFVI_NODE_VIRTUAL_ISOLATED)
        self.virtual_trusted_url = "{0}{1}".format(
            api_url,
            endpoints_s.NFVI_NODE_VIRTUAL_TRUSTED)
        self.physical_url = "{0}{1}".format(
            api_url,
            endpoints_s.NFVI_NODE_PHYSICAL)
        self.physical_isolated_url = "{0}{1}".format(
            api_url,
            endpoints_s.NFVI_NODE_PHYSICAL_ISOLATED)
        self.physical_trusted_url = "{0}{1}".format(
            api_url,
            endpoints_s.NFVI_NODE_PHYSICAL_TRUSTED)
        self.utils = TestUtils()

    def get_virtual_length(self):
        virtual = json.loads(requests.get(self.virtual_url,
                                          verify=False).text)
        return len(virtual)

    def get_virtual_isolated_length(self):
        virtual_isolated = json.loads(requests.get(self.virtual_isolated_url,
                                                   verify=False).text)
        return len(virtual_isolated)

    def get_virtual_trusted_length(self):
        virtual_trusted = json.loads(requests.get(self.virtual_trusted_url,
                                                  verify=False).text)
        return len(virtual_trusted)

    def get_physical_length(self):
        physical = json.loads(requests.get(self.physical_url,
                                           verify=False).text)
        return len(physical)

    def get_physical_isolated_length(self):
        physical_isolated = json.loads(requests.get(self.physical_isolated_url,
                                                    verify=False).text)
        return len(physical_isolated)

    def get_physical_trusted_length(self):
        physical_trusted = json.loads(requests.get(self.physical_trusted_url,
                                                   verify=False).text)
        return len(physical_trusted)

    def create_node(self, physical=None):
        phys_virt = False
        if physical is not None:
            phys_virt = physical
        url = self.post_node
        exp_code = HttpCode.OK
        schema = infra_m().post_node_schema()
        data = {"host_name": "84.88.40.113",
                "ip_address": "84.88.40.113",
                "pcr0": "example",
                "driver": "OAT",
                "analysis_type": "FULL",
                "distribution": "xenial",
                "authentication": {
                    "type": "password",
                    "username": "user",
                    "password": "password"
                },
                "physical": phys_virt,
                "isolation_policy": {
                    "name": "Dummy",
                    "type": "shutdown",
                    "command": "ls -laht"
                }}
        prv_virtual = self.get_virtual_length()
        prv_virtual_isolated = self.get_virtual_isolated_length()
        prv_virtual_trusted = self.get_virtual_trusted_length()
        prv_physical = self.get_physical_length()
        prv_physical_isolated = self.get_physical_isolated_length()
        prv_physical_trusted = self.get_physical_trusted_length()
        headers = {"Content-type": "application/json"}
        response = self.utils.test_post(url, schema, data, headers, exp_code)
        node_data = json.loads(response.text)
        cur_virtual = self.get_virtual_length()
        cur_virtual_isolated = self.get_virtual_isolated_length()
        cur_virtual_trusted = self.get_virtual_trusted_length()
        cur_physical = self.get_physical_length()
        cur_physical_isolated = self.get_physical_isolated_length()
        cur_physical_trusted = self.get_physical_trusted_length()
        if phys_virt is False:
            assert cur_virtual == prv_virtual + 1
            assert cur_physical == prv_physical
            assert cur_virtual_trusted == prv_virtual_trusted + 1
            assert cur_virtual_isolated == prv_virtual_isolated
        else:
            assert cur_virtual == prv_virtual
            assert cur_physical == prv_physical + 1
            assert cur_physical_trusted == prv_physical_trusted + 1
            assert cur_physical_isolated == prv_physical_isolated
        del_url = self.delete_node.replace("<node_id>",
                                           node_data["node_id"])
        self.utils.test_put(del_url, None,
                            {"disabled": True},
                            headers,
                            HttpCode.NO_CONTENT)
        self.utils.test_delete(del_url, None, {}, HttpCode.NO_CONTENT)

    def test_post_node(self):
        self.create_node()

    def test_post_physical_node(self):
        self.create_node(True)
