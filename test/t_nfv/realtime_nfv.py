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


import os
import unittest

from common.test_utils import TestUtils

from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.http.http_code import HttpCode
from src.server.mocks.vnf import MockVnfs as vnfs_m


class TestNfvVnfRealtime(unittest.TestCase):

    def setUp(self):
        self.exec_action_on_vnf = endpoints_s.VNSF_ACTION_EXEC
        self.get_vnfr_config = endpoints_s.VNSF_C_VNSFS
        self.vnsf_running_list = endpoints_s.VNSF_R_VNSFS
        self.utils = TestUtils()

    def test_vnsf_running_list(self):
        url = self.vnsf_running_list
        exp_code = HttpCode.OK
        headers = {}
        schema = vnfs_m().get_vnfr_running_schema()
        self.utils.test_get(url, schema, headers, exp_code)

    def test_get_vnfr_config(self):
        url = self.get_vnfr_config
        exp_code = HttpCode.OK
        headers = {}
        schema = vnfs_m().get_vnfr_config_schema()
        self.utils.test_get(url, schema, headers, exp_code)

    @unittest.skip(TestUtils.ignore_hazard)
    def test_exec_action_on_vnf(self):
        url = self.exec_action_on_vnf
        exp_code = HttpCode.OK
        headers = {}
        data = {}
        schema = vnfs_m().exec_action_on_vnf_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)

    def test_exec_action_on_vnf_invalid_header(self):
        url = self.exec_action_on_vnf
        exp_code = HttpCode.UNSUP_MEDIA
        headers = {"Content-Type": "invalid/content"}
        data = {}
        schema = vnfs_m().exec_action_on_vnf_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)

    def test_exec_action_on_vnf_invalid_data(self):
        url = self.exec_action_on_vnf
        exp_code = HttpCode.TEAPOT
        headers = {"Content-Type": "application/json"}
        # Sample file (not even a package)
        file_loc = os.path.abspath(__file__)
        data = {"invalid_key": file_loc}
        schema = vnfs_m().exec_action_on_vnf_schema()
        self.utils.test_post(url, schema, data, headers, exp_code)
