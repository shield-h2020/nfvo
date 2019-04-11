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
from core.log import setup_custom_logger
from db.models.auth.auth import PasswordAuth, KeyAuth
from db.models.infra.network_flow import NetworkFlow
from db.models.infra.node import Node
from db.models.isolation.isolation_policy import InterfaceDown
from db.models.isolation.isolation_policy import DeleteFlow
from db.models.isolation.isolation_policy import OpenstackIsolation
from db.models.isolation.isolation_policy import OpenstackTermination
from db.models.isolation.isolation_policy import Shutdown
from db.models.vnf_action_request import VnfActionRequest
from mongoengine import connect as me_connect
from mongoengine.errors import OperationError, ValidationError

import json
import pymongo
import threading
import time

LOGGER = setup_custom_logger(__name__)


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
                "delete_flow",
                "interface_down",
                "isolation_record",
                "key_auth",
                "network_flow",
                "node",
                "openstack_isolation",
                "openstack_termination",
                "password_auth",
                "shutdown",
                "vdu",
                "vnf_action_request"
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

    def get_phys_virt_nodes(self, physical, isolated=None):
        """
        Get physical or virtual nodes
        """
        if isolated is not None:
            # Get isolated nodes (terminated also)
            nodes = Node.objects(physical=physical,
                                 isolated=isolated,
                                 terminated__in=[True, False])
        else:
            nodes = Node.objects(physical=physical)
        return self.__format_nodes(nodes)

    def get_flows(self, filters={}):
        """
        Get flow according to an ID or multiple flows as saved previously.
        Flows are returned ordered - from newest first to oldest in the end
        """
        if filters is not None:
            # Expand filters from dictionary to parameters for mongoengine
            flows = NetworkFlow.objects(**filters).order_by("-date")
        else:
            flows = NetworkFlow.objects().order_by("-date")
        return flows

    def store_flows(self, device_id, table_id, flow_id, flow, trusted=False):
        """
        Stores the flow or multiple flows and associated data.
        """
        try:
            print("storing flows -> to store flow_id = " + str(flow_id))
            print("storing flows -> to store flow = " + str(flow))
            print("storing flows -> to store trusted = " + str(trusted))
            flows = NetworkFlow(device_id=device_id,
                                table_id=table_id,
                                flow_id=flow_id,
                                flow=flow,
                                trusted=trusted)
            print("storing flows = " + str(flows))
            flows.save()
        except (OperationError, ValidationError):
            # Rolling back
            flows.delete()
            e = "Cannot store network information (flows)"
            raise Exception(e)
        return str(flows.flow_id)

    def delete_flows(self, device_id, table_id, flow_id=None, date=None):
        """
        Stores the flow or multiple flows and associated data.
        """
        try:
            if flow_id is None and date is None:
                flows = NetworkFlow.objects(device_id=device_id,
                                            table_id=table_id)
            elif flow_id is None and date is not None:
                flows = NetworkFlow.objects(device_id=device_id,
                                            table_id=table_id,
                                            date=date)
            elif flow_id is not None and date is None:
                flows = NetworkFlow.objects(device_id=device_id,
                                            table_id=table_id,
                                            flow_id=flow_id)
            flows.delete()
        except (OperationError, ValidationError):
            # Rolling back
            flows.delete()
            e = "Cannot delete network information (flows)"
            raise Exception(e)
        return str(flow_id)

    def get_nodes(self, node_id=None):
        """
        Get nodes
        """
        if node_id is None:
            nodes = Node.objects()
        else:
            nodes = Node.objects(id=ObjectId(node_id))
        return self.__format_nodes(nodes)

    def __format_nodes(self, nodes):
        """
        Output nodes with a specific format
        """
        response = []
        for node in nodes:
            node_resp = {"node_id": str(node.id),
                         "host_name": node["host_name"],
                         "ip_address": node["ip_address"],
                         "pcr0": node["pcr0"],
                         "driver": node["driver"],
                         "distribution": node["distribution"],
                         "analysis_type": node["analysis_type"],
                         "physical": node["physical"]}
            if node["isolated"]:
                node_resp["status"] = "isolated"
                records = [{"configuration": x["output"],
                            "date": x["date"]} for x in
                           node["isolation_policy"]["records"]]
                node_resp["configuration"] = records
                if node["terminated"]:
                    node_resp["status"] = "terminated"
            else:
                node_resp["status"] = "connected"
            if node["disabled"] is False:
                response.append(node_resp)
        return response

    def delete_node(self, node_id):
        """
        Deletes the node and reference field documents
        """
        nodes = Node.objects(id=ObjectId(node_id))
        for node in nodes:
            node.authentication.delete()
            for record in node.isolation_policy["records"]:
                record.delete()
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
            isolation = DeleteFlow(
                name=str(isolation_policy["name"]),
                switch=str(isolation_policy["switch"]),
                target_filter=str(isolation_policy["target_filter"]))
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
        termination_policy = node_data["termination_policy"]
        if termination_policy["type"] == "ifdown":
            termination = InterfaceDown(
                name=str(termination_policy["name"]),
                interface_name=str(termination_policy["interface_name"]))
        if termination_policy["type"] == "delflow":
            termination = DeleteFlow(
                name=str(termination_policy["name"]),
                switch=str(termination_policy["switch"]),
                target_filter=str(termination_policy["target_filter"]))
        if termination_policy["type"] == "shutdown":
            termination = Shutdown(name=str(termination_policy["name"]),
                                   command=str(termination_policy["command"]))
        try:
            termination.save()
        except (OperationError, ValidationError):
            # Rolling back
            auth.delete()
            e = "Cannot store node information (termination)"
            raise Exception(e)
        physical = False
        if ("physical" in node_data) and (node_data["physical"] is True):
            physical = True
        node = Node(host_name=str(node_data["host_name"]),
                    ip_address=str(node_data["ip_address"]),
                    distribution=str(node_data["distribution"]),
                    pcr0=str(node_data["pcr0"]),
                    driver=str(node_data["driver"]),
                    analysis_type=str(node_data["analysis_type"]),
                    authentication=auth,
                    isolation_policy=isolation,
                    termination_policy=termination,
                    disabled=False,
                    physical=physical)
        try:
            node.save()
        except (OperationError, ValidationError):
            # Rolling back
            auth.delete()
            isolation.delete()
            e = "Cannot store node information (node)"
            raise Exception(e)
        return str(node.id)

    def get_vnf_actions(self, vnsfr_id):
        """
        Get remote action executed per vNSF.
        """
        vnf_action_requests = VnfActionRequest.objects(vnsfr_id=vnsfr_id)
        return vnf_action_requests

    def store_vdu(self, name, management_ip,
                  isolation_policy,
                  termination_policy,
                  authentication,
                  analysis_type, pcr0, distribution, driver,
                  instance_id,
                  vnfr_id):
        """
        Register VDU as node.
        Isolation and/or termination policy is stored,
        as well as authentication policy.
        Isolation and termination follow the precedence
        (from highest to lowest):
        isolate/host_shutdown, isolate/iface_down,
        isolate/flow_delete, terminate/host_shutdown,
        terminate/iface_down, terminate/flow_delete
        """
        if isolation_policy["type"] == "shutdown":
            LOGGER.info("Storing shutdown isolation")
            isolation = Shutdown(name=str(isolation_policy["name"]),
                                 command=str(isolation_policy["command"]))
        elif isolation_policy["type"] == "ifdown":
            LOGGER.info("Storing interface down isolation")
            isolation = InterfaceDown(
                name=str(isolation_policy["name"]),
                interface_name=str(isolation_policy["interface_name"]))
        elif isolation_policy["type"] == "delflow":
            LOGGER.info("Storing delete flow isolation")
            isolation = DeleteFlow(
                name=str(isolation_policy["name"]),
                switch=str(isolation_policy["switch"]),
                target_filter=str(isolation_policy["target_filter"]))
        elif isolation_policy["type"] == "openstack_isolation":
            LOGGER.info("Storing openstack isolation")
            isolation = OpenstackIsolation(
                name=str(isolation_policy["name"]),
                identity_endpoint=isolation_policy["identity_endpoint"],
                username=isolation_policy["username"],
                password=isolation_policy["password"],
                project_name=isolation_policy["project_name"],
                domain_name=isolation_policy["domain_name"])
        if termination_policy["type"] == "shutdown":
            LOGGER.info("Storing shutdown termination")
            termination = Shutdown(name=str(termination_policy["name"]),
                                   command=str(termination_policy["command"]))
        elif termination_policy["type"] == "ifdown":
            LOGGER.info("Storing interface down termination")
            termination = InterfaceDown(
                name=str(termination_policy["name"]),
                interface_name=str(termination_policy["interface_name"]))
        elif termination_policy["type"] == "delflow":
            LOGGER.info("Storing delete flow termination")
            termination = DeleteFlow(
                name=str(termination_policy["name"]),
                switch=str(termination_policy["switch"]),
                target_filter=str(termination_policy["target_filter"]))
        elif termination_policy["type"] == "openstack_termination":
            LOGGER.info("Storing openstack termination")
            termination = OpenstackTermination(
                name=str(termination_policy["name"]),
                identity_endpoint=termination_policy["identity_endpoint"],
                username=termination_policy["username"],
                password=termination_policy["password"],
                project_name=termination_policy["project_name"],
                domain_name=termination_policy["domain_name"])
        if authentication["type"] == "private_key":
            LOGGER.info("Storing private key auth")
            auth = KeyAuth(username=str(authentication["username"]),
                           private_key=str(authentication["private_key"]))
        elif authentication["type"] == "password":
            LOGGER.info("Storing password auth")
            auth = PasswordAuth(username=str(authentication["username"]),
                                password=str(authentication["password"]))
        else:
            LOGGER.info("Authentication mode not supported")
            return
        auth.save()
        isolation.save()
        termination.save()
        LOGGER.info(
            "Storing node with instance_id {0}".format(str(instance_id)))
        LOGGER.info("hostname: {0}".format(name))
        LOGGER.info("ip_address: {0}".format(management_ip))
        LOGGER.info("instance_id: {0}".format(str(instance_id)))
        vdu = Node(host_name=name,
                   ip_address=management_ip,
                   authentication=auth,
                   pcr0=pcr0,
                   driver=driver,
                   analysis_type=analysis_type,
                   distribution=distribution,
                   disabled=False,
                   physical=False,
                   isolation_policy=isolation,
                   termination_policy=termination,
                   instance_id=str(instance_id),
                   vnfr_id=str(vnfr_id))
        vdu.save()

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
