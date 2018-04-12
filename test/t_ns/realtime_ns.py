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

import unittest


class TestNfvNsRealtime(unittest.TestCase):

    def setUp(self):
        self.get_nsr_config = endpoints_s.NS_C_NSS
        self.post_nsr_instantiate = endpoints_s.NS_INSTANTIATE
        self.utils = TestUtils()

    def test_get_nsr_config(self):
        url = self.get_nsr_config
        exp_code = HttpCode.OK
        schema = ns_m().get_nsr_config_schema()
        self.utils.test_get(url, schema, {}, exp_code)

    @unittest.skip(TestUtils.ignore_hazard)
    def test_post_nsr_instantiate(self):
        url = self.get_nsr_instantiate
        exp_code = HttpCode.OK
        schema = ns_m().post_nsr_instantiate_schema()
        self.utils.test_post(url, schema, {}, exp_code)
