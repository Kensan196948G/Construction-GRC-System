"""セキュリティ強化ミドルウェア

CSP、追加セキュリティヘッダー、レート制限超過ログを提供。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """追加セキュリティヘッダーを付与するミドルウェア"""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Content Security Policy
        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
            " https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' http://localhost:* ws://localhost:*; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # 追加ヘッダー
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response["X-Permitted-Cross-Domain-Policies"] = "none"

        return response


class RequestLoggingMiddleware:
    """APIリクエストのログ記録ミドルウェア"""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if request.path.startswith("/api/") and response.status_code >= 400:
            logger.warning(
                "API %s %s -> %d (user=%s, ip=%s)",
                request.method,
                request.path,
                response.status_code,
                getattr(request, "user", "anonymous"),
                request.META.get("REMOTE_ADDR", "unknown"),
            )

        return response
