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


import uuid
import unittest

from core.config import FullConfParser
from db.models.vnf_action_request import VnfActionRequest
from db.models.auth.auth import PasswordAuth
from db.models.infra.node import Node
from db.models.isolation.isolation_policy import InterfaceDown
from db.models.compute.vdu import Vdu
from mongoengine import connect as me_connect


class TestDbConnectivity(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDbConnectivity, self).__init__(*args, **kwargs)
        config = FullConfParser()
        db_category = config.get("db.conf")
        db_general = db_category.get("general")
        host = db_general.get("host")
        port = int(db_general.get("port"))
        db_db = db_category.get("db")
        db_name = db_db.get("name")
        user_id = db_db.get("user")
        auth_source = db_db.get("auth_source")
        user_password = db_db.get("password")
        auth_db_address = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
            user_id,
            user_password,
            host,
            port,
            db_name,
            auth_source)
        me_connect(host=auth_db_address)

    def test_db_connectivity(self):
        vnsfr_id = str(uuid.uuid4())
        vnf_action_request = VnfActionRequest(primitive="test-primitive",
                                              vnsfr_id=vnsfr_id,
                                              params={"policy": "set-policy"},
                                              response={"status": "success"})
        vnf_action_request.save()
        read_vnf_action = VnfActionRequest.objects(vnsfr_id=vnsfr_id).first()
        read_vnf_action.delete()

    def test_vdu_model(self):
        authentication = PasswordAuth(username="user", password="password")
        authentication.save()
        isolation_policy = InterfaceDown(name="ens0 down",
                                         interface_name="ens0")
        isolation_policy.save()
        node = Node(host_name="nova2",
                    ip_address="192.168.10.1",
                    distribution="xenial",
                    pcr0="()",
                    driver="ssh",
                    analysis_type="()",
                    authentication=authentication,
                    isolation_policy=isolation_policy,
                    disabled=False)
        node.save()
        vdu_ip_address = "192.168.10.10"
        vdu = Vdu(name="vfw",
                  management_ip=vdu_ip_address,
                  authentication=authentication,
                  isolation_policy=isolation_policy,
                  node=node)
        vdu.save()
        read_vdu = Vdu.objects(management_ip=vdu_ip_address)
        read_vdu.delete()
        read_node = Node.objects(host_name="nova2")
        read_node.delete()
        read_isolation_policy = InterfaceDown.objects(id=isolation_policy.id)
        read_isolation_policy.delete()
        read_authentication = PasswordAuth.objects(username="user")
        read_authentication.delete()
