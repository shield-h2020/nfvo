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
            error_details = "{}\t{}: {}".format(error_details, error_msg, error_det)
        response = Response(response=error_details, status=error_code)
        raise HTTPException(response=response)

    @staticmethod
    def improper_usage(error_msg):
        return Exception.abort(ExceptionCode.CODE_TEAPOT, ExceptionCode.IMPROPER_USAGE, error_msg)

    @staticmethod
    def invalid_content_type(error_msg):
        return Exception.abort(CODE_BAD_REQUEST, INVALID_CONTENT_TYPE, error_msg)

