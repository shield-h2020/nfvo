#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server import content
from nfv import vnf
from nfvo.osm import endpoints as osm_eps

import json
import requests


def get_nsr_config():
    resp = requests.get(osm_eps.NS_CATALOG_C,
        headers=content.get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def get_nsr_running():
    resp = requests.get(osm_eps.NS_CATALOG_O,
        headers=content.get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def fetch_config_nss():
    catalog = get_nsr_config()
    return format_ns_catalog(catalog)

def fetch_running_vnsfs():
    catalog = vnf.get_vnfr_running()
    return vnf.format_vnsf_catalog(catalog)

def format_ns_catalog(catalog):
    nss = []
    for ns in catalog["collection"]["nsd:nsd"]:
        ns_dict = {"ns_id": ns.get("id", None),
            "name": ns.get("name"),
            "vendor": ns.get("vendor")}
        nss.append(ns_dict)
    return nss
