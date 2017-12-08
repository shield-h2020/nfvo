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


class MockVim:

    def __init__(self):
        self.get_vim_list_mock = [
            {
                "name": "openstack-vim1",
                "uuid": str(uuid.uuid4()),
            }
        ]
        self.get_vim_img_list_mock = {
            "tenant": {
                "datacenter": [
                  {
                    "checksum": "",
                    "container_format": "",
                    "created_at": "2017-01-01T00:00:01Z",
                    "disk_format": "",
                    "file": "/v2/images/4acfc0ea-80f1-7c0e7557f911/file",
                    "id": str(uuid.uuid4()),
                    "min_disk": 0,
                    "min_ram": 0,
                    "name": "",
                    "owner": "",
                    "protected": "false",
                    "schema": "",
                    "size": 0,
                    "status": "",
                    "tags": [],
                    "updated_at": "2017-05-29T11:26:44Z",
                    "virtual_size": "",
                    "visibility": "public"
                  }
                ]
            }
        }
        self.register_vdu_mock = {}

    def get_vim_list_schema(self):
        schema = self.get_vim_list_mock
        for schema_conf in schema:
            schema_conf["name"] = And(Use(str))
            schema_conf["uuid"] = And(Use(str),
                                      lambda n: regex.uuid4(n) is not None)
        return Schema(schema)

    def get_vim_img_list_schema(self):
        schema = {
            And(Use(str)): {
                And(Use(str)): [
                    {
                        "checksum": And(Use(str)),
                        "container_format": And(Use(str)),
                        "created_at": And(
                            Use(str), lambda n: regex.rfc3399(n) is not None),
                        "disk_format": And(Use(str)),
                        "file": And(Use(str),
                                    lambda n: regex.unix_path(n) is not None),
                        "id": And(Use(str),
                                  lambda n: regex.uuid4(n) is not None),
                        "min_disk": And(Use(int)),
                        "min_ram": And(Use(int)),
                        "name": And(Use(str)),
                        "owner": And(Use(str)),
                        "protected": And(Use(str)),
                        "schema": And(Use(str)),
                        "size": And(Use(int)),
                        "status": And(Use(str)),
                        "tags": And(Use(list)),
                        "updated_at": And(
                            Use(str), lambda n: regex.rfc3399(n) is not None),
                        "virtual_size": And(Use(str)),
                        "visibility": And(Use(str),
                                          lambda s: s in ("public", "private"))
                    }
                ]
            }
        }
        return Schema(schema)

    def register_vdu_schema(self):
        schema_conf = self.register_vdu_mock
        schema = schema_conf
        return Schema(schema)
