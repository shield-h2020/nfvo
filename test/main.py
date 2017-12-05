#!/usr/bin/env python
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


from common.test_endpoints import TestCommonEndpoints
from nfv.test_nfv import TestNfvVnf
import unittest


class TestSuite:
    def __init__(self):
        tests = [TestCommonEndpoints, TestNfvVnf]
        loader = unittest.TestLoader()
        suites_list = []
        suites_list += [loader.loadTestsFromTestCase(t) for t in tests]
        big_suite = unittest.TestSuite(suites_list)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(big_suite)

if __name__ == "__main__":
    TestSuite()
