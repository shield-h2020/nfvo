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
from src.server.mocks.ns import MockNs as ns_m

import json
import time
import unittest


class TestNfvNsRealtime(unittest.TestCase):

    def setUp(self):
        self.get_nsr_config = endpoints_s.NS_C_NSS
        self.post_nsr_instantiate = endpoints_s.NS_INSTANTIATE
        self.delete_nsr = endpoints_s.NS_DELETE
        self.get_nsr_running = endpoints_s.NS_R_NSS
        self.utils = TestUtils()

    def test_get_nsr_config(self):
        url = self.get_nsr_config
        exp_code = HttpCode.OK
        schema = ns_m().get_nsr_config_schema()
        self.utils.test_get(url, schema, {}, exp_code)

    def test_post_nsr_instantiate(self):
        url = self.post_nsr_instantiate
        exp_code = HttpCode.OK
        schema = ns_m().post_nsr_instantiate_schema()
        data = {"instance_name": "realtime-test",
                "ns_name": "fl7filter_nsd",
                "vim_net": "provider",
                "action": "set-policies",
                "params": {"policies": "test-policy"}}
        headers = {"Content-type": "application/json"}
        response = self.utils.test_post(url, schema, data, headers, exp_code)
        instantiation_data = json.loads(response.text)
        del_url = self.delete_nsr.replace("<instance_id>",
                                          instantiation_data["instance_id"])
        del_schema = ns_m().delete_nsr_schema()
        time.sleep(5)
        self.utils.test_delete(del_url, del_schema, {}, exp_code)

    def test_get_nsr_running(self):
        url = self.get_nsr_running
        exp_code = HttpCode.OK
        schema = ns_m().get_nsr_running_schema()
        self.utils.test_get(url, schema, {}, exp_code)
