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


from core import regex as regex_r

import unittest
import uuid


class TestRegex(unittest.TestCase):

    def test_uuid4(self):
        uuid_sample = str(uuid.uuid4())
        self.assertNotEquals(None, regex_r.uuid4(uuid_sample))

    def test_unix_path(self):
        path_sample = "/path/to/something"
        self.assertNotEquals(None, regex_r.unix_path(path_sample))

    @unittest.expectedFailure
    def test_unix_path_invalid(self):
        path_sample = "not/abs/path"
        self.assertNotEquals(None, regex_r.unix_path(path_sample))

    def test_rfc3399(self):
        date_sample = "2102-12-30T21:51:23Z"
        self.assertNotEquals(None, regex_r.rfc3399(date_sample))

    @unittest.expectedFailure
    def test_rfc3399_invalid(self):
        date_sample = "2102-12-30 21:51:23"
        self.assertNotEquals(None, regex_r.rfc3399(date_sample))
