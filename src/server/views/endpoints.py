#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from server import endpoints as endpoints_s


nfvo_views = Blueprint("nfvo_endpoint_views", __name__)


@nfvo_views.route(endpoints_s.ROOT, methods=["GET"])
def endpoints():
    return endpoints_s.api_endpoints()
