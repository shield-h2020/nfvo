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
from core.exception import Exception
from core.exception import HttpCode
from core.exception import ExceptionCode
from db.models.infra.node import Node as NodeModel
from db.models.auth.auth import PasswordAuth
from db.models.isolation.isolation_policy import InterfaceDown
from db.models.isolation.isolation_policy import DeleteFlow
from db.models.isolation.isolation_policy import Shutdown
from db.models.isolation.isolation_record import IsolationRecord
from jinja2 import Template


import configparser
import paramiko
import uuid


class Node:

    def __init__(self, node_id):
        nodes = NodeModel.objects(id=ObjectId(node_id))
        if len(nodes) < 1:
            error_msg = "Node with id={0} not found".format(node_id)
            Exception.abort(HttpCode.NOT_FOUND,
                            ExceptionCode.NOT_FOUND,
                            error_msg)
        config = configparser.ConfigParser()
        config.read("conf/isolation.conf")
        self._scripts_path = config["scripts"]["path"]
        self._shutdown_path = config["scripts"]["shutdown"]
        self._delflow_path = config["scripts"]["delflow"]
        self._ifdown_path = config["scripts"]["ifdown"]
        self._node = nodes[0]

    def isolate(self):
        ssh = paramiko.client.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        if isinstance(self._node["authentication"], PasswordAuth):
            ssh.connect(self._node["host_name"],
                        username=self._node["authentication"]["username"],
                        password=self._node["authentication"]["password"])
        else:
            ssh.connect(self._node["host_name"],
                        username=self._node["authentication"]["username"],
                        pkey=self._node["authentication"]["private_key"])
        scp = ssh.open_sftp()
        file_id = str(uuid.uuid4())
        if isinstance(self._node["isolation_policy"], Shutdown):
            # Process shutdown by command template
            with open("{0}/{1}".format(self._scripts_path,
                                       self._shutdown_path)) as fhandle:
                sd_templ = Template(fhandle.read())
                # Send script to node and render template with policy command
                with scp.open("{0}.sh".format(file_id), "w") as rfhandle:
                    command = self._node["isolation_policy"]["command"]
                    rfhandle.write(sd_templ.render(command=command))
            ssh.exec_command("chmod u+x {0}.sh".format(file_id))
            # Execute isolation commmand
            (stdin, stdout, stderr) = ssh.exec_command("./{0}.sh".
                                                       format(file_id))
            # Store isolation record
            record = IsolationRecord(output=stdout.read(), error=stderr.read())
            record.save()
            # Remove tmp file
            ssh.exec_command("rm {0}.sh".format(file_id))
            self._node["isolation_policy"]["records"].append(record)
            self._node["isolation_policy"].save()
            self._node["isolated"] = True
            self._node.save()
        if isinstance(self._node["isolation_policy"], InterfaceDown):
            # Process interface down template
            with open("{0}/{1}".format(self._scripts_path,
                                       self._ifdown_path)) as fhandle:
                sd_templ = Template(fhandle.read())
                # Send script to node and render template with policy command
                with scp.open("{0}.sh".format(file_id), "w") as rfhandle:
                    ifname = self._node["isolation_policy"]["interface_name"]
                    rfhandle.write(sd_templ.render(interface_name=ifname))
            ssh.exec_command("chmod u+x {0}.sh".format(file_id))
            # Execute isolation script
            (stdin, stdout, stderr) = ssh.exec_command("./{0}.sh".
                                                       format(file_id))
            # Store isolation record
            record = IsolationRecord(output=stdout.read(), error=stderr.read())
            record.save()
            # Remove tmp file
            ssh.exec_command("rm {0}.sh".format(file_id))
            self._node["isolation_policy"]["records"].append(record)
            self._node["isolation_policy"].save()
            self._node["isolated"] = True
            self._node.save()
        if isinstance(self._node["isolation_policy"], DeleteFlow):
            # Process delete flow template
            with open("{0}/{1}".format(self._scripts_path,
                                       self._delflow_path)) as fhandle:
                sd_templ = Template(fhandle.read())
                # Send script to node and render template with policy command
                with scp.open("{0}.sh".format(file_id), "w") as rfhandle:
                    flow_id = self._node["isolation_policy"]["flow_id"]
                    rule = self._node["isolation_policy"]["rule"]
                    rfhandle.write(sd_templ.render(flow_id=flow_id,
                                                   rule=rule))
            ssh.exec_command("chmod u+x {0}.sh".format(file_id))
            # Execute isolation script
            (stdin, stdout, stderr) = ssh.exec_command("./{0}.sh".
                                                       format(file_id))
            # Store isolation record
            record = IsolationRecord(output=stdout.read(), error=stderr.read())
            record.save()
            # Remove tmp file
            ssh.exec_command("rm {0}.sh".format(file_id))
            self._node["isolation_policy"]["records"].append(record)
            self._node["isolation_policy"].save()
            self._node["isolated"] = True
            self._node.save()