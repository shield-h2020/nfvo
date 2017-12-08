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
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from enum import Enum
from werkzeug.exceptions import HTTPException


class ExceptionCode(Enum):

    IMPROPER_USAGE = "Improper usage"
    INTERNAL_ERROR = "Internal server error"
    INVALID_CONTENT_TYPE = "Invalid Content-Type"
    NOT_FOUND = "Method not found"
    NOT_IMPLEMENTED = "Method not implemented"

    def __get__(self, *args, **kwargs):
        return self.value

    def __str__(self):
        return str(self.value)


class Exception:

    @staticmethod
    def abort(error_code, error_msg, error_det=None):
        response = Exception.inform(error_code, error_msg, error_det)
        raise HTTPException(response=response)

    @staticmethod
    def inform(error_code, error_msg, error_det=None):
        error_details = "{0}: {1}".format(error_code, error_msg)
        error = {"error": error_details}
        if error_det is not None:
            error.update({"reason": str(error_det)})
        error = jsonify(error).response
        if len(error) > 0:
            error = error[0]
        return HttpResponse.json(error_code, error)

    @staticmethod
    def improper_usage(error_msg=None):
        return Exception.abort(
            HttpCode.TEAPOT,
            ExceptionCode.IMPROPER_USAGE,
            error_msg)

    @staticmethod
    def internal_error(error_msg=None):
        return Exception.inform(
            HttpCode.INTERNAL_ERROR,
            ExceptionCode.INTERNAL_ERROR,
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

    @staticmethod
    def not_found(error_msg=None):
        return Exception.inform(
            HttpCode.NOT_FOUND,
            ExceptionCode.NOT_FOUND,
            error_msg)
