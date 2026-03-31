"""GRCシステム共通ミドルウェア"""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("grc.audit")


class AuditLogMiddleware:
    """API操作の監査ログミドルウェア

    全APIリクエストを記録する。ISO27001 A.8.15「ログ記録」の証跡。
    """

    EXCLUDED_PATHS = {"/api/health/", "/admin/jsi18n/", "/static/", "/media/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if any(request.path.startswith(p) for p in self.EXCLUDED_PATHS):
            return self.get_response(request)

        start_time = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        if request.path.startswith("/api/"):
            self._log_api_request(request, response, duration_ms)

        return response

    def _log_api_request(self, request: HttpRequest, response: HttpResponse, duration_ms: float) -> None:
        user = getattr(request, "user", None)
        username = user.username if user and user.is_authenticated else "anonymous"

        log_data = {
            "method": request.method,
            "path": request.path,
            "user": username,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "ip": self._get_client_ip(request),
        }

        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            logger.info("API_WRITE: %s", json.dumps(log_data, ensure_ascii=False))
        else:
            logger.debug("API_READ: %s", json.dumps(log_data, ensure_ascii=False))

    def _get_client_ip(self, request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
