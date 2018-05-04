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
                            Optional("description"): And(Use(str)),
                            Optional("vendor"): And(Use(str)),
                            Optional("version"): And(Use(str)),
                            Optional("ip-profile-ref"): And(Use(str)),
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
            "instance_id": str(uuid.uuid4()),
            "result": "success",
            "vim_id": str(uuid.uuid4())
        }

        self.delete_nsr_mock = {
            "action": "delete",
            "instance_id": str(uuid.uuid4()),
            "result": "success"
        }

        self.get_nsr_running_mock = {
            self.res_key: [
                {
                    "config_status": "configured",
                    "constituent_vnf_instances": [
                        {
                            "config_jobs": [
                                {
                                    "create_time": 1523980234,
                                    "job_id": 1,
                                    "job_status": "success",
                                    "primitives": [
                                        {
                                            "execution_id":
                                            "action-aab4f318-cdcb",
                                            "execution_status": "success",
                                            "name": "set-policies"
                                        }
                                    ],
                                    "triggered_by": "vnf-primitive"
                                }
                            ],
                            "config_status": "configuring",
                            "ip": "10.101.20.52",
                            "ns_id": "d75efa2d-b4d4-42a3-9bcb-20324f7d8e47",
                            "ns_name": "fl7f_test25",
                            "operational_status": "running",
                            "vendor": "POLITO",
                            "vim": "openstack-orion",
                            "vnf_id": "6c358c6b-2807-4988-826e-6c601e674e0d",
                            "vnf_name": "fl7f_test25__fl7filter_vnfd__1"
                        }
                    ],
                    "instance_id": "d75efa2d-b4d4-42a3-9bcb-20324f7d8e47",
                    "instance_name": "fl7filter_nsd",
                    "ns_name": "fl7filter_nsd",
                    "operational_status": "running",
                    "vlrs": [
                        {
                            "vim_id": "d75efa2d-b4d4-42a3-9bcb-20324f7d8e47",
                            "vlr_id": "8cb0c418-830f-4bf6-acdc-fbccdc0b1818"
                        }
                    ]
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
            And(Use(str), lambda n: regex.uuid(n) is not None)
        schema["instance_id"] = \
            And(Use(str), lambda n: regex.uuid(n) is not None)
        schema["result"] = And(Use(str))
        return Schema(schema)

    def delete_nsr_schema(self):
        schema = self.delete_nsr_mock
        schema["action"] = And(Use(str))
        schema["result"] = And(Use(str))
        schema["instance_id"] = \
            And(Use(str), lambda n: regex.uuid4(n) is not None)
        return Schema(schema)

    def get_nsr_running_schema(self):
        schema = self.get_nsr_running_mock
        for running_ns in schema[self.res_key]:
            running_ns["config_status"] = And(Use(str))
            running_ns["instance_id"] = \
                And(Use(str), lambda n: regex.uuid4(n) is not None)
            running_ns["instance_name"] = And(Use(str))
            running_ns["ns_name"] = And(Use(str))
            running_ns["operational_status"] = And(Use(str))
            for vlr in running_ns["vlrs"]:
                vlr["vim_id"] = And(Use(str))
                vlr["vlr_id"] = \
                    And(Use(str), lambda n: regex.uuid4(n) is not None)
            for vnf in running_ns["constituent_vnf_instances"]:
                for config_job in vnf["config_jobs"]:
                    config_job["create_time"] = And(Use(int))
                    config_job["job_id"] = And(Use(int))
                    config_job["job_status"] = And(Use(str))
                    config_job["triggered_by"] = And(Use(str))
                    for primitive in config_job["primitives"]:
                        primitive["execution_id"] = And(Use(str))
                        primitive["execution_status"] = And(Use(str))
                        primitive["name"] = And(Use(str))
                vnf["config_status"] = And(Use(str))
                vnf["ip"] = And(Use(str))
                vnf["vnf_id"] = \
                    And(Use(str), lambda n: regex.uuid4(n) is not None)
                vnf["ns_id"] = \
                    And(Use(str), lambda n: regex.uuid4(n) is not None)
                vnf["ns_name"] = And(Use(str))
                vnf["operational_status"] = And(Use(str))
                vnf["vendor"] = And(Use(str))
                vnf["vim"] = And(Use(str))
                vnf["vnf_name"] = And(Use(str))
        return Schema(schema)
