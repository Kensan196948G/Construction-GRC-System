"""レポート関連Celeryタスク"""

from __future__ import annotations

from datetime import timedelta
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


def _calculate_next_run(frequency: str, from_dt):
    """頻度に基づいて次回実行日時を計算する。"""
    if frequency == "daily":
        return from_dt + timedelta(days=1)
    if frequency == "weekly":
        return from_dt + timedelta(weeks=1)
    # monthly
    return from_dt + timedelta(days=30)


@shared_task(name="reports.run_scheduled_reports")
def run_scheduled_reports():
    """定期レポートスケジュールを実行する（毎時0分）。

    is_active=True かつ next_run <= now のスケジュールを対象に
    PDFを生成してメール添付送信し、次回実行日時を更新する。
    """
    from django.utils import timezone

    from apps.reports.models import ScheduledReport
    from apps.reports.services import GRCDataService

    now = timezone.now()
    due_schedules = ScheduledReport.objects.filter(is_active=True, next_run__lte=now)

    executed: list[str] = []
    failed: list[str] = []

    for schedule in due_schedules:
        try:
            pdf_bytes = _generate_pdf_for_type(schedule.report_type, GRCDataService)
            _send_report_email(schedule, pdf_bytes)
            schedule.last_run = now
            schedule.next_run = _calculate_next_run(schedule.frequency, now)
            schedule.save(update_fields=["last_run", "next_run", "updated_at"])
            executed.append(str(schedule.id))
            logger.info("ScheduledReport executed: id=%s name=%s", schedule.id, schedule.name)
        except Exception as exc:
            logger.error("ScheduledReport failed: id=%s name=%s error=%s", schedule.id, schedule.name, exc)
            failed.append(str(schedule.id))

    return {"executed": executed, "failed": failed, "count": len(executed)}


def _generate_pdf_for_type(report_type: str, data_service) -> bytes:
    """レポートタイプに応じてPDFバイナリを生成する。"""
    from apps.reports.pdf_generator import PDFReportGenerator

    if report_type == "grc_dashboard":
        data = data_service.get_dashboard_data()
        return PDFReportGenerator.generate_grc_dashboard_pdf(data)
    if report_type == "compliance_status":
        data = data_service.get_compliance_data()
        return PDFReportGenerator.generate_compliance_report_pdf(data)
    if report_type in ("risk_trend", "iso27001_annual", "soa", "audit_report"):
        data = data_service.get_risk_data()
        return PDFReportGenerator.generate_risk_report_pdf(data)
    # 未知のタイプはダッシュボードPDFにフォールバック
    data = data_service.get_dashboard_data()
    return PDFReportGenerator.generate_grc_dashboard_pdf(data)


def _send_report_email(schedule, pdf_bytes: bytes) -> None:
    """スケジュールの受信者にPDF添付メールを送信する。"""
    from django.conf import settings
    from django.core.mail import EmailMessage

    recipients = schedule.recipients
    if not recipients:
        logger.info("ScheduledReport id=%s: no recipients, skipping email", schedule.id)
        return

    report_type_label = {
        "grc_dashboard": "GRCダッシュボード",
        "iso27001_annual": "ISO27001年次レポート",
        "compliance_status": "規格別準拠レポート",
        "risk_trend": "リスクトレンド分析",
        "soa": "適用宣言書（SoA）",
        "audit_report": "監査報告書",
    }.get(schedule.report_type, schedule.report_type)

    subject = f"[GRC] {schedule.name} — {report_type_label}"
    body = (
        f"定期レポート「{schedule.name}」が自動生成されました。\n\n"
        f"レポート種別: {report_type_label}\n"
        f"配信頻度: {schedule.get_frequency_display()}\n\n"
        "--\nConstruction-GRC-System 自動配信"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@grc.local"),
        to=recipients,
    )
    email.attach(f"{schedule.name}.pdf", pdf_bytes, "application/pdf")
    email.send(fail_silently=False)


@shared_task(name="reports.send_daily_digest")
def send_daily_digest():
    """日次GRCダイジェスト送信（毎日18:00実行）"""
    from django.db.models import F

    from apps.audits.models import AuditFinding
    from apps.compliance.models import ComplianceRequirement
    from apps.reports.notification_service import NotificationService
    from apps.risks.models import Risk

    total_risks = Risk.objects.count()
    # annotate でDB側集計 (N+1回避: 全件Python展開→COUNT(WHERE)1クエリ)
    critical = (
        Risk.objects.annotate(risk_score=F("likelihood_inherent") * F("impact_inherent"))
        .filter(risk_score__gte=15)
        .count()
    )

    total_compliance = ComplianceRequirement.objects.count()
    compliant = ComplianceRequirement.objects.filter(compliance_status="compliant").count()
    rate = round(compliant / total_compliance * 100, 1) if total_compliance > 0 else 0

    open_findings = AuditFinding.objects.exclude(cap_status="closed").count()

    summary = {
        "risks": total_risks,
        "critical_risks": critical,
        "compliance_rate": rate,
        "open_findings": open_findings,
    }

    result = NotificationService.notify_daily_digest(summary)
    return {"summary": summary, "notification_results": result}
