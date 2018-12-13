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


from nfvo.osm.osm_r2 import OSMR2
from nfvo.osm.osm_r4 import OSMR4
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from server.http import content
from server.mocks.vnf import MockVnsf as vnfs_m

import requests


class VnsfoVnsf:

    def __init__(self, release=None):
        self.orchestrator = OSMR2()
        if release == 4:
            self.orchestrator = OSMR4()
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    @content.on_mock(vnfs_m().get_vnfr_config_mock)
    def get_vnfr_config(self):
        return self.orchestrator.get_vnf_descriptors()

    @content.on_mock(vnfs_m().get_vnfr_running_mock)
    def get_vnfr_running(self):
        return self.orchestrator.get_vnf_instances()

    @content.on_mock(vnfs_m().exec_action_on_vnf_mock)
    def exec_action_on_vnf(self, payload):
        return self.orchestrator.exec_action_on_vnf(payload)

    @content.on_mock(vnfs_m().exec_action_on_vnf_mock)
    def submit_action_request(self, vnfr_id=None, action=None, params=list()):
        payload = {"vnfr_id": vnfr_id,
                   "action": action,
                   "params": params}
        return self.orchestrator.exec_action_on_vnf(payload)
