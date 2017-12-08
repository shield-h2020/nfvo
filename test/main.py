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


import argparse
import unittest

from t_nfv.mocked_nfv import TestNfvVnfMocked
from t_nfv.realtime_nfv import TestNfvVnfRealtime
from t_server.mocked_endpoints import TestServerEndpointsMocked
from t_server.realtime_endpoints import TestServerEndpointsRealtime
from t_vim.mocked_vim import TestVimMocked
from t_vim.realtime_vim import TestVimRealtime


class TestSuite:

    def __init__(self, args):
        mocked, realtime = args.mock, args.real_time
        tests = []
        tests_mocked = self.__define_tests_mocked()
        tests_realtime = self.__define_tests_realtime()
        if mocked:
            tests += tests_mocked
        elif realtime:
            tests += tests_realtime
        else:
            tests += [tests_mocked, tests_realtime]

        loader = unittest.TestLoader()
        suites_list = []
        suites_list += [loader.loadTestsFromTestCase(t) for t in tests]
        self.suite = unittest.TestSuite(suites_list)

    def __define_tests_realtime(self):
        return [
            TestNfvVnfRealtime,
            TestServerEndpointsRealtime,
            TestVimRealtime,
        ]

    def __define_tests_mocked(self):
        return [
            TestNfvVnfMocked,
            TestServerEndpointsMocked,
            TestVimMocked,
        ]

    def run(self):
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(self.suite)


def parse_args():
    parser = argparse.ArgumentParser(description="Run unit tests")
    parser.add_argument("-m", "--mock", action="store_true",
                        help="Run mocked tests only")
    parser.add_argument("-r", "--real-time", action="store_true",
                        help="Run real-time tests only")
    return parser


if __name__ == "__main__":
    parser = parse_args()
    test_suite = TestSuite(parser.parse_args())
    test_suite.run()
