#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nfvo.osm import endpoints as osm_eps

import json
import requests


def get_vim_name_by_uuid(vim_list, uuid):
    for dc in vim_list:
        if dc.get("uuid") == uuid:
            return dc.get("name")
    return ""

def get_vim_list():
    resp = requests.get(osm_eps.VIM_LIST_O,
        headers=osm_eps.get_default_headers(),
        verify=False)
    output = json.loads(resp.text)
    output = output.get("collection") \
        .get("rw-launchpad:datacenters")[0] \
        .get("ro-accounts")[0] \
        .get("datacenters")
#    output = map(lambda x: {"name": x.get("name") }, output)
    return output
