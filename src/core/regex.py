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


from uuid import UUID

import re


def uuid(data, uuid_version=None):
    try:
        version = UUID(data).version
    except ValueError:
        return None
    if uuid_version is None:
        # If no version is provided, match any
        return data
    if uuid_version == version:
        return data
    return None


def uuid4(data):
    return uuid(data, 4)


def unix_path(data):
    path_re = re.compile("^['\"]?(?:\/[^\/]*)*['\"]?$")
    return path_re.match(data)


def rfc3399(data):
    date_re = re.compile("^\d{4}-\d{2}-\d{2}T(\d{2}(:?))*.\d{2}Z$")
    return date_re.match(data)
