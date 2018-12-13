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
from src.nfv.ns import VnsfoNs as nfvo_ns
from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.http.http_code import HttpCode
from src.server.mocks.ns import MockNs as ns_m

import unittest
import uuid


class TestNfvNsMockedR2(unittest.TestCase):

    def setUp(self):
        self.get_nsr_config = endpoints_s.NS_C_NSS_R2
        self.post_nsr_instantiate = endpoints_s.NS_INSTANTIATE_R2
        self.delete_nsr = endpoints_s.NS_DELETE_R2.replace('<instance_id>',
                                                           str(uuid.uuid4()))
        self.get_nsr_running = endpoints_s.NS_R_NSS_R2
        self.nfvo_ns = nfvo_ns()
        self.utils = TestUtils()

    def test_mocked_get_nsr_config(self):
        url = self.get_nsr_config
        exp_code = HttpCode.OK
        exp_out = self.nfvo_ns.get_nsr_config(**{"mock": True})
        schema = ns_m().get_nsr_config_schema()
        self.utils.test_mocked_get(url, schema, {}, exp_code, exp_out)

    def test_mocked_post_nsr_instantiate(self):
        url = self.post_nsr_instantiate
        exp_code = HttpCode.OK
        exp_out = self.nfvo_ns.instantiate_ns(**{"mock": True})
        schema = ns_m().post_nsr_instantiate_schema()
        data = {}
        self.utils.test_mocked_post(url, schema, data, {}, exp_code, exp_out)

    def test_mocked_delete_nsr(self):
        url = self.delete_nsr
        exp_code = HttpCode.OK
        exp_out = self.nfvo_ns.delete_ns(**{"mock": True})
        schema = ns_m().delete_nsr_schema()
        self.utils.test_mocked_delete(url, schema, {}, exp_code, exp_out)

    def test_mocked_get_ns_running(self):
        url = self.get_nsr_running
        exp_code = HttpCode.OK
        exp_out = self.nfvo_ns.get_nsr_running(**{"mock": True})
        schema = ns_m().get_nsr_running_schema()
        self.utils.test_mocked_get(url, schema, {}, exp_code, exp_out)
