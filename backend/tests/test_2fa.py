"""TOTP 2FA テスト."""

from __future__ import annotations

from django.test import TestCase
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import GRCUser  # noqa: E402
from apps.accounts.totp import generate_totp_secret


@pytest.mark.django_db
class TestTOTPSetup(TestCase):
    def setUp(self):
        self.user = GRCUser.objects.create_user(
            username="testuser2fa",
            password="testpass123",
            role=GRCUser.Role.GENERAL,
        )
        self.client = APIClient()
        resp = self.client.post("/api/v1/auth/token/", {"username": "testuser2fa", "password": "testpass123"})
        self.token = resp.data.get("access", "")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_totp_setup_generates_secret(self):
        resp = self.client.post("/api/v1/auth/2fa/setup/")
        assert resp.status_code == 200
        assert "secret" in resp.data
        assert len(resp.data["secret"]) == 32

    def test_totp_verify_invalid_token_returns_400(self):
        self.client.post("/api/v1/auth/2fa/setup/")
        resp = self.client.post("/api/v1/auth/2fa/verify/", {"token": "000000"})
        assert resp.status_code == 400

    def test_totp_disable_clears_secret(self):
        self.user.totp_secret = generate_totp_secret()
        self.user.totp_enabled = True
        self.user.save()
        resp = self.client.post("/api/v1/auth/2fa/disable/")
        assert resp.status_code == 200
        self.user.refresh_from_db()
        assert not self.user.totp_enabled
        assert self.user.totp_secret == ""

    def test_totp_verify_without_setup_returns_400(self):
        resp = self.client.post("/api/v1/auth/2fa/verify/", {"token": "123456"})
        assert resp.status_code == 400
        assert "error" in resp.data

    def test_totp_setup_idempotent(self):
        """2回セットアップしても秘密鍵は変わらない."""
        resp1 = self.client.post("/api/v1/auth/2fa/setup/")
        secret1 = resp1.data["secret"]
        resp2 = self.client.post("/api/v1/auth/2fa/setup/")
        secret2 = resp2.data["secret"]
        assert secret1 == secret2
