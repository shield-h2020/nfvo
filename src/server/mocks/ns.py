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
from schema import Optional
from schema import Schema
from schema import Use

import uuid


class MockNs:

    def __init__(self):
        self.res_key = "ns"
        self.get_nsr_config_mock = {
            self.res_key: [
                {
                    "constituent_vnfs": [
                        {
                            "member-vnf-index": And(Use(int)),
                            "start-by-default":
                            And(Use(str), lambda s: s in ("true", "false")),
                            "vnfd-id-ref": And(Use(str))
                        }
                    ],
                    "description": And(Use(str)),
                    "ns_name": And(Use(str)),
                    "vendor": And(Use(str)),
                    "version": And(Use(str)),
                    "vld": [
                        {
                            "id": And(Use(str)),
                            "mgmt-network":
                            And(Use(str), lambda s: s in ("true", "false")),
                            "name": And(Use(str)),
                            "short-name": And(Use(str)),
                            "type": And(Use(str)),
                            Optional("vim-network-name"): And(Use(str)),
                            "vnfd-connection-point-ref": [
                                {
                                    "member-vnf-index-ref": And(Use(int)),
                                    "vnfd-connection-point-ref": And(Use(str)),
                                    "vnfd-id-ref": And(Use(str))
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.post_nsr_instantiate_mock = {
            "instance_name": "my service instance",
            "ns_name": "l23filter_nsd",
            "vim_id": str(uuid.uuid4()),
            "vim_net": "provider"
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
            for schema_vld in schema.get("vld", []):
                schema_vld["id"] = And(Use(str))
                schema_vld["mgmt-network"] = \
                    And(Use(str), lambda s: s in ("true", "false"))
                schema_vld["name"] = And(Use(str))
                schema_vld["short-name"] = And(Use(str))
                schema_vld["type"] = And(Use(str))
                schema_vld[Optional("vim-network-name")] = And(Use(str))
                for schema_vld_ref in schema_vld.\
                        get("vnfd-connection-point-ref", []):
                    schema_vld_ref["member-vnf-index-ref"] = And(Use(int))
                    schema_vld_ref["vnfd-connection-point-ref"] = And(Use(str))
                    schema_vld_ref["vnfd-id-ref"] = And(Use(str))
        return Schema(schema)

    def post_nsr_instantiate_schema(self):
        schema = self.post_nsr_instantiate_mock
        schema["instance_name"] = And(Use(str))
        schema["ns_name"] = And(Use(str))
        schema["vim_id"] = \
            And(Use(str), lambda n: regex.uuid4(n) is not None)
        schema["vim_net"] = And(Use(str))
        return Schema(schema)
