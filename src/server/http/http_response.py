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


from flask import jsonify
from flask import Response


class HttpResponse:

    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_TEXT = "text/html"

    @staticmethod
    def set_content_type(content_type):
        return {"Content-Type": content_type}

    @staticmethod
    def json(status_code, status_msg):
        if not isinstance(status_msg, str):
            try:
                status_msg = jsonify(status_msg).response
            except TypeError:
                status_msg = str(status_msg)
        headers = HttpResponse.set_content_type(
            HttpResponse.CONTENT_TYPE_JSON)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def json_unformatted(status_code, status_msg):
        headers = HttpResponse.set_content_type(
            HttpResponse.CONTENT_TYPE_JSON)
        try:
            import json
            status_msg = json.dumps(status_msg)
        except:
            status_msg = str(status_msg)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def text(status_code, status_msg):
        headers = HttpResponse.set_content_type(
            HttpResponse.CONTENT_TYPE_TEXT)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def generic(status_code, status_msg, headers):
        return Response(status=status_code, response=status_msg,
                        headers=headers)
