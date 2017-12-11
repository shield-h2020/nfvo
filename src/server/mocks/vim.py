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


class MockVim:

    def __init__(self):
        self.res_key = "vim"
        self.get_vim_list_mock = {
            self.res_key: [
                {
                    "name": "openstack-vim1",
                    "uuid": str(uuid.uuid1()),
                }
            ]
        }
        r_uuid4 = str(uuid.uuid4())
        self.get_vim_img_list_mock = {
            self.res_key: [
                {
                    And(Use(str)): {
                        And(Use(str)): [
                          {
                            "checksum": "",
                            "container_format": "",
                            "created_at": "2017-01-01T00:00:01Z",
                            "disk_format": "",
                            "file": "/v2/images/{}/file".format(r_uuid4),
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
            ]
        }
        self.register_vdu_mock = {}

    def get_vim_list_schema(self):
        schema = self.get_vim_list_mock
        for schema_conf in schema.get(self.res_key):
            schema_conf["name"] = And(Use(str))
            schema_conf["uuid"] = And(Use(str),
                                      lambda n: regex.uuid(n, 1) is not None)
        return Schema(schema)

    def get_vim_img_list_schema(self):
        schema = self.get_vim_img_list_mock
        for schema_conf in schema.get(self.res_key):
            schema_conf2 = list(schema_conf.values())[0]
            schema_conf3 = list(schema_conf2.values())[0][0]
            schema_conf3[Optional("base_image_ref")] = And(
                Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf3[Optional("boot_roles")] = And(Use(str))
            schema_conf3["checksum"] = And(Use(str))
            schema_conf3["container_format"] = And(Use(str))
            schema_conf3["created_at"] = And(
                Use(str), lambda n: regex.rfc3399(n) is not None)
            schema_conf3["disk_format"] = And(Use(str))
            schema_conf3["file"] = And(
                Use(str), lambda n: regex.unix_path(n) is not None)
            schema_conf3["id"] = And(
                Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf3[Optional("image_location")] = And(Use(str))
            schema_conf3[Optional("image_state")] = And(Use(str))
            schema_conf3[Optional("image_type")] = And(Use(str))
            schema_conf3[Optional("instance_uuid")] = And(
                Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf3[Optional("kernel_id")] = And(
                Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf3["min_disk"] = And(Use(int))
            schema_conf3["min_ram"] = And(Use(int))
            schema_conf3["name"] = And(Use(str))
            schema_conf3["owner"] = And(Use(str))
            schema_conf3[Optional("owner_id")] = And(Use(str))
            schema_conf3["protected"] = And(Use(str))
            schema_conf3[Optional("ramdisk_id")] = And(
                Use(str), lambda n: regex.uuid4(n) is not None)
            schema_conf3["schema"] = And(Use(str))
            schema_conf3["size"] = And(Use(int))
            schema_conf3["status"] = And(Use(str))
            schema_conf3["tags"] = And(Use(list))
            schema_conf3["tags"] = And(Use(list))
            schema_conf3["updated_at"] = And(
                Use(str), lambda n: regex.rfc3399(n) is not None)
            schema_conf3[Optional("user_id")] = And(Use(str))
            schema_conf3["virtual_size"] = And(Use(str))
            schema_conf3["visibility"] = And(
                Use(str), lambda s: s in ("public", "private"))
        return Schema(schema)

    def register_vdu_schema(self):
        schema_conf = self.register_vdu_mock
        schema = schema_conf
        return Schema(schema)
