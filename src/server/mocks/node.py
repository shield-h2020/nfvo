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
from schema import Optional
from schema import Schema
from schema import Use

import uuid


class MockNode:

    def __init__(self):
        self.res_key = "node"
        self.post_node_mock = {
            "node_id": str(uuid.uuid4())
        }

    def post_node_schema(self):
        schema = self.post_node_mock
        schema["node_id"] = And(Use(str))
        return Schema(schema)

    def get_node_schema(self):
        schema = self.post_node_mock
        schema["host_name"] = And(Use(str))
        schema["node_id"] = And(Use(str))
        schema["analysis_type"] = And(Use(str))
        schema["distribution"] = And(Use(str))
        schema["ip_address"] = And(Use(str))
        schema["pcr0"] = And(Use(str))
        schema["status"] = And(Use(str))
        schema["driver"] = And(Use(str))
        schema["timestamp"] = Optional(Use(str))
        schema["configuration"] = Optional(Use(str))
        return Schema(schema)
