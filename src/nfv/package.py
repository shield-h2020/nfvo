#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nfvo.osm import endpoints as osm_eps

import json
import os
import requests


def onboard_package(pkg_path):
    # TODO: Check 'package-create' endpoint to fetch
    # remote HTTP-hosted packages
    data = {"package": (os.path.split(pkg_path)[1],
            open(pkg_path, "rb"))}
    resp = requests.post(osm_eps.PKG_ONBOARD,
            headers=osm_eps.get_default_headers(),
            files=data,
            verify=False)
    output = json.loads(resp.text)
    output["package"] = pkg_path
    return output
