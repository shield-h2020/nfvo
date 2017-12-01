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


from nfvo.osm import endpoints as osm_eps

import json
import requests


def get_vim_name_by_uuid(vim_list, uuid):
    for dc in vim_list:
        if dc.get("uuid") == uuid:
            return dc.get("name")
    return ""


def get_vim_list():
    resp = requests.get(
            osm_eps.VIM_LIST_O,
            headers=osm_eps.get_default_headers(),
            verify=False)
    output = json.loads(resp.text)
    output = output.get("collection") \
                   .get("rw-launchpad:datacenters")[0] \
                   .get("ro-accounts")[0] \
                   .get("datacenters")
    return output
