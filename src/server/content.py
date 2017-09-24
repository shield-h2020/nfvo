#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import request
from flask import Response


def data_not_in_request(request, expected_data):
    return any(map(lambda x: x not in request.json.keys(), expected_data))

def error_on_unallowed_method(output):
    resp = Response(str(output), status=405, mimetype="text/plain")
    return resp

def expect_given_content(expected_content):
    best = request.accept_mimetypes \
        .best_match([expected_content, "text/html"])
    return best == expected_content

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

def filter_actions(actions):
    filtered = filter(lambda x: x in
        ["GET", "POST", "PUT", "PATCH", "DELETE"], actions)
    return [ f for f in filtered ]

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def parse_output_json(output):
    resp = Response(str(output), status=200, mimetype="application/json")
    return resp
