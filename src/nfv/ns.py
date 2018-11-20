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
from server.http import content
from server.mocks.ns import MockNs as ns_m


class VnsfoNs:

    def __init__(self):
        self.orchestrator = OSMR2()

    @content.on_mock(ns_m().get_nsr_config_mock)
    def get_nsr_config(self, ns_name=None):
        return self.orchestrator.get_ns_descriptors(ns_name)

    @content.on_mock(ns_m().get_nsr_running_mock)
    def get_nsr_running(self, instance_id=None):
        return self.orchestrator.get_ns_instances(instance_id)

    @content.on_mock(ns_m().post_nsr_instantiate_mock)
    def instantiate_ns(self, instantiation_data):
        return self.orchestrator.post_ns_instance(instantiation_data)

    @content.on_mock(ns_m().delete_nsr_mock)
    def delete_ns(self, instance_id):
        return self.orchestrator.delete_ns_instance(instance_id)

    def fetch_config_nss(self):
        catalog = self.get_nsr_config()
        return catalog
