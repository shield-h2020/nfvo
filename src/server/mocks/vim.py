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


class MockVim:

    def __init__(self):
        self.get_vim_list_mock = [{
            "name": "",
            "uuid": "",
        }]
        self.get_vim_img_list_mock = {
            "tenant": {
                "datacenter": [
                  {
                    "checksum": "",
                    "container_format": "",
                    "created_at": "",
                    "disk_format": "",
                    "file": "",
                    "id": "",
                    "min_disk": 0,
                    "min_ram": 0,
                    "name": "",
                    "owner": "",
                    "protected": False,
                    "schema": "",
                    "size": 0,
                    "status": "",
                    "tags": [],
                    "updated_at": "",
                    "virtual_size": "",
                    "visibility": ""
                  }
                ]
            }
        }
        self.register_vdu_mock = {}

    def get_vim_list_schema(self):
        schema_conf = self.get_vim_list_mock
        schema_conf[0]["name"] = And(Use(str))
        schema_conf[0]["uuid"] = And(Use(str))
        schema = schema_conf
        return Schema(schema)

    def get_vim_img_list_schema(self):
        schema = {
            And(Use(str)): {
                And(Use(str)): [
                    {
                        "checksum": And(Use(str)),
                        "container_format": And(Use(str)),
                        "created_at": And(Use(str)),
                        "disk_format": And(Use(str)),
                        "file": And(Use(str)),
                        "id": And(Use(str)),
                        "min_disk": And(Use(int)),
                        "min_ram": And(Use(int)),
                        "name": And(Use(str)),
                        "owner": And(Use(str)),
                        "protected": And(Use(bool)),
                        "schema": And(Use(str)),
                        "size": And(Use(int)),
                        "status": And(Use(str)),
                        "tags": And(Use(list)),
                        "updated_at": And(Use(str)),
                        "virtual_size": And(Use(str)),
                        "visibility": And(Use(str)),
                    }
                ]
            }
        }
        return Schema(schema)

    def register_vdu_schema(self):
        schema_conf = self.register_vdu_mock
        schema = schema_conf
        return Schema(schema)
