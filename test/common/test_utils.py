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
from unittest import TestCase

import json
import requests
import requests_mock


class TestUtils:

    def __init__(self):
        self.url_base = api_url
        self.test = TestCase()
        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount("mock", self.adapter)
        # Ignore warning messages on insecure requests
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def format_endpoint(self, endpoint):
        if not endpoint.startswith("http"):
            url = "{0}{1}".format(self.url_base, endpoint)
        else:
            url = endpoint
        url = url[:-1] if url.endswith("/") else url
        return url

    def check_output(self, response, schema, exp_code, exp_out):
        if exp_code is None:
            exp_code = response.status_code
        # Check proper code returned
        self.test.assertEqual(exp_code, response.status_code)
        if exp_out is None:
            # Avoid simple commas, json will not load properly
            exp_out = response.content.decode("utf-8")
        if isinstance(exp_out, str):
            exp_out = exp_out.replace("'", "\"")
            exp_out = json.loads(exp_out)
        # Check proper content returned
        val_con = getattr(schema, "validate")(exp_out)
        self.test.assertEqual(exp_out, val_con,
                              "Unexpected output structure")

    def test_get(self, url, schema, exp_code=None, exp_out=None):
        url = self.format_endpoint(url)
        response = requests.get(
            url,
            headers={"User-Agent": "curl"},
            verify=False)
        self.check_output(response, schema, exp_code, exp_out)

    def test_mocked_get(self, url, schema, exp_code, exp_out):
        url = self.format_endpoint(url)
        self.adapter.register_uri(
            "GET", url, status_code=200,
            text=str(exp_out)
        )
        with requests_mock.mock(real_http=True) as m:
            m.get(url, text=str(exp_out))
            self.test_get(url, schema, exp_code, exp_out)

    def test_post(self, url, schema, data, exp_code=None, exp_out=None):
        url = self.format_endpoint(url)
        response = requests.post(
            url,
            headers={"User-Agent": "curl"},
            data=data,
            verify=False)
        self.check_output(response, schema, exp_code, exp_out)

    def test_mocked_post(self, url, schema, data, exp_code, exp_out):
        url = self.format_endpoint(url)
        self.adapter.register_uri(
            "POST", url, status_code=200,
            text=str(exp_out)
        )
        with requests_mock.mock(real_http=True) as m:
            m.post(url, text=str(exp_out))
            self.test_post(url, schema, data, exp_code, exp_out)
