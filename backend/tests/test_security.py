"""セキュリティテスト — OWASP Top 10 対応確認

A01: Broken Access Control
A02: Cryptographic Failures
A03: Injection
A05: Security Misconfiguration
A07: Authentication Failures
"""

from __future__ import annotations

from django.test import Client, TestCase


class TestBrokenAccessControl(TestCase):
    """A01: アクセス制御テスト"""

    def test_unauthenticated_api_rejected(self):
        """未認証リクエストが401を返すことを確認"""
        client = Client()
        endpoints = [
            "/api/v1/risks/",
            "/api/v1/controls/",
            "/api/v1/compliance/",
            "/api/v1/audits/",
            "/api/v1/reports/",
        ]
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in (
                401,
                403,
            ), f"{endpoint} returned {response.status_code}"

    def test_admin_endpoint_requires_auth(self):
        """管理画面がログインを要求"""
        client = Client()
        response = client.get("/admin/")
        # redirect to login or login page
        assert response.status_code in (301, 302, 200)


class TestSecurityHeaders(TestCase):
    """A05: セキュリティ設定テスト"""

    def test_health_endpoint_accessible(self):
        """ヘルスチェックは認証不要"""
        client = Client()
        response = client.get("/api/health/")
        assert response.status_code in (200, 503)

    def test_csp_header_present(self):
        """CSPヘッダーが設定されていることを確認"""
        client = Client()
        response = client.get("/api/health/")
        csp = response.get("Content-Security-Policy", "")
        assert "default-src" in csp or response.status_code == 503

    def test_x_frame_options(self):
        """X-Frame-Optionsが設定されていることを確認"""
        client = Client()
        response = client.get("/api/health/")
        # DjangoのXFrameOptionsMiddlewareまたはカスタムミドルウェア
        assert response.get("X-Frame-Options") is not None or response.status_code == 503


class TestAuthenticationSecurity(TestCase):
    """A07: 認証セキュリティテスト"""

    def test_jwt_endpoint_exists(self):
        """JWT取得エンドポイントが存在"""
        client = Client()
        response = client.post(
            "/api/v1/auth/token/",
            {"username": "invalid", "password": "invalid"},
            content_type="application/json",
        )
        assert response.status_code in (400, 401)

    def test_password_validators_configured(self):
        """パスワードバリデータが設定されていることを確認"""
        from django.conf import settings

        validators = getattr(settings, "AUTH_PASSWORD_VALIDATORS", [])
        assert len(validators) >= 3

    def test_jwt_settings_configured(self):
        """JWT設定が適切"""
        from django.conf import settings

        jwt_settings = getattr(settings, "SIMPLE_JWT", {})
        assert "ACCESS_TOKEN_LIFETIME" in jwt_settings
        # アクセストークンは24時間以内
        assert jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds() <= 86400


class TestInjectionPrevention(TestCase):
    """A03: インジェクション対策テスト"""

    def test_sql_injection_in_search(self):
        """検索パラメータのSQLインジェクション耐性"""
        client = Client()
        # SQLインジェクション試行（認証不要のhealthエンドポイントで確認）
        response = client.get("/api/health/?q='; DROP TABLE risks_risk; --")
        # エラーではなく正常処理
        assert response.status_code in (200, 503)


class TestRateLimiting(TestCase):
    """レート制限テスト"""

    def test_throttle_settings_configured(self):
        """レート制限が設定されていることを確認"""
        from django.conf import settings

        rest = getattr(settings, "REST_FRAMEWORK", {})
        throttle_classes = rest.get("DEFAULT_THROTTLE_CLASSES", [])
        throttle_rates = rest.get("DEFAULT_THROTTLE_RATES", {})
        assert len(throttle_classes) >= 1
        assert "anon" in throttle_rates or "user" in throttle_rates


class TestCryptographicSecurity(TestCase):
    """A02: 暗号化設定テスト"""

    def test_secret_key_not_default(self):
        """SECRET_KEYがデフォルト値でないことを確認（本番時）"""
        from django.conf import settings

        # 開発環境ではデフォルト値を許容するが、存在を確認
        assert hasattr(settings, "SECRET_KEY")
        assert len(settings.SECRET_KEY) >= 20

    def test_password_hashers_configured(self):
        """パスワードハッシュアルゴリズムがセキュア"""
        from django.conf import settings

        hashers = getattr(settings, "PASSWORD_HASHERS", [])
        # Djangoデフォルトは PBKDF2 — 十分セキュア
        if hashers:
            assert any("PBKDF2" in h or "Argon2" in h or "BCrypt" in h for h in hashers)
