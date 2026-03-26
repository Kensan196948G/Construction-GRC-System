"""ヘルスチェックビュー

DB接続・Redis接続の確認エンドポイントを提供する。
認証不要で /api/health/ からアクセス可能。
"""

from __future__ import annotations

import time
from typing import Any

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    """システムヘルスチェックエンドポイント

    GET /api/health/
    認証不要。ロードバランサやk8sプローブ用。
    """

    def get(self, request: Any) -> JsonResponse:
        """ヘルスチェックを実行し結果をJSONで返す。"""
        health: dict[str, Any] = {
            "status": "healthy",
            "checks": {},
        }
        overall_healthy = True

        # DB接続チェック
        health["checks"]["database"] = self._check_database()
        if health["checks"]["database"]["status"] != "ok":
            overall_healthy = False

        # Redis接続チェック
        health["checks"]["redis"] = self._check_redis()
        if health["checks"]["redis"]["status"] != "ok":
            overall_healthy = False

        health["status"] = "healthy" if overall_healthy else "unhealthy"
        status_code = 200 if overall_healthy else 503

        return JsonResponse(health, status=status_code)

    @staticmethod
    def _check_database() -> dict[str, Any]:
        """データベース接続を確認する。"""
        try:
            start = time.monotonic()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            elapsed_ms = round((time.monotonic() - start) * 1000, 2)
            return {"status": "ok", "response_time_ms": elapsed_ms}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}

    @staticmethod
    def _check_redis() -> dict[str, Any]:
        """Redisキャッシュ接続を確認する。"""
        try:
            start = time.monotonic()
            cache.set("_health_check", "ok", timeout=10)
            value = cache.get("_health_check")
            elapsed_ms = round((time.monotonic() - start) * 1000, 2)
            if value == "ok":
                return {"status": "ok", "response_time_ms": elapsed_ms}
            return {"status": "error", "detail": "Cache read/write mismatch"}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}
