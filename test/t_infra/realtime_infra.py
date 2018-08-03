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
from src.server.mocks.node import MockNode as node_m

import json
import time
import unittest


class TestInfraRealtime(unittest.TestCase):

    def setUp(self):
        self.post_node = endpoints_s.NODE
        self.delete_node = endpoints_s.NODE_ID
        self.utils = TestUtils()

    def test_post_node(self):
        url = self.post_node
        exp_code = HttpCode.OK
        schema = node_m().post_node_schema()
        data = {"host_name": "node.test",
                "ip_address": "192.168.10.2",
                "pcr0": "",
                "driver": "OAT",
                "analysis_type": "FULL",
                "distribution": "xenial",
                "authentication": {
                    "type": "password",
                    "username": "user",
                    "password": "password"
                },
                "isolation_policy": {
                    "name": "DownEth0",
                    "type": "ifdown",
                    "interface_name": "eth0"
                }}
        headers = {"Content-type": "application/json"}
        response = self.utils.test_post(url, schema, data, headers, exp_code)
        node_data = json.loads(response.text)
        del_url = self.delete_node.replace("<node_id>",
                                           node_data["node_id"])
        time.sleep(5)
        self.utils.test_delete(del_url, None, {}, HttpCode.NO_CONTENT)
