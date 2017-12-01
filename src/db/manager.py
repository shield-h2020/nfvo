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
from core.config import FullConfParser

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
        self.user_password = self.db_db.get("password")
        self.user_options = {"roles": [
            {"role": "readWrite", "db": self.db_name},
            {"role": "dbAdmin", "db": self.db_name}
        ]}
        self.address = "mongodb://{}:{}".format(self.host, self.port)
        self.auth_db_address = "mongodb://{}:{}@{}:{}/{}".format(
                self.user_id,
                self.user_password,
                self.host,
                self.port,
                self.db_name)
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
                row["params"] = params
                row["date"] = current_time
                return table.save(row)
            else:
                entry = {"_vnsfr_id": vnsfr_id,
                         "primitive": primitive,
                         "params": params,
                         "date": current_time}
                return table.insert(entry)
        except Exception:
            e = "Cannot store MSPL information for vNSF with ID: {}".\
                    format(vnsfr_id)
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
