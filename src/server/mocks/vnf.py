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


class MockVnfs:

    def __init__(self):
        self.get_vnfr_config_mock = [{
            "charm": "",
            "description": "",
            "ns_name": "",
            "vendor": "",
            "version": "",
        }]
        self.get_vnfr_running_mock = {}
        self.exec_action_on_vnf_mock = {}

    def get_vnfr_config_schema(self):
        schema_conf = self.get_vnfr_config_mock
        schema_conf[0]["charm"] = And(Use(str))
        schema_conf[0]["description"] = And(Use(str))
        schema_conf[0]["ns_name"] = And(Use(str))
        schema_conf[0]["vendor"] = And(Use(str))
        schema_conf[0]["version"] = And(Use(str))
        schema = schema_conf
        return Schema(schema)

    def get_vnfr_running_schema(self):
        schema = self.get_vnfr_running_mock
        return Schema(schema)

    def exec_action_on_vnf_schema(self):
        schema = self.exec_action_on_vnf_mock
        return Schema(schema)
