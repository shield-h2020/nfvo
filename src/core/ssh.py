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


import paramiko
from Crypto import Random


class SshSession(object):

    def __init__(self, *args, **kwargs):
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.user = kwargs["user"]
        self.password = kwargs["password"]
        self.client = self.__create_client()

    def __create_client(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Re-initialise RNG upon fork to avoid connectivity issues
        Random.atfork()
        client.connect(self.host, username=self.user,
                       port=self.port, password=self.password)
        return client

    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
