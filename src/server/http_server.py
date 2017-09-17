#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from core import log
from core.config import FullConfParser
from db.manager import DBManager
from flask import Flask, g, request, request_started, request_finished
from server.views import nfvo_views
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
        self._app = Flask(__name__.split(".")[-1])
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
        New method. Allows to register URLs from a the views file.
        """
        self._app.register_blueprint(nfvo_views)

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
