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


@pytest.mark.django_db
class TestRunScheduledReportsTask(TestCase):
    """run_scheduled_reports Celery タスクのテスト."""

    def setUp(self):
        self.user = GRCUser.objects.create_user(
            username="taskuser",
            password="testpass123",
            role=GRCUser.Role.GRC_ADMIN,
        )

    def _make_schedule(self, name, frequency="weekly", is_active=True, next_run=None, **kwargs):
        from django.utils import timezone

        from apps.reports.models import ScheduledReport

        if next_run is None:
            next_run = timezone.now() - __import__("datetime").timedelta(hours=1)
        return ScheduledReport.objects.create(
            name=name,
            report_type="grc_dashboard",
            frequency=frequency,
            is_active=is_active,
            next_run=next_run,
            created_by=self.user,
            recipients=["test@example.com"],
            **kwargs,
        )

    def test_runs_only_due_active_schedules(self):
        """期限到来済みかつ is_active=True のものだけ実行される。"""
        from django.utils import timezone

        due = self._make_schedule("期限到来済み")
        self._make_schedule("非アクティブ", is_active=False)
        future_dt = timezone.now() + __import__("datetime").timedelta(hours=2)
        self._make_schedule("将来実行", next_run=future_dt)

        from apps.reports.tasks import run_scheduled_reports

        result = run_scheduled_reports()

        assert result["count"] == 1
        assert str(due.id) in result["executed"]

    def test_last_run_updated_after_execution(self):
        """実行後に last_run が now() に近い値で更新される。"""
        from django.utils import timezone

        schedule = self._make_schedule("last_run テスト")
        assert schedule.last_run is None

        from apps.reports.tasks import run_scheduled_reports

        run_scheduled_reports()

        schedule.refresh_from_db()
        assert schedule.last_run is not None
        delta = timezone.now() - schedule.last_run
        assert delta.total_seconds() < 10

    def test_next_run_updated_by_frequency(self):
        """frequency に応じて next_run が適切に更新される。"""
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()
        daily = self._make_schedule("daily テスト", frequency="daily")
        weekly = self._make_schedule("weekly テスト", frequency="weekly")
        monthly = self._make_schedule("monthly テスト", frequency="monthly")

        from apps.reports.tasks import run_scheduled_reports

        run_scheduled_reports()

        daily.refresh_from_db()
        weekly.refresh_from_db()
        monthly.refresh_from_db()

        assert daily.next_run >= now + timedelta(hours=23)
        assert weekly.next_run >= now + timedelta(days=6)
        assert monthly.next_run >= now + timedelta(days=29)

    def test_no_due_schedules_returns_empty(self):
        """実行対象がない場合は count=0 を返す。"""
        from django.utils import timezone

        future_dt = timezone.now() + __import__("datetime").timedelta(hours=2)
        self._make_schedule("将来のみ", next_run=future_dt)

        from apps.reports.tasks import run_scheduled_reports

        result = run_scheduled_reports()

        assert result["count"] == 0
        assert result["executed"] == []

    def test_inactive_schedule_not_executed(self):
        """is_active=False のスケジュールは実行されない。"""
        self._make_schedule("非アクティブ", is_active=False)

        from apps.reports.tasks import run_scheduled_reports

        result = run_scheduled_reports()

        assert result["count"] == 0
