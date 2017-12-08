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


import unittest
import uuid

from common.test_utils import TestUtils

from src.nfvi import vim as vim_s
from src.server.endpoints import VnsfoEndpoints as endpoints_s
from src.server.http.http_code import HttpCode
from src.server.mocks.vim import MockVim as vim_m


class TestVimMocked(unittest.TestCase):

    def setUp(self):
        self.get_vim_list = endpoints_s.VIM_LIST
        self.get_vim_img_list = endpoints_s.VIM_IMAGE
        self.register_vdu = endpoints_s.VIM_IMAGE_UPLOAD
        self.utils = TestUtils()

    def test_mocked_vim_list(self):
        url = self.get_vim_list
        exp_code = HttpCode.OK
        exp_out = vim_s.get_vim_list(**{"mock": True})
        data = {}
        schema = vim_m().get_vim_list_schema()
        self.utils.test_mocked_get(url, schema, data, exp_code, exp_out)

    def test_mocked_vim_img_list(self):
        url = self.get_vim_img_list
        exp_code = HttpCode.OK
        exp_out = vim_s.get_vim_img_list(**{"mock": True})
        data = {}
        schema = vim_m().get_vim_img_list_schema()
        self.utils.test_mocked_get(url, schema, data, exp_code, exp_out)

    def test_mocked_register_vdu(self):
        url = self.register_vdu.replace("<vim_id>", str(uuid.uuid4()))
        exp_code = HttpCode.OK
        exp_out = vim_s.register_vdu(**{"mock": True})
        headers = {}
        data = {}
        schema = vim_m().register_vdu_schema()
        self.utils.test_mocked_post(url, schema, data,
                                    headers, exp_code, exp_out)
