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


from flask import Response
from werkzeug.exceptions import HTTPException


class ExceptionCode:

    CODE_BAD_REQUEST = 400
    CODE_TEAPOT = 418

    IMPROPER_USAGE = "Improper usage"
    INVALID_CONTENT_TYPE = "Invalid Content-Type"


class Exception:

    @staticmethod
    def abort(error_code, error_msg, error_det=None):
        error_details = "Error: {}".format(error_code)
        if error_det is not None:
            error_details = "{}\t{}: {}".format(
                    error_details, error_msg, error_det)
        response = Response(response=error_details, status=error_code)
        raise HTTPException(response=response)

    @staticmethod
    def improper_usage(error_msg):
        return Exception.abort(
                ExceptionCode.CODE_TEAPOT, ExceptionCode.IMPROPER_USAGE,
                error_msg)

    @staticmethod
    def invalid_content_type(error_msg):
        return Exception.abort(
                ExceptionCode.CODE_BAD_REQUEST,
                ExceptionCode.INVALID_CONTENT_TYPE,
                error_msg)