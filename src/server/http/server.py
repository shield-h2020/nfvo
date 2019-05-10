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


from gui.swagger import swagger_views as v_gui
from server.http.server_cfg import ServerConfig
from server.views.endpoints import nfvo_views as v_endpoints
from server.views.infra import nfvo_views as v_nfvi
from server.views.ns import nfvo_views as v_ns
from server.views.package import nfvo_views as v_pkg
from server.views.vim import nfvo_views as v_vim
from server.views.vnf import nfvo_views as v_vnsf
from werkzeug import serving

import logging as log
import os
import ssl
import sys

logger = log.getLogger("httpserver")


class Server(object):
    """
    Encapsulates a Flask server instance to expose a REST API.
    """

    def __init__(self):
        """
        Constructor for the server wrapper.
        """
        cfg = ServerConfig()
        self.__dict__.update(cfg.__dict__)

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

    def run(self):
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
                    os.path.dirname(__file__), "../../../", "cert"))
                context_crt = os.path.join(certs_path, "server.crt")
                context_key = os.path.join(certs_path, "server.key")
                try:
                    context.load_cert_chain(context_crt, context_key)
                except Exception:
                    exc_det = "Error starting server. Missing " + \
                        "server cert or key under {}".format(certs_path)
                    logger.critical(exc_det)
                    sys.exit(exc_det)

                if self.verify_users:
                    context.verify_mode = ssl.CERT_REQUIRED
                    try:
                        context.load_verify_locations(
                            os.path.join(certs_path, "ca.crt"))
                    except Exception:
                        exc_det = "Error starting server. Missing " + \
                            "or empty {}/ca.crt".format(certs_path)
                        logger.critical(exc_det)
                        sys.exit(exc_det)

                    if self.debug:
                        logger.debug("SSL context defined")
                else:
                    if self.debug:
                        logger.debug("SSL context defined with " +
                                     "client verification")

            if self.https_enabled:
                serving.run_simple(
                    self.host, int(self.port), self._app,
                    ssl_context=context, use_reloader=False,
                    threaded=True)
            # No HTTPS required no "ssl_context" object at all
            else:
                serving.run_simple(
                    self.host, int(self.port), self._app,
                    use_reloader=False,
                    threaded=True)
        finally:
            self._app._got_first_request = False
