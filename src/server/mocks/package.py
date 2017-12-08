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


class MockPackage:

    def __init__(self):
        self.onboard_package_mock = {
            "package": "/opt/osm_pkg/cirros_vnf.tar.gz",
            "transaction_id": str(uuid.uuid4()),
        }
        self.onboard_package_remote_mock = {
            "path": "/opt/osm_pkg/cirros_vnf.tar.gz",
        }
        self.remove_package_mock = {
            "package": "cirros_vnfd",
        }

    def onboard_package_schema(self):
        schema_conf = self.onboard_package_mock
        schema_conf["package"] = \
            And(Use(str), lambda n: regex.unix_path(n) is not None)
        schema_conf["transaction_id"] = \
            And(Use(str), lambda n: regex.uuid4(n) is not None)
        schema = schema_conf
        return Schema(schema)

    def onboard_package_remote_schema(self):
        schema_conf = self.onboard_package_remote_mock
        schema_conf["path"] = \
            And(Use(str), lambda n: regex.unix_path(n) is not None)
        schema = schema_conf
        return Schema(schema)

    def remove_package_schema(self):
        schema_conf = self.remove_package_mock
        schema_conf["package"] = And(Use(str))
        schema = schema_conf
        return Schema(schema)
