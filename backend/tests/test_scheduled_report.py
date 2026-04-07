"""レポートスケジュール機能テスト."""

from __future__ import annotations

from django.test import TestCase
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
