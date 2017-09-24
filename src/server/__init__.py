#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.config import FullConfParser


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
