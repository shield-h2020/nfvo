# -*- coding: utf-8 -*-

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from functools import wraps
from flask import request
from flask import Response


def data_in_request(request_content, expected):
    if "application/json" in request.__dict__\
            .get("environ").get("CONTENT_TYPE"):
        return all(map(lambda x: x in request_content.json.keys(), expected))
    return False


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
    filtered = filter(
            lambda x: x in ["GET", "POST", "PUT", "PATCH", "DELETE"],
            actions)
    return [f for f in filtered]


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def parse_output_json(output):
    resp = Response(str(output), status=200, mimetype="application/json")
    return resp
