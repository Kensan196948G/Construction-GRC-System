"""Docker Compose環境でAPIエンドポイントを直接叩く統合テスト。
実行前提: docker compose up -d でサービスが起動済みであること。
SKIP_DOCKER_INTEGRATION=1 でスキップ。
"""
from __future__ import annotations
import os
import pytest
import requests

BASE_URL = os.getenv("INTEGRATION_BASE_URL", "http://localhost:8000")

pytestmark = pytest.mark.skipif(
    os.getenv("SKIP_DOCKER_INTEGRATION") == "1",
    reason="Docker統合テストはスキップ設定済み",
)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        resp = requests.get(f"{BASE_URL}/api/health/", timeout=10)
        assert resp.status_code == 200

    def test_health_db_connected(self):
        resp = requests.get(f"{BASE_URL}/api/health/", timeout=10)
        data = resp.json()
        assert data.get("database") == "ok", f"DB未接続: {data}"

    def test_health_redis_connected(self):
        resp = requests.get(f"{BASE_URL}/api/health/", timeout=10)
        data = resp.json()
        assert data.get("redis") == "ok", f"Redis未接続: {data}"


class TestAuthEndpoints:
    def test_token_obtain_requires_credentials(self):
        resp = requests.post(
            f"{BASE_URL}/api/v1/auth/token/",
            json={"username": "nouser", "password": "nopass"},
            timeout=10,
        )
        assert resp.status_code == 401

    def test_profile_requires_auth(self):
        resp = requests.get(f"{BASE_URL}/api/v1/auth/profile/", timeout=10)
        assert resp.status_code == 401


class TestAPIEndpoints:
    def _get_token(self) -> str:
        resp = requests.post(
            f"{BASE_URL}/api/v1/auth/token/",
            json={
                "username": os.getenv("TEST_ADMIN_USER", "admin"),
                "password": os.getenv("TEST_ADMIN_PASSWORD", "adminpass"),
            },
            timeout=10,
        )
        if resp.status_code != 200:
            pytest.skip("管理者ユーザーが未作成のためスキップ")
        return resp.json()["access"]

    def test_risks_list_requires_auth(self):
        resp = requests.get(f"{BASE_URL}/api/v1/risks/", timeout=10)
        assert resp.status_code == 401

    def test_risks_list_with_auth(self):
        token = self._get_token()
        resp = requests.get(
            f"{BASE_URL}/api/v1/risks/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert resp.status_code == 200
        assert "results" in resp.json()
