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


from schema import And
from schema import Schema
from schema import Use


class MockEndpoints:

    def __init__(self):
        self.get_api_endpoints_mock = {
            "endpoints":
                [{
                    "methods": ["GET"],
                    "endpoint": "/",
                }]
        }

    def get_api_endpoints_schema(self):
        schema = self.get_api_endpoints_mock
        schema_ep = schema.get("endpoints")[0]
        schema_ep["methods"] = [
            And(str, Use(str.upper), lambda s: s in (
                "GET", "POST", "DELETE", "PUT"))
        ]
        schema_ep["endpoint"] = \
            And(Use(str))
        return Schema(schema)
