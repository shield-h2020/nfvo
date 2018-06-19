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


from bson import json_util
from bson.objectid import ObjectId
from core.config import FullConfParser
from db.models.vnf_action_request import VnfActionRequest
from db.models.infra.node import Node
from db.models.auth.auth import PasswordAuth, KeyAuth
from db.models.isolation.isolation_policy import InterfaceDown
from db.models.isolation.isolation_policy import DeleteFlow
from db.models.isolation.isolation_policy import Shutdown
from mongoengine import connect as me_connect
from mongoengine.errors import OperationError, ValidationError

import json
import logging
import pymongo
import threading
import time

logger = logging.getLogger("db-manager")


class DBManager():
    """
    Wrapper for MongoClient to communicate to the RO (local) mongo-db
    """

    def __init__(self):
        self.__mutex = threading.Lock()
        self.config = FullConfParser()
        self.db_category = self.config.get("db.conf")
        self.db_general = self.db_category.get("general")
        self.host = self.db_general.get("host")
        self.port = int(self.db_general.get("port"))
        self.db_db = self.db_category.get("db")
        self.db_name = self.db_db.get("name")
        self.user_id = self.db_db.get("user")
        self.auth_source = self.db_db.get("auth_source")
        self.user_password = self.db_db.get("password")
        self.user_options = {"roles": [
            {"role": "readWrite", "db": self.db_name},
            {"role": "dbAdmin", "db": self.db_name}
        ]}
        self.address = "mongodb://{}:{}".format(self.host, self.port)
        self.auth_db_address = "mongodb://{}:{}@{}:{}/{}?authSource={}".format(
                self.user_id,
                self.user_password,
                self.host,
                self.port,
                self.db_name,
                self.auth_source)
        me_connect(host=self.auth_db_address)
        self.collections = [
                "resource.vnsf",
                "resource.vnsf.action",
                "topology.physical",
                "topology.slice",
                "topology.slice.sdn"
        ]
        self.client = pymongo.MongoClient(self.address, self.port)
        self._first_setup()

    def _first_setup(self):
        db = self.__get_database(self.address)
        if not db:
            db.add_user(self.user_id, self.user_password, **self.user_options)
        for collection_name in self.collections:
            collection = self.__get_table(collection_name)
            if not collection:
                collection = db.create_collection(collection_name)

    def __get_database(self, db_address=None):
        if not db_address:
            db_address = self.auth_db_address
        self.client = pymongo.MongoClient(db_address, self.port)
        return getattr(self.client, self.db_name)

    def __get_table(self, table_name):
        return getattr(self.__get_database(), table_name)

    def __check_return_rows(self, rows, custom_table, filter_params={}):
        if rows is None:
            raise Exception("%s -- could not find entry with params=%s!" %
                            (custom_table.full_name, filter_params))
        return rows

    def __get_one(self, custom_table, filter_params={}):
        table = custom_table
        try:
            self.__mutex.acquire()
            row = table.find_one(filter_params)
            return self.__check_return_rows(row, custom_table, filter_params)
        finally:
            self.__mutex.release()

    def __get_all(self, custom_table, filter_params={}):
        table = custom_table
        try:
            self.__mutex.acquire()
            rows = table.find(filter_params)
            return self.__check_return_rows(rows, custom_table, filter_params)
        finally:
            self.__mutex.release()

    def __current_ms(self):
        return int(round(time.time() * 1000))

    def __to_json(data):
        return json.dumps(data, default=json_util.default)

    def format_vnf_action_output(self, output):
        vnf_out_list_primitive = output["vnf-out-list"]["vnf-out-primitive"]
        exec_id = vnf_out_list_primitive["execution-id"]
        exec_status = vnf_out_list_primitive["execution-status"]
        exec_err_details = vnf_out_list_primitive["execution-error-details"]
        primitive_name = vnf_out_list_primitive["name"]
        primitive_index = vnf_out_list_primitive["index"]
        return {
            "job_id": output.get("create-time", ""),
            "create_time": output.get("create-time", ""),
            "vnf_id": output["vnf-out-list"]["vnfr-id-ref"],
            "execution_id": exec_id,
            "execution_status": exec_status,
            "exec_err_details": exec_err_details,
            "name": primitive_name,
            "index": primitive_index,
            "member_vnf_index_ref":
            output["vnf-out-list"]["member_vnf_index_ref"],
            "instance_id": output["nsr_id_ref"],
            "triggered_by": output["triggered-by"]}

    def delete_node(self, node_id):
        """
        Deletes the node and reference field documents
        """
        nodes = Node.objects(id=ObjectId(node_id))
        for node in nodes:
            node.authentication.delete()
            node.isolation_policy.delete()
            node.delete()

    def store_node_information(self, node_data):
        """
        Stores node information including authentication and isolation_policy
        """
        authentication = node_data["authentication"]
        if authentication["type"] == "password":
            auth = PasswordAuth(username=authentication["username"],
                                password=authentication["password"])
        if authentication["type"] == "private_key":
            auth = KeyAuth(username=authentication["username"],
                           private_key=authentication["private_key"])
        try:
            auth.save()
        except (OperationError, ValidationError):
            e = "Cannot store node information (auth)"
            raise Exception(e)
        isolation_policy = node_data["isolation_policy"]
        if isolation_policy["type"] == "ifdown":
            isolation = InterfaceDown(
                name=str(isolation_policy["name"]),
                interface_name=str(isolation_policy["interface_name"]))
        if isolation_policy["type"] == "delflow":
            isolation = DeleteFlow(name=str(isolation_policy["name"]),
                                   flow_id=str(isolation_policy["flow_id"]),
                                   rule=str(isolation_policy["rule"]))
        if isolation_policy["type"] == "shutdown":
            isolation = Shutdown(name=str(isolation_policy["name"]),
                                 command=str(isolation_policy["command"]))
        try:
            isolation.save()
        except (OperationError, ValidationError):
            # Rolling back
            auth.delete()
            e = "Cannot store node information (isolation)"
            raise Exception(e)
        node = Node(host_name=str(node_data["host_name"]),
                    ip_address=str(node_data["ip_address"]),
                    distribution=str(node_data["distribution"]),
                    pcr0=str(node_data["pcr0"]),
                    driver=str(node_data["driver"]),
                    analysis_type=str(node_data["analysis_type"]),
                    authentication=auth,
                    isolation_policy=isolation)
        try:
            node.save()
        except (OperationError, ValidationError):
            # Rolling back
            auth.delete()
            isolation.delete()
            e = "Cannot store node information (node)"
            raise Exception(e)
        return str(node.id)

    def store_vnf_action(self, vnsfr_id, primitive, params, output):
        """
        Track remote action executed per vNSF.
        """
        try:
            if "output" in output:
                fmt_output = self.format_vnf_action_output(output["output"])
            else:
                fmt_output = output
            vnf_action_request = VnfActionRequest(primitive=primitive,
                                                  vnsfr_id=vnsfr_id,
                                                  params=params,
                                                  response=fmt_output)
            vnf_action_request.save()
        except Exception:
            e = "Cannot store MSPL information for vNSF with ID: {}".\
                    format(vnsfr_id)
            raise Exception(e)

    def delete_action_per_vnsf(self, vnsfr_id):
        table = self.__get_table("resource.vnsf.action")
        try:
            self.__mutex.acquire()
            table.remove({"_vnsfr_id": vnsfr_id})

        finally:
            self.__mutex.release()
