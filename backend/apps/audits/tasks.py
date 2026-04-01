"""監査ワークフロー 定期タスク"""

from celery import shared_task


@shared_task(name="audits.check_cap_deadlines")
def check_cap_deadlines():
    """CAP期限チェック（毎日実行）

    期限超過および期限間近の是正処置（CAP）を検出する。
    """
    from apps.audits.workflow import AuditWorkflowService

    overdue = AuditWorkflowService.get_overdue_caps()
    upcoming = AuditWorkflowService.get_upcoming_caps(days=7)

    return {
        "overdue_count": len(overdue),
        "upcoming_count": len(upcoming),
        "overdue": overdue[:10],
        "upcoming": upcoming[:10],
    }


@shared_task(name="audits.auto_complete_audits")
def auto_complete_audits():
    """全CAPクローズ済み監査の自動完了（毎日実行）

    実施中の監査で全所見のCAPがクローズされたものを自動的に完了にする。
    """
    from apps.audits.models import Audit
    from apps.audits.workflow import AuditWorkflowService

    completed = []
    for audit in Audit.objects.filter(status="in_progress"):
        success, _msg = AuditWorkflowService.auto_complete_audit(audit)
        if success:
            completed.append(audit.audit_id)

    return {"auto_completed": completed, "count": len(completed)}
