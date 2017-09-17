#!/usr/bin/env python
# -*- coding: utf-8 -*

from bson import json_util
from core.config import FullConfParser

import ast
import json
import logging
import pymongo
import threading
import time

logger = logging.getLogger("db-manager")


class DBManager():
    """
    This object is a wrapper for MongoClient to communicate to the RO
    (local) mongo-db
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
        self.user_password = self.db_db.get("password")
        #general_section = self.config.get("general")
        #self.db_name = ast.literal_eval(general_section.get("db_name"))
        #self.host = "127.0.0.1"
        #self.port = 27017
        #self.db_name = "shield-nfvo"
        #self.user_id = "user"
        #self.user_password = "user"
        self.user_options = {"roles": [
            { "role": "readWrite", "db": self.db_name },
            { "role": "dbAdmin", "db": self.db_name }
        ]}
        self.address = "mongodb://{}:{}".format(self.host, self.port)
        self.auth_db_address = "mongodb://{}:{}@{}:{}/{}".format(self.user_id,
            self.user_password,
            self.host, self.port, self.db_name)
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
        db = self.__get_database()
        #db.add_user(self.user_id, self.user_password, **self.user_options)
        if not db:
            db.add_user(self.user_id, self.user_password, **self.user_options)
        for collection_name in self.collections:
            collection = self.__get_table(collection_name)
            if not collection:
                collection = db.create_collection(collection_name)

    def __get_database(self):
        self.client = pymongo.MongoClient(self.auth_db_address, self.port)
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

#    def store_vnf_action(self, vnsfr_id, primitive, description, params):
    def store_vnf_action(self, vnsfr_id, primitive, params):
        """
        Track remote action executed per vNSF.
        """
        table = self.__get_table("resource.vnsf.action")
        try:
            self.__mutex.acquire()
            current_time = self.__current_ms()
            row = table.find_one({"_vnsfr_id": vnsfr_id})
            if row:
                row["primitive"] = primitive
#                row["description"] = description
                row["params"] = params
                row["date"] = current_time
                return table.save(row)
            else:
                entry = {"_vnsfr_id": vnsfr_id,
                         "primitive": primitive,
#                         "description": description,
                         "params": params,
                         "date": current_time }
                return table.insert(entry)
        except:
            e = "Cannot store MSPL information for vNSF with ID: {}".format(vnsfr_id)
            raise Exception(e)
        finally:
            self.__mutex.release()

    def delete_action_per_vnsf(self, vnsfr_id):
        table = self.__get_table("resource.vnsf.action")
        try:
            self.__mutex.acquire()
            table.remove({"_vnsfr_id": vnsfr_id})

        finally:
            self.__mutex.release()


if __name__ == "__main__":
    db_manager = DBManager()
    db_manager._first_setup()
    db_manager.store_mspl("vnsf__1", "<xml>data</xml>")
    db_manager.store_mspl("vnsf__1", "<xml>data 2</xml>")
