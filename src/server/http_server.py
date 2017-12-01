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
from flask import request
from gui.swagger import swagger_views as v_gui
from server.views.endpoints import nfvo_views as v_endpoints
from server.views.infra import nfvo_views as v_nfvi
from server.views.ns import nfvo_views as v_ns
from server.views.package import nfvo_views as v_pkg
from server.views.vim import nfvo_views as v_vim
from server.views.vnf import nfvo_views as v_vnsf
from werkzeug import serving

import ast
import logging as log
import os
import ssl
import sys

logger = log.getLogger("httpserver")
API_HOST = "0.0.0.0"
API_PORT = "8000"
API_DEBUG = True
HTTPS_ENABLED = True
API_VERIFY_CLIENT = False


class Server(object):
    """
    Encapsules a flask server instance to expose a REST API.
    """

    def __init__(self):
        """
        Constructor for the server wrapper.
        """
        # Imports the named package, in this case this file
        self.__load_config()
        self._app = Flask(__name__.split(".")[-1],
            template_folder=self.template_folder)
        self._app.mongo = DBManager()
        #self._app.nfvo_host = self.nfvo_host
        #self._app.nfvo_port = self.nfvo_port
        # Added in order to be able to execute "before_request" method
        app = self._app

        @app.before_request
        def before_request():
            # "Attach" objects within the "g" object.
            # This is passed to each view method
            g.mongo = self._app.mongo

    def __load_config(self):
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
        self.https_enabled = ast.literal_eval(\
                self.api_sec.get("https_enabled")) \
                or HTTPS_ENABLED
        self.verify_users = ast.literal_eval(\
                self.api_sec.get("verify_client_cert")) \
                or API_VERIFY_CLIENT
        # GUI data
        self.template_folder = os.path.normpath(
            os.path.join(os.path.dirname(__file__),
                         "../gui", "flask_swagger_ui/templates"))
        # General NFVO data
        #self.nfvo_category = self.config.get("nfvo.conf")
        #self.nfvo_general = self.nfvo_category.get("general")
        #self.nfvo_host = self.nfvo_general.get("host")
        #self.nfvo_port = self.nfvo_general.get("port")

    @property
    def app(self):
        """
        Returns the flask instance (not part of the service interface,
        since it is specific to flask).
        """
        return self._app

    def add_routes(self):
        """
        New method. Allows to register URLs from the views files.
        """
        self._app.register_blueprint(v_endpoints)
        self._app.register_blueprint(v_gui)
        self._app.register_blueprint(v_nfvi)
        self._app.register_blueprint(v_ns)
        self._app.register_blueprint(v_pkg)
        self._app.register_blueprint(v_vim)
        self._app.register_blueprint(v_vnsf)

    def runServer(self, services=[]):
        """
        Starts up the server. It (will) support different config options
        via the config plugin.
        """
        self.add_routes()
        logger.info("Registering app server at %s:%i", self.host, self.port)
        try:
            context = None
            if self.https_enabled:
                # Set up a TLS context
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                certs_path = os.path.normpath(os.path.join(
                    os.path.dirname(__file__), "../../", "cert"))
                context_crt = os.path.join(certs_path, "server.crt")
                context_key = os.path.join(certs_path, "server.key")
                try:
                    context.load_cert_chain(context_crt, context_key)
                except Exception as e:
                    exc_det = "Error starting server. Missing " + \
                        "server cert or key under {}".format(certs_path)
                    logger.critical(exc_det)
                    sys.exit(exc_det)

                if self.verify_users:
                    context.verify_mode = ssl.CERT_REQUIRED
                    try:
                        context.load_verify_locations(\
                            os.path.join(certs_path, "ca.crt"))
                    except Exception as e:
                        exc_det = "Error starting server. Missing " + \
                            "or empty {}/ca.crt".format(certs_path)
                        logger.critical(exc_det)
                        sys.exit(exc_det)

                    if self.debug:
                        logger.debug("SSL context defined")
                else:
                    if self.debug:
                        logger.debug("SSL context defined with client verification")

            serving.run_simple(
                self.host, self.port, self._app, \
                ssl_context=context, use_reloader=False)
        finally:
            self._app._got_first_request = False
