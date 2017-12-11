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


from core import regex
from schema import And
from schema import Schema
from schema import Use

import uuid


class MockVnsf:

    def __init__(self):
        self.res_key = "vnsf"
        self.get_vnfr_config_mock = {
            self.res_key: [
                {
                    "charm": "mspl_charm",
                    "description": "Generated by OSM package generator",
                    "ns_name": "cirros_2vnf_nsd",
                    "vendor": "OSM",
                    "version": "1.0",
                }
            ]
        }
        self.get_vnfr_running_mock = {
            self.res_key: [
                {
                    "config_status": "configuring",
                    "ip": "10.11.12.13",
                    "ns_id": str(uuid.uuid4()),
                    "ns_name": "cirros_2vnf_nsd",
                    "operational_status": "running",
                    "vendor": "OSM",
                    "vim": "openstack-vim1",
                    "vnf_id": str(uuid.uuid4()),
                    "vnf_name": "vnf_name__cirros_2vnfd__1",
                }
            ]
        }
        self.exec_action_on_vnf_mock = {}

    def get_vnfr_config_schema(self):
        schema = self.get_vnfr_config_mock
        for schema_conf in schema.get(self.res_key):
            schema_conf["charm"] = And(Use(str))
            schema_conf["description"] = And(Use(str))
            schema_conf["ns_name"] = And(Use(str))
            schema_conf["vendor"] = And(Use(str))
            schema_conf["version"] = And(Use(str))
        return Schema(schema)

    def get_vnfr_running_schema(self):
        schema = self.get_vnfr_running_mock
        for schema_conf in schema.get(self.res_key):
            schema_conf["config_status"] = And(Use(str))
            schema_conf["ip"] = And(Use(str))
            schema_conf["ns_id"] = \
                And(Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf["ns_name"] = And(Use(str))
            schema_conf["operational_status"] = And(Use(str))
            schema_conf["vendor"] = And(Use(str))
            schema_conf["vim"] = And(Use(str))
            schema_conf["vnf_id"] = \
                And(Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf["vnf_name"] = And(Use(str))
        return Schema(schema)

    def exec_action_on_vnf_schema(self):
        schema = self.exec_action_on_vnf_mock
        return Schema(schema)
