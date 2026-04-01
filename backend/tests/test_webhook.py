"""Webhook通知サービステスト

WebhookNotifier の各メソッドを unittest.mock.patch で検証。
外部HTTP通信は全てモック化。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.reports.webhook import WebhookNotifier


class TestWebhookNotifierSendNotification(TestCase):
    """send_notification メソッドのテスト"""

    def test_no_url_returns_false(self) -> None:
        """Webhook URLが未設定の場合はFalseを返す"""
        result = WebhookNotifier.send_notification("test.event", {"key": "value"})
        assert result is False

    @patch("apps.reports.webhook.requests.post")
    def test_explicit_url_sends_post(self, mock_post: MagicMock) -> None:
        """明示的なURLにPOSTリクエストを送信する"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        result = WebhookNotifier.send_notification(
            "test.event",
            {"key": "value"},
            webhook_url="https://example.com/webhook",
        )
        assert result is True
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs[1]["json"]["event_type"] == "test.event"
        assert call_kwargs[1]["json"]["payload"] == {"key": "value"}
        assert call_kwargs[1]["json"]["system"] == "Construction-GRC-System"

    @override_settings(GRC_WEBHOOK_URL="https://example.com/webhook")
    @patch("apps.reports.webhook.requests.post")
    def test_settings_url_used_when_no_explicit_url(self, mock_post: MagicMock) -> None:
        """settings.GRC_WEBHOOK_URL を使用する"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        result = WebhookNotifier.send_notification("test.event", {})
        assert result is True
        mock_post.assert_called_once()

    @patch("apps.reports.webhook.requests.post")
    def test_request_exception_returns_false(self, mock_post: MagicMock) -> None:
        """requests例外発生時はFalseを返す"""
        import requests

        mock_post.side_effect = requests.RequestException("Connection error")

        result = WebhookNotifier.send_notification(
            "test.event",
            {},
            webhook_url="https://example.com/webhook",
        )
        assert result is False

    @patch("apps.reports.webhook.requests.post")
    def test_payload_includes_timestamp(self, mock_post: MagicMock) -> None:
        """送信データにtimestampが含まれる"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        WebhookNotifier.send_notification(
            "test.event",
            {},
            webhook_url="https://example.com/webhook",
        )
        call_kwargs = mock_post.call_args
        assert "timestamp" in call_kwargs[1]["json"]


class TestWebhookNotifierConvenienceMethods(TestCase):
    """便利メソッドのテスト"""

    @patch("apps.reports.webhook.requests.post")
    def test_notify_risk_created(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        with self.settings(GRC_WEBHOOK_URL="https://example.com/webhook"):
            result = WebhookNotifier.notify_risk_created({"risk_id": "RISK-001"})
        assert result is True
        payload = mock_post.call_args[1]["json"]
        assert payload["event_type"] == "risk.created"

    @patch("apps.reports.webhook.requests.post")
    def test_notify_risk_level_changed(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        with self.settings(GRC_WEBHOOK_URL="https://example.com/webhook"):
            result = WebhookNotifier.notify_risk_level_changed("RISK-001", "MEDIUM", "HIGH")
        assert result is True
        payload = mock_post.call_args[1]["json"]
        assert payload["event_type"] == "risk.level_changed"
        assert payload["payload"]["old_level"] == "MEDIUM"
        assert payload["payload"]["new_level"] == "HIGH"

    @patch("apps.reports.webhook.requests.post")
    def test_notify_compliance_status_changed(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        with self.settings(GRC_WEBHOOK_URL="https://example.com/webhook"):
            result = WebhookNotifier.notify_compliance_status_changed("REQ-001", "unknown", "compliant")
        assert result is True

    @patch("apps.reports.webhook.requests.post")
    def test_notify_audit_finding_created(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        with self.settings(GRC_WEBHOOK_URL="https://example.com/webhook"):
            result = WebhookNotifier.notify_audit_finding_created({"finding_id": "F-001"})
        assert result is True

    @patch("apps.reports.webhook.requests.post")
    def test_notify_stable_achieved(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        with self.settings(GRC_WEBHOOK_URL="https://example.com/webhook"):
            result = WebhookNotifier.notify_stable_achieved(pr_number=42, run_count=3)
        assert result is True
        payload = mock_post.call_args[1]["json"]
        assert payload["event_type"] == "ci.stable_achieved"
        assert payload["payload"]["pr"] == 42

    def test_notify_risk_created_no_url(self) -> None:
        """URL未設定時はFalse"""
        result = WebhookNotifier.notify_risk_created({"risk_id": "RISK-001"})
        assert result is False
