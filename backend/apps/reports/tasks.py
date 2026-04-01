"""レポート関連Celeryタスク"""

from celery import shared_task


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
