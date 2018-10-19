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
# Used to map internally to an OSM DC, if user does not request a specific one
# TODO: once all DCs are operative, request from /vim endpoint
NFVO_DEFAULT_KVM_DATACENTER = "f9acd550-9d48-11e7-ae4c-00163e3afbe5"
# TODO: once all DCs are operative, request provider network name somehow else
NFVO_DEFAULT_KVM_DATACENTER_NET = "provider"
NFVO_DEFAULT_DOCKER_DATACENTER = "f9acd550-9d48-11e7-ae4c-00163e3afbe5"
NFVO_DEFAULT_DOCKER_DATACENTER_NET = "provider"
NFVO_PKG_ENDPOINT = NFVO_ENDPOINT
NFVO_PKG_PORT = "8443"
NFVO_PKG_STATUS_PORT = "4567"
NFVO_RO_ENDPOINT = NFVO_ENDPOINT
NFVO_RO_PORT = "9090"


def load_config():
    config = FullConfParser()
    # General NFVO data
    nfvo_category = config.get("nfvo.conf")
    nfvo_general = nfvo_category.get("general")
    nfvo_host = nfvo_general.get("host", NFVO_ENDPOINT)
    nfvo_port = nfvo_general.get("port", NFVO_PORT)
    nfvo_default_kvm_datacenter = \
        nfvo_general.get("default_kvm_datacenter",
                         NFVO_DEFAULT_KVM_DATACENTER)
    nfvo_default_docker_datacenter = \
        nfvo_general.get("default_docker_datacenter",
                         NFVO_DEFAULT_DOCKER_DATACENTER)
    nfvo_default_kvm_datacenter_net = \
        nfvo_general.get("default_kvm_datacenter_net",
                         NFVO_DEFAULT_KVM_DATACENTER)
    nfvo_default_docker_datacenter_net = \
        nfvo_general.get("default_docker_datacenter_net",
                         NFVO_DEFAULT_DOCKER_DATACENTER)
    # Package data
    nfvo_package = nfvo_category.get("package")
    nfvo_pkg_host = nfvo_package.get("host", NFVO_PKG_ENDPOINT)
    nfvo_pkg_port = nfvo_package.get("port", NFVO_PKG_PORT)
    # RO data
    nfvo_ro = nfvo_category.get("ro")
    nfvo_ro_host = nfvo_ro.get("host", NFVO_RO_ENDPOINT)
    nfvo_ro_port = nfvo_ro.get("port", NFVO_RO_PORT)
    return {"nfvo_host": nfvo_host,
            "nfvo_port": nfvo_port,
            "nfvo_default_kvm_datacenter":
            nfvo_default_kvm_datacenter,
            "nfvo_default_kvm_datacenter_net":
            nfvo_default_kvm_datacenter_net,
            "nfvo_default_docker_datacenter":
            nfvo_default_docker_datacenter,
            "nfvo_default_docker_datacenter_net":
            nfvo_default_docker_datacenter_net,
            "nfvo_pkg_host": nfvo_pkg_host,
            "nfvo_pkg_port": nfvo_pkg_port,
            "nfvo_ro_host": nfvo_ro_host,
            "nfvo_ro_port": nfvo_ro_port}


cfg = load_config()
NFVO_ENDPOINT = cfg.get("nfvo_host")
NFVO_PORT = cfg.get("nfvo_port")
NFVO_DEFAULT_KVM_DATACENTER = cfg.get("nfvo_default_kvm_datacenter")
NFVO_DEFAULT_KVM_DATACENTER_NET = cfg.get("nfvo_default_kvm_datacenter_net")
NFVO_DEFAULT_DOCKER_DATACENTER = cfg.get("nfvo_default_docker_datacenter")
NFVO_DEFAULT_DOCKER_DATACENTER_NET = \
    cfg.get("nfvo_default_docker_datacenter_net")
NFVO_PKG_ENDPOINT = cfg.get("nfvo_pkg_host")
NFVO_PKG_PORT = cfg.get("nfvo_pkg_port")
NFVO_RO_ENDPOINT = cfg.get("nfvo_ro_host")
NFVO_RO_PORT = cfg.get("nfvo_ro_port")
