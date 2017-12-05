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


from common.rest_cfg import api_url
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from schema import And
from schema import Schema
from schema import Use
import json
import requests
import unittest


class TestCommonEndpoints(unittest.TestCase):

    def setUp(self):
        self.url = api_url
        self.endpoints = "/"
        # Ignore warning messages on insecure requests
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    @staticmethod
    def _get_endpoint_list_schema():
        return Schema({
            "endpoints":
                [{
                    "methods": [
                        And(str, Use(str.upper), lambda s: s in (
                            "GET", "POST", "DELETE", "PUT"))
                    ],
                    "endpoint":
                        And(Use(str))
                }]
        })

    def test_api_endpoints(self):
        response = requests.get(
            "{0}{1}".format(self.url, self.endpoints),
            headers={"User-Agent": "curl"},
            verify=False)
        response_text = response.content.decode("utf-8")
        response_ds = json.loads(response_text)
        # Check proper code returned
        self.assertEqual(200, response.status_code)
        # Check proper content returned
        val_con = self._get_endpoint_list_schema().\
            validate(response_ds)
        self.assertTrue(response_ds == val_con)
