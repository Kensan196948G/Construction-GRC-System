"""レポート関連Celeryタスク"""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


def _calculate_next_run(frequency: str, from_dt):
    """次回実行日時を周期に応じて計算する。"""
    from datetime import timedelta

    if frequency == "daily":
        return from_dt + timedelta(days=1)
    if frequency == "weekly":
        return from_dt + timedelta(weeks=1)
    # monthly: 1か月後（同日同時刻）を近似で30日後
    return from_dt + timedelta(days=30)


@shared_task(name="reports.run_scheduled_reports")
def run_scheduled_reports():
    """ScheduledReport を定期実行するタスク。Celery Beat から毎時呼び出される。"""
    from django.utils import timezone

    from apps.reports.models import ScheduledReport
    from apps.reports.notification_service import NotificationService

    now = timezone.now()

    due_schedules = ScheduledReport.objects.filter(
        is_active=True,
        next_run__lte=now,
    )

    executed = []
    for schedule in due_schedules:
        try:
            recipients = schedule.recipients if isinstance(schedule.recipients, list) else []
            recipients_str = ", ".join(recipients) if recipients else "（受信者なし）"
            message = (
                f"スケジュール名: {schedule.name}\n"
                f"レポート種別: {schedule.report_type}\n"
                f"頻度: {schedule.frequency}\n"
                f"受信者: {recipients_str}"
            )
            NotificationService.notify(
                event_type="report.scheduled",
                title=f"定期レポート実行: {schedule.name}",
                message=message,
                severity="info",
                extra={"schedule_id": str(schedule.id), "recipients": recipients},
            )

            schedule.last_run = now
            schedule.next_run = _calculate_next_run(schedule.frequency, now)
            schedule.save(update_fields=["last_run", "next_run", "updated_at"])

            logger.info(
                "ScheduledReport executed: id=%s name=%s next_run=%s",
                schedule.id,
                schedule.name,
                schedule.next_run,
            )
            executed.append(str(schedule.id))
        except Exception as exc:  # noqa: BLE001
            logger.error("ScheduledReport failed: id=%s error=%s", schedule.id, exc)

    return {"executed": executed, "count": len(executed)}


@shared_task(name="reports.send_daily_digest")
def send_daily_digest():
    """日次GRCダイジェスト送信（毎日18:00実行）"""
    from apps.audits.models import AuditFinding
    from apps.compliance.models import ComplianceRequirement
    from apps.reports.notification_service import NotificationService
    from apps.risks.models import Risk

    total_risks = Risk.objects.count()
    critical = sum(1 for r in Risk.objects.all() if r.risk_level == "CRITICAL")

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
