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
from server.endpoints import VnsfoEndpoints as endpoints_s
from server.mocks.endpoints import MockEndpoints as endpoints_m
from src.core.http_code import HttpCode
import unittest


class TestServerEndpointsMocked(unittest.TestCase):

    def setUp(self):
        self.get_endpoints = endpoints_s.ROOT
        self.utils = TestUtils()

    def test_mocked_api_endpoints(self):
        url = self.get_endpoints
        exp_code = HttpCode.OK
        exp_out = endpoints_s.get_endpoints(**{"mock": True})
        schema = endpoints_m().get_api_endpoints_schema()
        self.utils.test_mocked_get(url, schema, {}, exp_code, exp_out)
