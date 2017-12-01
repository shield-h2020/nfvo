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


NFVO_ENDPOINT = "10.101.10.100"
NFVO_PORT = "8008"
NFVO_PKG_ENDPOINT = "10.101.10.100"
NFVO_PKG_PORT = "8443"


def load_config():
    config = FullConfParser()
    # General NFVO data
    nfvo_category = config.get("nfvo.conf")
    nfvo_general = nfvo_category.get("general")
    nfvo_host = nfvo_general.get("host", NFVO_ENDPOINT)
    nfvo_port = nfvo_general.get("port", NFVO_PORT)
    # Package data
    nfvo_package = nfvo_category.get("package")
    nfvo_pkg_host = nfvo_package.get("host", NFVO_PKG_ENDPOINT)
    nfvo_pkg_port = nfvo_package.get("port", NFVO_PKG_PORT)
    return {"nfvo_host": nfvo_host,
            "nfvo_port": nfvo_port,
            "nfvo_pkg_host": nfvo_pkg_host,
            "nfvo_pkg_port": nfvo_pkg_port}


cfg = load_config()
NFVO_ENDPOINT = cfg.get("nfvo_host")
NFVO_PORT = cfg.get("nfvo_port")
NFVO_PKG_ENDPOINT = cfg.get("nfvo_pkg_host")
NFVO_PKG_PORT = cfg.get("nfvo_pkg_port")
