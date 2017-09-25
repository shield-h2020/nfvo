#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core import download
from nfvo.osm import endpoints as osm_eps
from shutil import rmtree

import json
import os
import requests


def onboard_package(pkg_path):
    """
    Uploads a VNF or NS package to the NFVO.

    @param pkg_path Local or remote path to the package
    @return output Structure with provided path and transaction ID
    """
    pkg_path_or = pkg_path
    # TODO: Check 'package-create' endpoint to fetch
    # remote HTTP-hosted packages
    if not os.path.exists(pkg_path):
        pkg_path = download.fetch_content(pkg_path)
    data = {"package": (os.path.split(pkg_path)[1],
            open(pkg_path, "rb"))}
    resp = requests.post(osm_eps.PKG_ONBOARD,
            headers=osm_eps.get_default_headers(),
            files=data,
            verify=False)
    output = json.loads(resp.text)
    output["package"] = pkg_path_or
    if pkg_path_or != pkg_path:
        rmtree(os.path.dirname(pkg_path))
    return output

def remove_package(pkg_name):
    remove_url = osm_eps.PKG_VNF_REMOVE
    if "_ns" in pkg_name:
        remove_url = osm_eps.PKG_NS_REMOVE
    remove_url = remove_url.format(pkg_name)
    resp = requests.delete(remove_url,
            headers=osm_eps.get_default_headers(),
            verify=False)
    output = json.loads(resp.text)
    return output
