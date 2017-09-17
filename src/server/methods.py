#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.config import FullConfParser
from flask import current_app
from flask import request
from flask import Response
from flask import url_for
from functools import wraps
from templates import nfvo as nfvo_tmpl

import json
import requests


#NFVO_ENDPOINT = "10.148.131.134"
NFVO_ENDPOINT = "10.101.10.100"
NFVO_PORT = "8008"


def load_config():
    config = FullConfParser()
    # General NFVO data
    nfvo_category = config.get("nfvo.conf")
    nfvo_general = nfvo_category.get("general")
    nfvo_host = nfvo_general.get("host", NFVO_ENDPOINT)
    nfvo_port = nfvo_general.get("port", NFVO_PORT)
    return {"nfvo_host": nfvo_host,
            "nfvo_port": nfvo_port}

cfg = load_config()
NFVO_ENDPOINT = cfg.get("nfvo_host")
NFVO_PORT = cfg.get("nfvo_port")


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def filter_actions(actions):
    filtered = filter(lambda x: x in
        ["GET", "POST", "PUT", "PATCH", "DELETE"], actions)
    return [ f for f in filtered ]

def get_endpoints(app):
    links = []
    for rule in app.url_map.iter_rules():
        if "static" in rule.endpoint:
            break
        if has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        else:
            url = rule.rule
        links.append({"endpoint": url, "methods": filter_actions(rule.methods)})
    return links


def get_nsr_config():
    resp = requests.get("https://{}:{}/v1/api/config/nsd-catalog/nsd"\
        .format(NFVO_ENDPOINT, NFVO_PORT), headers=get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def get_vnfr_config():
    resp = requests.get("https://{}:{}/api/config/vnfr-catalog/vnfr"\
        .format(NFVO_ENDPOINT, NFVO_PORT), headers=get_default_headers(),
        verify=False)
    print(resp.text)
    output = json.loads(resp.text)
    return output

def get_nsr_running():
    resp = requests.get("https://{}:{}/api/operational/nsd-catalog/nsd"\
        .format(NFVO_ENDPOINT, NFVO_PORT), headers=get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def get_vnfr_running():
    resp = requests.get("https://{}:{}/api/operational/vnfr-catalog/vnfr"\
        .format(NFVO_ENDPOINT, NFVO_PORT), headers=get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    return output

def post_action_to_vnf(payload):
    resp = requests.post("https://{}:{}/api/operations/exec-ns-service-primitive"\
        .format(NFVO_ENDPOINT, NFVO_PORT), headers=post_default_headers(),
        data=json.dumps(payload),
        verify=False)
    output = json.loads(resp.text)
    return output

def format_ns_catalog(catalog):
    nss = []
    for ns in catalog["collection"]["nsd:nsd"]:
        ns_dict = {"ns_id": ns.get("id", None),
            "name": ns.get("name"),
            "vendor": ns.get("vendor")}
        nss.append(ns_dict)
    return nss

def format_vnsf_catalog(catalog):
    vnsfs = []
    for vnf in catalog["collection"]["vnfr:vnfr"]:
        vnsf_dict = {"vnf_id": vnf.get("id"),
            "name": vnf.get("name"),
            "vendor": vnf.get("vendor"),
            "ns_id": vnf.get("nsr-id-ref")}
        vnsfs.append(vnsf_dict)
    return vnsfs

def fetch_config_nss():
    catalog = get_nsr_config()
    return format_ns_catalog(catalog)

#def fetch_running_nss():
#    catalog = get_nsr_running()
#    return format_ns_catalog(catalog)

#def fetch_config_vnsfs():
#    catalog = get_vnfr_running()
#    return format_vnsf_catalog(catalog)

def fetch_running_vnsfs():
    catalog = get_vnfr_running()
    return format_vnsf_catalog(catalog)

#def fill_vnf_action_request(vnfr_id=None, primitive=None, description=None, params=None):
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
    output = post_action_to_vnf(exec_tmpl)
    # Keep track of remote action per vNSF
    #current_app.mongo.store_vnf_action(vnfr_id, primitive, description, params)
    current_app.mongo.store_vnf_action(vnfr_id, primitive, params)
    return output

#def submit_action_request(vnfr_id=None, action=None, description=None, params=list()):
def submit_action_request(vnfr_id=None, action=None, params=list()):
#    return fill_vnf_action_request(vnfr_id, action, description, params)
    return fill_vnf_action_request(vnfr_id, action, params)


def data_not_in_request(request, expected_data):
    return any(map(lambda x: x not in request.json.keys(), expected_data))

def parse_output_json(output):
    resp = Response(str(output), status=200, mimetype="application/json")
    return resp

def error_on_unallowed_method(output):
    resp = Response(str(output), status=405, mimetype="text/plain")
    return resp


# Specific to vNSFO implementation

def rest_auth_headers():
    return {"Authorization": "Basic YWRtaW46YWRtaW4="}

def get_default_headers():
    headers = rest_auth_headers()
    headers.update({"Accept": "application/vnd.yang.collection+json"})
    return headers

def post_default_headers():
    headers = rest_auth_headers()
    headers.update({"Content-Type": "application/vnd.yang.data+json",
        "Accept": "application/vnd.yang.data+json"})
    return headers

def expect_given_content(expected_content):
    best = request.accept_mimetypes \
        .best_match([expected_content, "text/html"])
    return best == expected_content

def get_user_agent(request):
    user_agent = ""
    try:
        user_agent = request.environ["HTTP_USER_AGENT"]
    except:
        pass
    return user_agent


def expect_json_content(func):
    """
    Enforce check of Content-Type header to meet 'application/json'.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if expect_given_content("application/json"):
            return func(*args, **kwargs)
        else:
            return error_on_unallowed_method("Content-Type not expected")
    return wrapper
