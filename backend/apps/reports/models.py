import uuid

from django.conf import settings
from django.db import models


class Report(models.Model):
    """自動生成レポート"""

    class ReportType(models.TextChoices):
        GRC_DASHBOARD = "grc_dashboard", "経営層GRCダッシュボード"
        ISO27001_ANNUAL = "iso27001_annual", "ISO27001年次レポート"
        COMPLIANCE_STATUS = "compliance_status", "規格別準拠レポート"
        RISK_TREND = "risk_trend", "リスクトレンド分析"
        SOA = "soa", "適用宣言書（SoA）"
        AUDIT_REPORT = "audit_report", "監査報告書"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file_path = models.FileField(upload_to="reports/%Y/%m/", blank=True)
    format = models.CharField(max_length=10, default="pdf", help_text="pdf/xlsx")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "レポート"
        verbose_name_plural = "レポート"

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"


class ScheduledReport(models.Model):
    """定期レポートスケジュール."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "毎日"
        WEEKLY = "weekly", "毎週"
        MONTHLY = "monthly", "毎月"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="スケジュール名")
    report_type = models.CharField(max_length=30, choices=Report.ReportType.choices)
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    recipients = models.JSONField(default=list, verbose_name="受信者メールアドレスリスト")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "レポートスケジュール"
        verbose_name_plural = "レポートスケジュール"
        indexes = [
            models.Index(fields=["is_active", "next_run"], name="sched_rpt_active_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.frequency})"
