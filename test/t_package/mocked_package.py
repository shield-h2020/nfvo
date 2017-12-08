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
from src.core.http_code import HttpCode
from src.nfv import package as package_s
from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.mocks.package import MockPackage as package_m

import unittest


class TestPackageMocked(unittest.TestCase):

    def setUp(self):
        self.onboard_package = endpoints_s.PKG_ONBOARD
        self.onboard_package_remote = endpoints_s.PKG_ONBOARD_REMOTE
        self.remove_package = endpoints_s.PKG_REMOVE
        self.utils = TestUtils()

    def test_mocked_onboard_package(self):
        url = self.onboard_package
        exp_code = HttpCode.OK
        exp_out = package_s.onboard_package(**{"mock": True})
        headers = {}
        data = {}
        schema = package_m().onboard_package_schema()
        self.utils.test_mocked_post(url, schema, data, headers,
                                    exp_code, exp_out)

    def test_mocked_onboard_package_remote(self):
        url = self.onboard_package_remote
        exp_code = HttpCode.OK
        exp_out = package_s.onboard_package_remote(**{"mock": True})
        headers = {}
        data = {}
        schema = package_m().onboard_package_remote_schema()
        self.utils.test_mocked_post(url, schema, data, headers,
                                    exp_code, exp_out)

    def test_mocked_remove_package(self):
        url = self.remove_package.replace("<vnsf_name>", "sample")
        exp_code = HttpCode.OK
        exp_out = package_s.remove_package(**{"mock": True})
        headers = {}
        schema = package_m().remove_package_schema()
        self.utils.test_mocked_delete(url, schema, headers, exp_code, exp_out)
