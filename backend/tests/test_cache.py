"""キャッシュユーティリティテスト

grc/cache.py の cache_key / get_or_set / invalidate を検証。
Django の LocMemCache (デフォルト) を使用。
"""

from __future__ import annotations

from django.core.cache import cache
from django.test import TestCase

from grc.cache import (
    CACHE_PREFIX,
    CACHE_TTL,
    cache_key,
    get_or_set,
    invalidate,
    invalidate_pattern,
)


class TestCacheKey(TestCase):
    """cache_key 関数のテスト"""

    def test_single_part(self) -> None:
        result = cache_key("dashboard")
        assert result == f"{CACHE_PREFIX}:dashboard"

    def test_multiple_parts(self) -> None:
        result = cache_key("risk", "heatmap", "v1")
        assert result == f"{CACHE_PREFIX}:risk:heatmap:v1"

    def test_numeric_parts(self) -> None:
        result = cache_key("user", "42")
        assert result == f"{CACHE_PREFIX}:user:42"

    def test_prefix_is_grc(self) -> None:
        assert CACHE_PREFIX == "grc"


class TestCacheTTL(TestCase):
    """CACHE_TTL 定義のテスト"""

    def test_dashboard_ttl(self) -> None:
        assert CACHE_TTL["dashboard"] == 300

    def test_all_ttls_positive(self) -> None:
        for key, ttl in CACHE_TTL.items():
            assert ttl > 0, f"TTL for {key} must be positive"

    def test_required_keys_exist(self) -> None:
        required = {"dashboard", "compliance_rate", "control_rate", "risk_heatmap"}
        assert required.issubset(set(CACHE_TTL.keys()))


class TestGetOrSet(TestCase):
    """get_or_set 関数のテスト"""

    def setUp(self) -> None:
        cache.clear()

    def test_cache_miss_calls_callback(self) -> None:
        call_count = 0

        def callback():
            nonlocal call_count
            call_count += 1
            return {"data": "test"}

        result = get_or_set("test:key", callback, 60)
        assert result == {"data": "test"}
        assert call_count == 1

    def test_cache_hit_skips_callback(self) -> None:
        call_count = 0

        def callback():
            nonlocal call_count
            call_count += 1
            return {"data": "test"}

        # 1回目: キャッシュMISS
        get_or_set("test:key2", callback, 60)
        assert call_count == 1

        # 2回目: キャッシュHIT
        result = get_or_set("test:key2", callback, 60)
        assert result == {"data": "test"}
        assert call_count == 1  # コールバック未呼出

    def test_returns_callback_result(self) -> None:
        result = get_or_set("test:list", lambda: [1, 2, 3], 60)
        assert result == [1, 2, 3]

    def test_caches_none_value_not_stored(self) -> None:
        """Noneはキャッシュされない（cache.getがNoneをMISSと判定）"""
        call_count = 0

        def callback():
            nonlocal call_count
            call_count += 1
            return

        get_or_set("test:none", callback, 60)
        get_or_set("test:none", callback, 60)
        # Noneはcache.getで区別できないため毎回コールバック呼出
        assert call_count == 2


class TestInvalidate(TestCase):
    """invalidate 関数のテスト"""

    def setUp(self) -> None:
        cache.clear()

    def test_invalidate_removes_key(self) -> None:
        cache.set("test:remove", "value", 60)
        assert cache.get("test:remove") == "value"
        invalidate("test:remove")
        assert cache.get("test:remove") is None

    def test_invalidate_multiple_keys(self) -> None:
        cache.set("test:a", "A", 60)
        cache.set("test:b", "B", 60)
        invalidate("test:a", "test:b")
        assert cache.get("test:a") is None
        assert cache.get("test:b") is None

    def test_invalidate_nonexistent_key(self) -> None:
        """存在しないキーの無効化はエラーにならない"""
        invalidate("test:nonexistent")  # should not raise


class TestInvalidatePattern(TestCase):
    """invalidate_pattern 関数のテスト"""

    def test_pattern_without_redis_is_noop(self) -> None:
        """django-redis未使用時はスキップされる（エラーなし）"""
        invalidate_pattern("dashboard")  # should not raise
