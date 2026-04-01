import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def grc_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data["status_code"] = response.status_code
        response.data["error_code"] = getattr(exc, "default_code", "unknown_error")
    else:
        logger.exception("Unhandled exception in %s", context.get("view", "unknown"))
        response = Response(
            {
                "detail": "予期しないエラーが発生しました。",
                "status_code": 500,
                "error_code": "internal_error",
            },
            status=500,
        )

    return response
