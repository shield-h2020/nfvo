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


from common.test_utils import TestUtils
from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.http.http_code import HttpCode
from src.server.mocks.infra import MockInfra as infra_m

import json
import unittest


class TestInfraRealtime(unittest.TestCase):

    def setUp(self):
        self.post_node = endpoints_s.NFVI_NODE
        self.delete_node = endpoints_s.NFVI_NODE_ID
        self.utils = TestUtils()

    def create_node(self, physical=None):
        print(self)
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
        headers = {"Content-type": "application/json"}
        response = self.utils.test_post(url, schema, data, headers, exp_code)
        node_data = json.loads(response.text)
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
