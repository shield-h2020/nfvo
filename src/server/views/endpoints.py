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


from flask import Blueprint
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from server.endpoints import VnsfoEndpoints as endpoints_s

nfvo_views = Blueprint("nfvo_endpoint_views", __name__)
nfvo_endpoints = endpoints_s()


@nfvo_views.route(endpoints_s.ROOT, methods=["GET"])
def endpoints():
    ep_content = nfvo_endpoints.api_endpoints()
    if "<html" in ep_content:
        return ep_content
    return HttpResponse.json(HttpCode.OK, ep_content)
