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
        self.get_nsr_config_mock = [{
            "ns": {
                "config_status": "configured",
                "name": "cirros_2vnf_nsd",
                "ns_id": "cirros_2vnf_nsd",
                "vendor_id": "OSM"
            }
        }]

    def get_nsr_config_schema(self):
        schema = self.get_nsr_config_mock
        for schema_conf in schema:
            schema_conf = schema_conf.get("ns")
            schema_conf["config_status"] = And(Use(str))
            schema_conf["name"] = And(Use(str))
            schema_conf["ns_id"] = And(Use(str))
            schema_conf["vendor_id"] = And(Use(str))
        return Schema(schema)
