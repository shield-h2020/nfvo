#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app
from nfvo.osm import endpoints as osm_eps
from templates import nfvo as nfvo_tmpl

import json
import requests


def get_vnfr_config():
    resp = requests.get(osm_eps.VNF_CATALOG_C,
        headers=osm_eps.get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def get_vnfr_running():
    resp = requests.get(osm_eps.VNF_CATALOG_O,
        headers=osm_eps.get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def fetch_running_vnsfs():
    catalog = get_vnfr_running()
    return format_vnsf_catalog(catalog)

def fill_vnf_action_request(vnfr_id=None, primitive=None, params=None):
    exec_tmpl = json.loads(nfvo_tmpl.exec_action)
    exec_tmpl_vnf = json.loads(nfvo_tmpl.exec_action_vnf)
    if vnfr_id:
        exec_tmpl_vnf["vnfr-id-ref"] = vnfr_id
    if primitive:
        exec_tmpl_vnf["vnf-primitive"][0]["name"] = primitive
#    if description:
#        exec_tmpl_vnf["name"] = description
    if params:
        exec_tmpl_vnf["vnf-primitive"][0]["parameter"] = []
        for key, val in params.items():
            d = {"name": key, "value": val}
            exec_tmpl_vnf["vnf-primitive"][0]["parameter"].append(d)
    exec_tmpl["input"]["vnf-list"] = [exec_tmpl_vnf]
    catalog = get_vnfr_running()
    nsr_id = None
    vnf_idx = None
    vnf_prim_idx = None
    for vnf in catalog["collection"]["vnfr:vnfr"]:
        if vnfr_id == vnf["id"]:
            nsr_id = vnf["nsr-id-ref"]
            vnf_idx = vnf["member-vnf-index-ref"]
            prims = vnf["vnf-configuration"]["service-primitive"]
            for pos, prim in enumerate(prims):
                if prim["name"] == primitive:
                    vnf_prim_idx = pos
                    break
    exec_tmpl["input"]["nsr_id_ref"] = nsr_id
    exec_tmpl["input"]["vnf-list"][0]["member_vnf_index_ref"] = vnf_idx
    exec_tmpl["input"]["vnf-list"][0]["vnf-primitive"][0]["index"] = vnf_prim_idx
    output = exec_action_on_vnf(exec_tmpl)
    # Keep track of remote action per vNSF
    #current_app.mongo.store_vnf_action(vnfr_id, primitive, description, params)
    current_app.mongo.store_vnf_action(vnfr_id, primitive, params)
    return output

def format_vnsf_catalog(catalog):
    vnsfs = []
    for vnf in catalog["collection"]["vnfr:vnfr"]:
        vnsf_dict = {"vnf_id": vnf.get("id"),
            "name": vnf.get("name"),
            "vendor": vnf.get("vendor"),
            "ns_id": vnf.get("nsr-id-ref")}
        vnsfs.append(vnsf_dict)
    return vnsfs

def exec_action_on_vnf(payload):
    resp = requests.post(osm_eps.VNF_ACTION_EXEC,
        headers=osm_eps.post_default_headers(),
        data=json.dumps(payload),
        verify=False)
    output = json.loads(resp.text)
    return output

def submit_action_request(vnfr_id=None, action=None, params=list()):
    return fill_vnf_action_request(vnfr_id, action, params)
