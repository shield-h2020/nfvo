#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nfvo.osm import NFVO_ENDPOINT
from nfvo.osm import NFVO_PKG_ENDPOINT
from nfvo.osm import NFVO_PORT
from nfvo.osm import NFVO_PKG_PORT


BASE = "https://{}:{}/{}"
PKG_NS_REMOVE = BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, "composer/api/catalog/nsd/{}?api_server=https://localhost")
PKG_ONBOARD = BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, "composer/upload?api_server=https://localhost")
PKG_VNF_REMOVE = BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, "composer/api/catalog/vnfd/{}?api_server=https://localhost")
#NS_CATALOG_C = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/config/nsd-catalog/nsd")
NS_CATALOG_C = BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, "composer/api/catalog?api_server=https://localhost")
NS_CATALOG_O = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operational/nsd-catalog/nsd")
VIM_LIST_O = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operational/datacenters")
VNF_ACTION_EXEC = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operations/exec-ns-service-primitive")
VNF_ACTION_L_EXEC = BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, "launchpad/api/exec-ns-service-primitive?api_server=https://localhost")
#VNF_CATALOG_C = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/config/vnfr-catalog/vnfr")
VNF_CATALOG_C = BASE.format(NFVO_PKG_ENDPOINT, NFVO_PKG_PORT, "composer/api/catalog?api_server=https://localhost")
VNF_CATALOG_O = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operational/vnfr-catalog/vnfr")


def get_default_headers():
    headers = rest_auth_headers()
    headers.update({"Accept": "application/vnd.yang.collection+json"})
    return headers

def post_default_headers():
    headers = rest_auth_headers()
    headers.update({"Content-Type": "application/vnd.yang.data+json",
        "Accept": "application/vnd.yang.data+json"})
    return headers

def post_encoded_headers():
    headers = rest_auth_headers()
    headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    return headers

def rest_auth_headers():
    return {"Authorization": "Basic YWRtaW46YWRtaW4="}
