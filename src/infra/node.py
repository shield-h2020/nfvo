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

from bson import ObjectId
from bson.errors import InvalidId
from core.exception import Exception as ShieldException
from core.exception import HttpCode
from core.exception import ExceptionCode as ShieldExceptionCode
from core.log import setup_custom_logger
from db.models.infra.node import Node as NodeModel
from db.models.auth.auth import PasswordAuth
from db.models.isolation.isolation_policy import InterfaceDown
from db.models.isolation.isolation_policy import DeleteFlow
from db.models.isolation.isolation_policy import OpenstackIsolation
from db.models.isolation.isolation_policy import Shutdown
from db.models.isolation.isolation_record import IsolationRecord
from io import StringIO
from jinja2 import Template
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1 import session as keystone_session
from novaclient.exceptions import MethodNotAllowed
from tm.tm_client import TMClient

import configparser
import json
import novaclient.client as nova_client
import paramiko
import random
import select
import socket
import uuid

LOGGER = setup_custom_logger(__name__)


class NodeSSHException(BaseException):
    pass


class Node:

    def __init__(self, node_id):
        try:
            nodes = NodeModel.objects(id=ObjectId(node_id))
        except InvalidId:
            nodes = NodeModel.objects(vnfr_id=node_id)
        if len(nodes) < 1:
            error_msg = "Node with id={0} not found".format(node_id)
            ShieldException.abort(HttpCode.NOT_FOUND,
                                  ShieldExceptionCode.NOT_FOUND,
                                  error_msg)
        config = configparser.ConfigParser()
        config.read("conf/isolation.conf")
        self._scripts_path = config["scripts"]["path"]
        self._shutdown_path = config["scripts"]["shutdown"]
        self._delflow_path = config["scripts"]["delflow"]
        self._ifdown_path = config["scripts"]["ifdown"]
        self._node = nodes[0]
        self._node["termination_policy"]

    def disable(self):
        self._node.disabled = True
        trust_monitor_client = TMClient()
        trust_monitor_client.delete_node(self._node.host_name)
        self._node.update(set__disabled=True)

    def delete(self):
        trust_monitor_client = TMClient()
        trust_monitor_client.delete_node(self._node.host_name)
        self._node.delete()

    def execute_commands(self, ssh, commands):
        transport = ssh.get_transport()
        stdout = ""
        stderr = ""
        for command in commands:
            channel = transport.open_session()
            channel.exec_command(command)
            while True:
                if channel.exit_status_ready():
                    break
                rl, wl, xl = select.select([channel], [], [], 0.0)
                if len(rl) > 0:
                    # Must be stdout
                    stdout = stdout + channel.recv(1024).decode("utf-8")
        return (stdout, stderr)

    def execute_shutdown(self, file_id, ssh, scp, policy):
        # Process shutdown by command template
        with open("{0}/{1}".format(self._scripts_path,
                                   self._shutdown_path)) as fhandle:
            sd_templ = Template(fhandle.read())
            commands = sd_templ.render(command=policy["command"]).splitlines()
        # Execute isolation commmands
        (stdout, stderr) = self.execute_commands(ssh, commands)
        # Store isolation record
        record = IsolationRecord(output=stdout, error=stderr)
        record.save()
        return record

    def execute_interface_down(self, file_id, ssh, scp, policy):
        # Process interface down template
        with open("{0}/{1}".format(self._scripts_path,
                                   self._ifdown_path)) as fhandle:
            sd_templ = Template(fhandle.read())
            # Get commands line by line
            commands = sd_templ.render(
                interface_name=policy["interface_name"]).splitlines()
        # Execute isolation commands
        (stdout, stderr) = self.execute_commands(ssh, commands)
        # Store isolation record
        record = IsolationRecord(output=stdout, error=stderr)
        record.save()
        return record

    def execute_delete_flow(self, file_id, ssh, scp, policy):
        # Process delete flow template
        with open("{0}/{1}".format(self._scripts_path,
                                   self._delflow_path)) as fhandle:
            sd_templ = Template(fhandle.read())
            # Send script to node and render template with policy command
            commands = sd_templ.render(
                switch=policy["switch"],
                target_filter=policy["target_filter"]).splitlines()
        # Execute isolation commands
        (stdout, stderr) = self.execute_commands(ssh, commands)
        # Store isolation record
        record = IsolationRecord(output=stdout, error=stderr)
        record.save()
        return record

    def terminate(self):
        policy = self._node["termination_policy"]
        if isinstance(policy, OpenstackIsolation):
            LOGGER.info("Openstack termination request")
            self.execute_openstack_termination()
            return
        self.isolate(terminated=True)

    def get_openstack_compute(self):
        policy = self._node["termination_policy"]
        LOGGER.info(policy["identity_endpoint"])
        LOGGER.info(policy["username"])
        LOGGER.info(policy["password"])
        LOGGER.info(policy["project_name"])
        LOGGER.info(policy["domain_name"])
        auth = v3.Password(auth_url=policy["identity_endpoint"],
                           username=policy["username"],
                           password=policy["password"],
                           project_name=policy["project_name"],
                           user_domain_name=policy["domain_name"],
                           project_domain_name=policy["domain_name"])
        version = policy["identity_endpoint"].split("/")[-1]
        if "v2" in version:
            auth = v2.Password(auth_url=policy["identity_endpoint"],
                               username=policy["username"],
                               password=policy["password"],
                               tenant_name=policy["project_name"])
        session = keystone_session.Session(auth=auth)
        compute = nova_client.Client("2.1", session=session)
        return compute

    def find_target_server(self, compute, ip_address):
        for server in compute.servers.list(search_opts={'all_tenants': 1}):
            try:
                # if this fails we're dealing with vim-emu incomplete API
                server.interface_list()
            except MethodNotAllowed:
                # proceed to "emulate" the isolation
                LOGGER.info("Does not support interface_list ... emulating")
                self.store_vim_emu_vnf_configuration()
                return
            for interface in server.interface_list():
                for fixed_ip in interface.fixed_ips:
                    LOGGER.info(interface.port_id)
                    if fixed_ip["ip_address"] == ip_address:
                        return server

    def execute_openstack_termination(self):
        ip_address = self._node["ip_address"].split(";")[0]
        target_server = None
        compute = self.get_openstack_compute()
        target_server = self.find_target_server(compute, ip_address)
        if not target_server:
            return
        target_server.stop()
        LOGGER.info("Server id found {0} for ip {1}".format(target_server.id,
                                                            ip_address))
        self._node.update(set__terminated=True)

    def execute_openstack_isolation(self):
        ip_address = self._node["ip_address"].split(";")[0]
        target_server = None
        compute = self.get_openstack_compute()
        target_server = self.find_target_server(compute, ip_address)
        if not target_server:
            return
        LOGGER.info("Server id found {0} for ip {1}".format(target_server.id,
                                                            ip_address))
        previous_config = []
        for interface in target_server.interface_list():
            LOGGER.info(interface.fixed_ips)
            previous_config.append(interface.fixed_ips)
            target_server.interface_detach(interface.port_id)
        record = IsolationRecord(output=json.dumps(previous_config), error="")
        record.save()
        self._node["isolation_policy"]["records"].append(record)
        self._node["isolation_policy"].save()
        self._node.update(set__isolated=True)

    def store_vim_emu_vnf_configuration(self, terminate):
        addresses = self._node["ip_address"].split(";")
        previous_config = []
        for address in addresses:
            previous_config.append({"subnet_id": str(uuid.uuid4()),
                                    "ip_address": address})
        for i in range(0, 2):
            subnet_id = str(uuid.uuid4())
            ip_address = "10.0.{0}.{1}".format(random.randint(2, 230),
                                               random.randint(2, 230))
            previous_config.append({"subnet_id": subnet_id,
                                    "ip_address": ip_address})
            record = IsolationRecord(output=json.dumps(previous_config),
                                     error="")
            record.save()
        self._node["isolation_policy"]["records"].append(record)
        self._node["isolation_policy"].save()
        self._node.update(set__isolated=True)
        if terminate:
            self._node.update(set__terminated=True)

    def isolate(self, terminated=False):
        policy = self._node["isolation_policy"]
        if isinstance(policy, OpenstackIsolation):
            LOGGER.info("Openstack isolation request")
            if terminated:
                self.execute_openstack_termination()
            else:
                self.execute_openstack_isolation()
            return
        ssh = paramiko.client.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        if isinstance(self._node["authentication"], PasswordAuth):
            ssh.connect(self._node["host_name"],
                        username=self._node["authentication"]["username"],
                        password=self._node["authentication"]["password"])
        else:
            try:
                self._node["host_name"].rstrip()
                pkey_from_auth = StringIO(
                    self._node["authentication"]["private_key"])
                pkey = paramiko.RSAKey.from_private_key(
                    pkey_from_auth)
                pkey_from_auth.close()
                ssh.connect(self._node["host_name"],
                            username=self._node["authentication"]["username"],
                            pkey=pkey)
            except socket.gaierror as exc:
                print("Error connecting {0}".format(exc))
                raise NodeSSHException
        scp = ssh.open_sftp()
        file_id = str(uuid.uuid4())
        if terminated:
            policy = self._node["termination_policy"]
        if isinstance(policy, Shutdown):
            record = self.execute_shutdown(file_id, ssh, scp, policy)
        if isinstance(policy, InterfaceDown):
            record = self.execute_interface_down(file_id, ssh, scp, policy)
        elif isinstance(policy, DeleteFlow):
            record = self.execute_delete_flow(file_id, ssh, scp, policy)
        ssh.close()
        self._node["isolation_policy"]["records"].append(record)
        self._node["isolation_policy"].save()
        self._node.update(set__isolated=True)
        if terminated:
            self._node.update(set__terminated=True)
        self._node.save()
