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
from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.mocks.package import MockPackage as package_m

import os
import unittest


class TestPackageRealtime(unittest.TestCase):

    def setUp(self):
        self.onboard_package = endpoints_s.PKG_ONBOARD
        self.onboard_package_remote = endpoints_s.PKG_ONBOARD_REMOTE
        self.remove_package = endpoints_s.PKG_REMOVE
        self.utils = TestUtils()

    @unittest.skip(TestUtils.ignore_hazard)
    def test_onboard_package(self):
        url = self.onboard_package
        exp_code = HttpCode.OK
        # Content-Type automatically set by requests (along with boundary)
        # headers = {"Content-Type": "multipart/form-data"}
        headers = {}
        # Sample file (not even a package)
        file_loc = os.path.abspath(__file__)
        data = {"package": file_loc}
        schema = package_m().onboard_package_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)

    @unittest.skip(TestUtils.ignore_hazard)
    def test_onboard_package_remote(self):
        url = self.onboard_package_remote
        exp_code = HttpCode.OK
        headers = {"Content-Type": "application/json"}
        # Sample file (not even a package)
        file_loc = os.path.abspath(__file__)
        data = {"path": file_loc}
        schema = package_m().onboard_package_remote_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)

    def test_onboard_package_remote_invalid_header(self):
        url = self.onboard_package_remote
        exp_code = HttpCode.UNSUP_MEDIA
        headers = {"Content-Type": "invalid/content"}
        data = {}
        schema = package_m().onboard_package_remote_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)

    def test_onboard_package_remote_invalid_data(self):
        url = self.onboard_package_remote
        exp_code = HttpCode.TEAPOT
        headers = {"Content-Type": "application/json"}
        data = {"invalid_key": ""}
        schema = package_m().onboard_package_remote_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)

    @unittest.skip(TestUtils.ignore_hazard)
    def test_remove_package(self):
        url = self.remove_package.replace("<vnsf_name>", "invalid-pkg")
        exp_code = HttpCode.OK
        headers = {}
        schema = package_m().remove_package_schema()
        self.utils.test_delete(url, schema, headers, exp_code)
