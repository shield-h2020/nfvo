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
from json.decoder import JSONDecodeError
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from unittest import TestCase

import ast
import json
import requests
import requests_mock


class TestUtils:

    ignore_realtime = "Real-time test"
    ignore_hazard = "Do not run remotely"

    def __init__(self):
        self.url_base = api_url
        self.test = TestCase()
        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount("mock", self.adapter)
        # Ignore warning messages on insecure requests
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def __format_endpoint(self, endpoint):
        if not endpoint.startswith("http"):
            url = "{0}{1}".format(self.url_base, endpoint)
        else:
            url = endpoint
        url = url[:-1] if url.endswith("/") else url
        return url

    def __set_url_headers(self, url, headers):
        url = self.__format_endpoint(url)
        headers_inner = {"User-Agent": "curl"}
        headers_inner.update(headers)
        return [url, headers_inner]

    def __check_output(self, response, schema_re, exp_code=None, exp_out=None):
        if exp_code is None:
            exp_code = response.status_code
        # Check proper code returned
        self.test.assertEqual(exp_code, response.status_code)
        if exp_out is None:
            # Avoid simple commas, json will not load properly
            exp_out = response.content.decode("utf-8")
        error = False
        if isinstance(exp_out, str):
            try:
                exp_out = exp_out.replace("'", "\"")
                exp_out = json.loads(exp_out)
                # Detect error output
                if not isinstance(exp_out, list):
                    error = "error" in exp_out.keys()
            # Detect decoding error
            except JSONDecodeError:
                try:
                    exp_out = ast.literal_eval(exp_out)
                except Exception:
                    error = True
        if not error:
            # Check proper content returned (exception raised if wrong)
            getattr(schema_re, "validate")(exp_out)
            # self.test.assertEqual(exp_out, val_con,
            #                       "Unexpected output structure")

    def test_get(self, url, schema, headers={}, exp_code=None, exp_out=None):
        url, headers_inner = self.__set_url_headers(url, headers)
        response = requests.get(
            url,
            headers=headers_inner,
            verify=False)
        self.__check_output(response, schema, exp_code, exp_out)

    def test_mocked_get(self, url, schema, headers, exp_code, exp_out):
        url, headers_inner = self.__set_url_headers(url, headers)
        self.adapter.register_uri(
            "GET", url, status_code=exp_code,
            request_headers=headers_inner,
            text=str(exp_out)
        )
        with requests_mock.mock(real_http=True) as m:
            m.get(url, text=str(exp_out))
            self.test_get(url, schema, headers_inner, exp_code, exp_out)

    def test_post(self, url, schema, data, headers={},
                  exp_code=None, exp_out=None):
        url, headers_inner = self.__set_url_headers(url, headers)
        response = requests.post(
            url,
            headers=headers_inner,
            # data=data if "json" not in headers_inner else {},
            json=data if "json" in headers_inner else {},
            files=data if "multipart" in headers_inner else {},
            verify=False)
        self.__check_output(response, schema, exp_code, exp_out)

    def test_mocked_post(self, url, schema, data, headers, exp_code, exp_out):
        url, headers_inner = self.__set_url_headers(url, headers)
        self.adapter.register_uri(
            "POST", url, status_code=exp_code,
            request_headers=headers_inner,
            text=str(exp_out)
        )
        with requests_mock.mock(real_http=True) as m:
            m.post(url, text=str(exp_out))
            self.test_post(url, schema, data, headers_inner,
                           exp_code, exp_out)

    def test_delete(self, url, schema, headers={},
                    exp_code=None, exp_out=None):
        url, headers_inner = self.__set_url_headers(url, headers)
        response = requests.delete(
            url,
            headers=headers_inner,
            verify=False)
        self.__check_output(response, schema, exp_code, exp_out)

    def test_mocked_delete(self, url, schema, headers, exp_code, exp_out):
        url, headers_inner = self.__set_url_headers(url, headers)
        self.adapter.register_uri(
            "DELETE", url, status_code=exp_code,
            request_headers=headers_inner,
            text=str(exp_out)
        )
        with requests_mock.mock(real_http=True) as m:
            m.delete(url, text=str(exp_out))
            self.test_delete(url, schema, headers_inner, exp_code, exp_out)
