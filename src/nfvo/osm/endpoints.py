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



