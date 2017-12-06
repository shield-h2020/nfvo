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


from core.config import FullConfParser
from db.manager import DBManager
from flask import Flask
from flask import g

import ast
import os

API_HOST = "0.0.0.0"
API_PORT = "8000"
API_DEBUG = True
HTTPS_ENABLED = True
API_VERIFY_CLIENT = False


class ServerConfig(object):
    """
    Configuration for the Flask server.
    """

    def __init__(self):
        """
        Constructor for the server wrapper.
        """
        # Imports the named package, in this case this file
        self.__import_config()
        self._app = Flask(
                __name__.split(".")[-1],
                template_folder=self.template_folder)
        self._app.mongo = DBManager()
        # self._app.nfvo_host = self.nfvo_host
        # self._app.nfvo_port = self.nfvo_port
        # Added in order to be able to execute "before_request" method
        app = self._app

        @app.before_request
        def before_request():
            # "Attach" objects within the "g" object.
            # This is passed to each view method
            g.mongo = self._app.mongo

    def __import_config(self):
        """
        Fill properties fom configuration files.
        """
        self.config = FullConfParser()
        # Imports API-related info
        self.api_category = self.config.get("api.conf")
        # General API data
        self.api_general = self.api_category.get("general")
        self.host = self.api_general.get("host", API_HOST)
        self.port = self.api_general.get("port", API_PORT)
        self.debug = ast.literal_eval(
                self.api_general.get("debug")) or API_DEBUG
        # Verification and certificates
        self.api_sec = self.api_category.get("security")
        self.https_enabled = ast.literal_eval(
                self.api_sec.get("https_enabled")) \
            or HTTPS_ENABLED
        self.verify_users = ast.literal_eval(
                self.api_sec.get("verify_client_cert")) \
            or API_VERIFY_CLIENT
        # GUI data
        self.template_folder = os.path.normpath(
            os.path.join(os.path.dirname(__file__),
                         "../../gui", "flask_swagger_ui/templates"))
        # General NFVO data
        # self.nfvo_category = self.config.get("nfvo.conf")
        # self.nfvo_general = self.nfvo_category.get("general")
        # self.nfvo_host = self.nfvo_general.get("host")
        # self.nfvo_port = self.nfvo_general.get("port")
