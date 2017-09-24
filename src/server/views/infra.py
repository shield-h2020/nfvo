#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import jsonify
from nfvi import vim
from server import endpoints


nfvo_views = Blueprint("nfvo_infra_views", __name__)


@nfvo_views.route(endpoints.NFVI_FLOW, methods=["GET"])
def fetch_devices_flowtable():
    return jsonify({})

@nfvo_views.route(endpoints.NFVI_TOPO, methods=["GET"])
def fetch_network_topology():
    return jsonify({})

@nfvo_views.route(endpoints.NFVI_NODES, methods=["GET"])
def fetch_physical_nodes():
    return jsonify({})
