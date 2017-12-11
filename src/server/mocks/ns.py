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


class MockNs:

    def __init__(self):
        self.res_key = "ns"
        self.get_nsr_config_mock = {
            self.res_key: [
                {
                    "constituent_vnfs": [
                        {
                            "member-vnf-index": 1,
                            "start-by-default": "true",
                            "vnfd-id-ref": "cirros_vnfd_v1_2"
                        }
                    ],
                    "description": "Generated by OSM package generator",
                    "ns_name": "cirros_2vnf_nsd",
                    "vendor": "OSM",
                    "version": "1.0"
                }
            ]
        }

    def get_nsr_config_schema(self):
        schema = self.get_nsr_config_mock
        for schema_conf in schema.get(self.res_key):
            for schema_const in schema_conf.get("constituent_vnfs"):
                schema_const["member-vnf-index"] = And(Use(int))
                schema_const["start-by-default"] = \
                    And(Use(str), lambda s: s in ("true", "false"))
                schema_const["vnfd-id-ref"] = And(Use(str))
            schema_conf["description"] = And(Use(str))
            schema_conf["ns_name"] = And(Use(str))
            schema_conf["vendor"] = And(Use(str))
            schema_conf["version"] = And(Use(str))
        return Schema(schema)
