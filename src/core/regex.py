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


import re


def uuid(uuid_version, data):
    transaction_id_re = re.compile((
        ("[a-f0-9]{8}-[a-f0-9]{4}-<version>[a-f0-9]{3}-" +
         "[89ab][a-f0-9]{3}-[a-f0-9]{12}$")
        .replace("<version>", str(uuid_version))))
    return transaction_id_re.match(data)


def uuid4(data):
    return uuid(4, data)


def unix_path(data):
    path_re = re.compile("^['\"]?(?:\/[^\/]*)*['\"]?$")
    return path_re.match(data)


def rfc3399(data):
    date_re = re.compile("^\d{4}-\d{2}-\d{2}T(\d{2}(:?))*.\d{2}Z$")
    return date_re.match(data)
