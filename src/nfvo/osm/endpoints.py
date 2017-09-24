#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server import NFVO_ENDPOINT
from server import NFVO_PORT


BASE = "https://{}:{}/{}"
VNF_ACTION_EXEC = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operations/exec-ns-service-primitive")
VNF_CATALOG_C = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/config/vnfr-catalog/vnfr")
VNF_CATALOG_O = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operational/vnfr-catalog/vnfr")
NS_CATALOG_C = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "v1/api/config/nsd-catalog/nsd")
NS_CATALOG_O = BASE.format(NFVO_ENDPOINT, NFVO_PORT, "api/operational/nsd-catalog/nsd")


def get_default_headers():
    headers = rest_auth_headers()
    headers.update({"Accept": "application/vnd.yang.collection+json"})
    return headers

def post_default_headers():
    headers = rest_auth_headers()
    headers.update({"Content-Type": "application/vnd.yang.data+json",
        "Accept": "application/vnd.yang.data+json"})
    return headers

def rest_auth_headers():
    return {"Authorization": "Basic YWRtaW46YWRtaW4="}
