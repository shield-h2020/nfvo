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


from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from enum import Enum
# from flask import Response
from werkzeug.exceptions import HTTPException


class ExceptionCode(Enum):

    IMPROPER_USAGE = "Improper usage"
    INVALID_CONTENT_TYPE = "Invalid Content-Type"
    NOT_IMPLEMENTED = "Method not implemented"

    def __get__(self, *args, **kwargs):
        return self.value

    def __str__(self):
        return str(self.value)


class Exception:

    @staticmethod
    def abort(error_code, error_msg, error_det=None):
        error_details = "{0}: {1}".format(error_code, error_msg)
        error = {"error": error_details}
        if error_det is not None:
            error.update({"reason": error_det})
        response = HttpResponse.json(error_code, error)
        raise HTTPException(response=response)

    @staticmethod
    def improper_usage(error_msg=None):
        return Exception.abort(
            HttpCode.TEAPOT,
            ExceptionCode.IMPROPER_USAGE,
            error_msg)

    @staticmethod
    def invalid_content_type(error_msg=None):
        return Exception.abort(
            HttpCode.UNSUP_MEDIA,
            ExceptionCode.INVALID_CONTENT_TYPE,
            error_msg)

    @staticmethod
    def not_implemented(error_msg=None):
        return Exception.abort(
            HttpCode.NOT_IMPL,
            ExceptionCode.NOT_IMPLEMENTED,
            error_msg)
