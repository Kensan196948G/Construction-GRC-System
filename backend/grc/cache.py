"""GRCキャッシュユーティリティ

Redis キャッシュの適用・無効化を一元管理する。
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache

logger = logging.getLogger(__name__)

# キャッシュキープレフィックス
CACHE_PREFIX = "grc"

# TTL定義（秒）
CACHE_TTL = {
    "dashboard": 300,  # 5分
    "compliance_rate": 3600,  # 1時間
    "control_rate": 3600,  # 1時間
    "risk_heatmap": 600,  # 10分
    "risk_dashboard": 300,  # 5分
    "framework_list": 86400,  # 24時間
    "nist_csf_list": 86400,  # 24時間
}


def cache_key(*parts: str) -> str:
    """キャッシュキーを生成する。"""
    return f"{CACHE_PREFIX}:" + ":".join(str(p) for p in parts)


def get_or_set(key: str, callback, ttl: int = 300) -> Any:
    """キャッシュから取得、なければcallbackで生成してセット。"""
    result = cache.get(key)
    if result is not None:
        logger.debug("Cache HIT: %s", key)
        return result
    logger.debug("Cache MISS: %s", key)
    result = callback()
    cache.set(key, result, ttl)
    return result


def invalidate(*keys: str) -> None:
    """指定キーのキャッシュを無効化する。"""
    for key in keys:
        cache.delete(key)
        logger.debug("Cache INVALIDATED: %s", key)


def invalidate_pattern(pattern: str) -> None:
    """パターンに一致するキャッシュを無効化する。"""
    try:
        from django_redis import get_redis_connection

        conn = get_redis_connection("default")
        keys = conn.keys(f"{CACHE_PREFIX}:{pattern}*")
        if keys:
            conn.delete(*keys)
            logger.debug("Cache INVALIDATED pattern: %s (%d keys)", pattern, len(keys))
    except (ImportError, Exception):
        # django-redis未使用の場合はスキップ
        logger.debug("Pattern invalidation not available")
