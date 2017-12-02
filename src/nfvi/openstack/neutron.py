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


from neutronclient.v2_0 import client


class OpenStackNeutron:
    """
    Adaptor to connect to OpenStack's Neutron service.
    Reference: https://docs.openstack.org/python-neutronclient/latest/reference
    """

    def __init__(self, os_conn):
        self.key_session = os_conn.key_session
        self.client = client.Client(session=self.key_session)

    def get_networks(self):
        return self.client.list_networks().get("networks", [])
