#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
from nfv import ns
from server import content
from server import endpoints


nfvo_views = Blueprint("nfvo_ns_views", __name__)


@nfvo_views.route(endpoints.NS_C_NSS, methods=["GET"])
def fetch_config_nss():
    return jsonify(ns.fetch_config_nss())
