"""統合通知サービステスト

NotificationService の Slack / Email / ログ通知をモックで検証。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from apps.reports.notification_service import NotificationService


class TestNotificationServiceNotify(TestCase):
    """notify メソッドのテスト"""

    def test_log_always_enabled(self) -> None:
        """Slack/Email未設定でもログ通知は常に成功"""
        results = NotificationService.notify("test.event", "Test Title", "Test message")
        assert results["log"] is True

    def test_no_slack_no_email(self) -> None:
        """Slack/Email未設定時はそれらのキーが結果に含まれない"""
        results = NotificationService.notify("test.event", "Test", "msg")
        assert "slack" not in results
        assert "email" not in results

    @override_settings(GRC_SLACK_WEBHOOK_URL="https://hooks.slack.com/test")
    @patch("apps.reports.notification_service.requests.post")
    def test_slack_notification_success(self, mock_post: MagicMock) -> None:
        """Slack通知成功時はslack=True"""
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        results = NotificationService.notify("test.event", "Title", "Message")
        assert results["slack"] is True
        mock_post.assert_called_once()

    @override_settings(GRC_SLACK_WEBHOOK_URL="https://hooks.slack.com/test")
    @patch("apps.reports.notification_service.requests.post")
    def test_slack_notification_failure(self, mock_post: MagicMock) -> None:
        """Slack通知失敗時はslack=False"""
        mock_post.side_effect = Exception("Connection refused")

        results = NotificationService.notify("test.event", "Title", "Message")
        assert results["slack"] is False

    @override_settings(
        GRC_NOTIFICATION_EMAILS=["admin@example.com"],
        DEFAULT_FROM_EMAIL="noreply@grc.example.com",
    )
    @patch("apps.reports.notification_service.send_mail")
    def test_email_notification_success(self, mock_send: MagicMock) -> None:
        """メール通知成功時はemail=True"""
        results = NotificationService.notify("test.event", "Title", "Message")
        assert results["email"] is True
        mock_send.assert_called_once()

    @override_settings(
        GRC_NOTIFICATION_EMAILS=["admin@example.com"],
        DEFAULT_FROM_EMAIL="noreply@grc.example.com",
    )
    @patch("apps.reports.notification_service.send_mail")
    def test_email_notification_failure(self, mock_send: MagicMock) -> None:
        """メール通知失敗時はemail=False"""
        mock_send.side_effect = Exception("SMTP error")

        results = NotificationService.notify("test.event", "Title", "Message")
        assert results["email"] is False

    @override_settings(
        GRC_NOTIFICATION_EMAILS="admin@example.com,ops@example.com",
        DEFAULT_FROM_EMAIL="noreply@grc.example.com",
    )
    @patch("apps.reports.notification_service.send_mail")
    def test_email_csv_string_recipients(self, mock_send: MagicMock) -> None:
        """カンマ区切り文字列の宛先がリストに変換される"""
        NotificationService.notify("test.event", "Title", "Message")
        call_args = mock_send.call_args
        recipients = call_args[0][3]  # 第4引数: recipient_list
        assert len(recipients) == 2
        assert "admin@example.com" in recipients
        assert "ops@example.com" in recipients


class TestNotificationServiceSlackPayload(TestCase):
    """Slackペイロードの構造テスト"""

    @override_settings(GRC_SLACK_WEBHOOK_URL="https://hooks.slack.com/test")
    @patch("apps.reports.notification_service.requests.post")
    def test_slack_payload_has_attachments(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        NotificationService.notify("test.event", "Title", "Message", severity="critical")
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"]
        assert "attachments" in payload
        attachment = payload["attachments"][0]
        assert attachment["color"] == "#D32F2F"  # critical color

    @override_settings(GRC_SLACK_WEBHOOK_URL="https://hooks.slack.com/test")
    @patch("apps.reports.notification_service.requests.post")
    def test_slack_severity_colors(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        color_map = {
            "critical": "#D32F2F",
            "high": "#FF6F00",
            "warning": "#FFA000",
            "info": "#1565C0",
            "success": "#388E3C",
        }
        for severity, expected_color in color_map.items():
            NotificationService.notify("test", "T", "M", severity=severity)
            payload = mock_post.call_args[1]["json"]
            assert payload["attachments"][0]["color"] == expected_color


class TestNotificationServiceConvenienceMethods(TestCase):
    """便利メソッドのテスト"""

    def test_notify_risk_critical(self) -> None:
        results = NotificationService.notify_risk_critical("RISK-001", "Critical Risk")
        assert results["log"] is True

    def test_notify_cap_overdue(self) -> None:
        results = NotificationService.notify_cap_overdue("F-001", 5)
        assert results["log"] is True

    def test_notify_compliance_degraded(self) -> None:
        results = NotificationService.notify_compliance_degraded("ISO27001", 95.0, 80.0)
        assert results["log"] is True

    def test_notify_audit_completed(self) -> None:
        results = NotificationService.notify_audit_completed("AUD-001", 3)
        assert results["log"] is True

    def test_notify_daily_digest(self) -> None:
        summary = {
            "risks": 50,
            "critical_risks": 2,
            "compliance_rate": 85,
            "open_findings": 10,
        }
        results = NotificationService.notify_daily_digest(summary)
        assert results["log"] is True
