"""レポートスケジュール機能テスト."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import GRCUser


@pytest.mark.django_db
class TestScheduledReport(TestCase):
    def setUp(self):
        self.user = GRCUser.objects.create_user(
            username="reportadmin",
            password="testpass123",
            role=GRCUser.Role.GRC_ADMIN,
        )
        self.client = APIClient()
        resp = self.client.post("/api/v1/auth/token/", {"username": "reportadmin", "password": "testpass123"})
        self.token = resp.data.get("access", "")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_scheduled_report_model_creates(self):
        from apps.reports.models import ScheduledReport

        schedule = ScheduledReport.objects.create(
            name="週次リスクレポート",
            report_type="risk_trend",
            frequency=ScheduledReport.Frequency.WEEKLY,
            recipients=["admin@example.com"],
            created_by=self.user,
        )
        assert schedule.name == "週次リスクレポート"
        assert str(schedule) == "週次リスクレポート (weekly)"

    def test_scheduled_report_model_defaults(self):
        from apps.reports.models import ScheduledReport

        schedule = ScheduledReport.objects.create(
            name="テストスケジュール",
            report_type="grc_dashboard",
            created_by=self.user,
        )
        assert schedule.is_active is True
        assert schedule.frequency == "weekly"
        assert schedule.recipients == []

    def test_scheduled_report_uuid_primary_key(self):
        from apps.reports.models import ScheduledReport

        schedule = ScheduledReport.objects.create(
            name="UUIDテスト",
            report_type="soa",
            created_by=self.user,
        )
        assert schedule.pk is not None
        assert len(str(schedule.pk)) == 36  # UUID format

    def test_scheduled_report_frequency_choices(self):
        from apps.reports.models import ScheduledReport

        daily = ScheduledReport.objects.create(
            name="日次レポート",
            report_type="compliance_status",
            frequency=ScheduledReport.Frequency.DAILY,
            created_by=self.user,
        )
        monthly = ScheduledReport.objects.create(
            name="月次レポート",
            report_type="iso27001_annual",
            frequency=ScheduledReport.Frequency.MONTHLY,
            created_by=self.user,
        )
        assert daily.frequency == "daily"
        assert monthly.frequency == "monthly"


class TestCalculateNextRun:
    """_calculate_next_run ユニットテスト（DB不要）."""

    def test_daily(self):
        from apps.reports.tasks import _calculate_next_run

        base = timezone.now()
        result = _calculate_next_run("daily", base)
        assert result == base + timedelta(days=1)

    def test_weekly(self):
        from apps.reports.tasks import _calculate_next_run

        base = timezone.now()
        result = _calculate_next_run("weekly", base)
        assert result == base + timedelta(weeks=1)

    def test_monthly_fallback(self):
        from apps.reports.tasks import _calculate_next_run

        base = timezone.now()
        result = _calculate_next_run("monthly", base)
        assert result == base + timedelta(days=30)


@pytest.mark.django_db
class TestRunScheduledReportsTask(TestCase):
    """run_scheduled_reports Celeryタスク結合テスト."""

    def setUp(self):
        self.user = GRCUser.objects.create_user(
            username="taskadmin",
            password="testpass123",
            role=GRCUser.Role.GRC_ADMIN,
        )

    def test_no_due_schedules_returns_empty(self):
        """実行対象なし → executed/failed ともに空."""
        from apps.reports.tasks import run_scheduled_reports

        result = run_scheduled_reports()
        assert result["executed"] == []
        assert result["failed"] == []
        assert result["count"] == 0

    def test_inactive_schedule_is_skipped(self):
        """is_active=False のスケジュールは無視される。"""
        from apps.reports.models import ScheduledReport
        from apps.reports.tasks import run_scheduled_reports

        ScheduledReport.objects.create(
            name="非アクティブ",
            report_type="grc_dashboard",
            frequency=ScheduledReport.Frequency.DAILY,
            is_active=False,
            next_run=timezone.now() - timedelta(hours=1),
            recipients=["test@example.com"],
            created_by=self.user,
        )
        result = run_scheduled_reports()
        assert result["count"] == 0

    def test_future_schedule_is_skipped(self):
        """next_run が未来のスケジュールは無視される。"""
        from apps.reports.models import ScheduledReport
        from apps.reports.tasks import run_scheduled_reports

        ScheduledReport.objects.create(
            name="未来スケジュール",
            report_type="grc_dashboard",
            frequency=ScheduledReport.Frequency.DAILY,
            is_active=True,
            next_run=timezone.now() + timedelta(hours=1),
            recipients=["test@example.com"],
            created_by=self.user,
        )
        result = run_scheduled_reports()
        assert result["count"] == 0

    @patch("apps.reports.tasks._generate_pdf_for_type")
    @patch("apps.reports.tasks._send_report_email")
    def test_due_schedule_executes_and_updates_next_run(self, mock_send, mock_pdf):
        """期限到達スケジュールが実行され next_run が更新される。"""
        from apps.reports.models import ScheduledReport
        from apps.reports.tasks import run_scheduled_reports

        mock_pdf.return_value = b"fake-pdf"
        mock_send.return_value = None

        schedule = ScheduledReport.objects.create(
            name="週次テスト",
            report_type="risk_trend",
            frequency=ScheduledReport.Frequency.WEEKLY,
            is_active=True,
            next_run=timezone.now() - timedelta(minutes=1),
            recipients=["admin@example.com"],
            created_by=self.user,
        )
        old_next_run = schedule.next_run

        result = run_scheduled_reports()

        assert result["count"] == 1
        assert str(schedule.id) in result["executed"]
        assert result["failed"] == []

        schedule.refresh_from_db()
        assert schedule.next_run > old_next_run
        assert schedule.last_run is not None
        mock_send.assert_called_once()

    @patch("apps.reports.tasks._generate_pdf_for_type", side_effect=RuntimeError("PDF error"))
    def test_pdf_error_moves_to_failed(self, mock_pdf):
        """PDF生成失敗時は failed リストに記録され例外を飲み込む。"""
        from apps.reports.models import ScheduledReport
        from apps.reports.tasks import run_scheduled_reports

        schedule = ScheduledReport.objects.create(
            name="失敗テスト",
            report_type="grc_dashboard",
            frequency=ScheduledReport.Frequency.DAILY,
            is_active=True,
            next_run=timezone.now() - timedelta(minutes=5),
            recipients=["fail@example.com"],
            created_by=self.user,
        )

        result = run_scheduled_reports()

        assert result["count"] == 0
        assert str(schedule.id) in result["failed"]


@pytest.mark.django_db
class TestSendReportEmail(TestCase):
    """_send_report_email メール送信テスト."""

    def setUp(self):
        self.user = GRCUser.objects.create_user(
            username="emailadmin",
            password="testpass123",
            role=GRCUser.Role.GRC_ADMIN,
        )

    def test_no_recipients_skips_send(self):
        """受信者なしの場合はメール送信しない。"""
        from apps.reports.models import ScheduledReport
        from apps.reports.tasks import _send_report_email

        schedule = ScheduledReport.objects.create(
            name="受信者なし",
            report_type="grc_dashboard",
            recipients=[],
            created_by=self.user,
        )
        # 例外なく完了し、EmailMessage.send は呼ばれない
        _send_report_email(schedule, b"fake-pdf")

    def test_email_sent_with_pdf_attachment(self):
        """受信者ありの場合はPDF添付メールが送信される。"""
        from django.core import mail
        from django.test.utils import override_settings

        from apps.reports.models import ScheduledReport
        from apps.reports.tasks import _send_report_email

        schedule = ScheduledReport.objects.create(
            name="添付テスト",
            report_type="risk_trend",
            frequency=ScheduledReport.Frequency.WEEKLY,
            recipients=["user@example.com"],
            created_by=self.user,
        )

        # EmailMessage がローカルインポートのため django.core.mail でパッチ
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"):
            _send_report_email(schedule, b"%PDF fake content")

        assert len(mail.outbox) == 1
        assert "添付テスト" in mail.outbox[0].subject
        assert len(mail.outbox[0].attachments) == 1
        assert mail.outbox[0].attachments[0][2] == "application/pdf"
