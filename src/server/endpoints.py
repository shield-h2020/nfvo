#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import current_app
from flask import jsonify
from flask import request
#from flask import request_finished
from flask import url_for
from gui import swagger
from server import content
from server import useragent


NFVI = "/nfvi/"
NFVI_C = "{}config/".format(NFVI)
NFVI_C_NS = "{}nss".format(NFVI_C)
NFVI_FLOW = "{}flowtable".format(NFVI)
NFVI_NODES = "{}nodes".format(NFVI)
NFVI_R = "{}running/".format(NFVI)
NFVI_TOPO = "{}topology".format(NFVI)
ROOT = "/"
VIM = "/vim/"
VIM_IMAGE = "{}vnsf_image".format(VIM)
VNSF = "/vnsf/"
VNSF_ACTION_EXEC = "{}action".format(VNSF)
VNSF_ACTION_STATUS = "{}<vnsf_id>/action/<action_id>".format(VNSF)
VNSF_VNSF_TENANT = "{}vnsfs/<tenant_id>".format(NFVI_R)
VNSF_VNSFS = "{}vnsfs".format(VNSF)


def api_endpoints():
    user_agent = useragent.get_user_agent(request)
    if "curl" in user_agent:
        endpoints = get_endpoints(current_app)
        output = dict()
        output["endpoints"] = endpoints
        #return methods.parse_output_json(output)
        return jsonify(output)
    else:
        return swagger.generate_swagger_docs()

def get_endpoints(app):
    links = []
    for rule in app.url_map.iter_rules():
        if "static" in rule.endpoint:
            break
        if content.has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
        else:
            url = rule.rule
        links.append({"endpoint": url, "methods": content.filter_actions(rule.methods)})
    return links
