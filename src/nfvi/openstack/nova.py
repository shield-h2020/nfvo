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


from novaclient import client


class OpenStackNova:
    """
    Adaptor to connect to OpenStack's Glance service.
    Reference: https://docs.openstack.org/python-novaclient/latest/reference
    """

    def __init__(self, os_conn):
        self.NOVA_VERSION = "2"
        self.key_session = os_conn.key_session
        self.client = client.Client(
                self.NOVA_VERSION, session=self.key_session)

    def get_servers(self):
        return self.client.servers.list()

    def get_server_interfaces(self, server):
        return self.client.servers.interface_list(server)

    def get_hypervisors(self):
        return self.client.hypervisors.list()
