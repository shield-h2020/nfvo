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


# from core.ssh import SshSession
from core.process import ProcessCommand
from keystoneauth1 import session
from keystoneauth1.identity import v2
import re


class OpenStackConnector:

    def __init__(self, **kwargs):
        """
        Constructor to gather connection details for OpenStack.
        If no arguments for OpenStack are provided, these will be
        fetched from OSM DB.
        If no arguments for OSM are provided, these will be
        fetched from vNSFO conf.
        In any case, the OSM datacenter must be provided.
        Expected input:
        {
            "openstack": {
                "user": "tenant_user",
                "password": "tenant_pass",
                "auth_url": "http://127.0.0.1:5000/v2.0",
                "tenant": "shield",
            },
            "osm: {
                "host": "127.0.0.1",
                "port": "22",
                "user": "osm_host_user",
                "password": "osm_host_pass",
                "datacenter": "dc1",
            }
        }
        """
        if "osm" not in kwargs:
            return
        if "datacenter" not in kwargs.get("osm"):
            return
        osm_details = kwargs.get("osm")
        dc_uuid = osm_details.get("datacenter")
        os_params = []
        if "openstack" in kwargs:
            os_details = kwargs.get("openstack")
            user = os_details.get("user")
            password = os_details.get("password")
            auth_url = os_details.get("auth_url")
            tenant = os_details.get("tenant")
            os_params = [user, password, auth_url, tenant]
        if len(os_params) != 4:
            self.InitEmpty(dc_uuid)
            os_params = [self.os_user, self.os_password,
                         self.os_auth_url, self.os_tenant]
        self.InitCredentials(*os_params)

    @classmethod
    def InitCredentials(self, user, passwd, url, tenant):
        self.os_user = user
        self.os_password = passwd
        self.os_auth_url = url
        self.os_tenant = tenant
        self.auth = v2.Password(
                username=self.os_user, password=self.os_password,
                tenant_name=self.os_tenant, auth_url=self.os_auth_url)
        self.key_session = session.Session(auth=self.auth)

    @classmethod
    def InitEmpty(self, dc_uuid):
        dc_raw = OpenStackConnector.__get_vim_credentials(dc_uuid)
        dc = OpenStackConnector.__parse_vim_credentials(dc_raw).get(dc_uuid)
        self.os_user = dc.get("user")
        self.os_password = dc.get("passwd")
        self.os_auth_url = dc.get("vim_url")
        self.os_tenant = dc.get("vim_tenant_name")

    @staticmethod
    def __get_vim_credentials(dc_uuid=None):
        mysql_command = "SELECT D.uuid, D.vim_url, D.config, T.config, \
                         T.vim_tenant_name, T.user, T.passwd FROM \
                         datacenters AS D, datacenter_tenants as T \
                         WHERE D.uuid = T.datacenter_id"
        # When a specific VIM/DC is provided, it will be filtered
        if dc_uuid is not None:
            mysql_command += " AND D.uuid = '{}'".format(dc_uuid)
        mysql_command += ";"
        lxc_command = "lxc exec RO -- mysql mano_db -e \"{}\""\
                      .format(mysql_command)
        lxc_command = re.sub(r"\s{1,}", " ", lxc_command)
        # ssh_params = {"host": "***", "user": "***",
        #               "port": int("22"), "password": "***"}
        # ssh_session = SshSession(**ssh_params)
        # sin, sout, serr = ssh_session.execute(lxc_command)
        # ssh_command = "ssh -A {}@{} '{}'"\
        #     .format(ssh_params["host"], ssh_params.get("host"), lxc_command)
        sout = ProcessCommand.execute(lxc_command)
        return sout

    @staticmethod
    def __parse_vim_credentials(raw_data):
        # Parse header titles (to know which value is under process)
        table_head_split = raw_data.split("\n")
        table_head = table_head_split[0]
        table_head = re.sub(r"config", "", table_head)
        table_head_split = table_head.split()

        # Parse each content entry (login data for datacenters)
        table_content = raw_data.replace(table_head, "")
        reg = "^([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}" + \
              "-[89ab][0-9a-f]{3}-[0-9a-f]{12}).*"
        reg = re.compile(reg, re.MULTILINE)
        uuids = re.findall(reg, table_content)
        dc_data_int = {}
        for uuid in reversed(uuids):
            # Retrieve from last position to 1st appearance of index
            dc_data_idx = table_content.index(uuid)
            dc_data = table_content[dc_data_idx:len(table_content)]
            # Remove options (within dictionaries or empty) -- and any newline
            dc_data_int[uuid] = re.sub(r"(?is){.+}", "", dc_data)
            dc_data_int[uuid] = dc_data_int[uuid].replace("NULL", "")
            dc_data_int[uuid] = re.sub(r"(\\)+n", "", dc_data_int[uuid])
            table_content = table_content.replace(dc_data, "")

        # Define new structure with details per DC
        dc_data_det = {}
        for dc, dc_data in dc_data_int.iteritems():
            dc_data_det[dc] = {}
            dc_data_split = dc_data.split()
            for n, head in enumerate(table_head_split):
                dc_data_det[dc][head] = dc_data_split[n]
        return dc_data_det
