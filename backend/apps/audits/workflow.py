"""監査ワークフロー管理サービス

監査のライフサイクル管理、ステータス遷移、CAP期限監視を提供。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any

from apps.audits.models import Audit, AuditFinding

logger = logging.getLogger(__name__)

# 許可されるステータス遷移
VALID_TRANSITIONS: dict[str, list[str]] = {
    "planned": ["in_progress", "cancelled"],
    "in_progress": ["completed", "cancelled"],
    "completed": ["closed"],
    "closed": [],
    "cancelled": [],
}


class AuditWorkflowService:
    """監査ワークフロー管理"""

    @staticmethod
    def transition_status(audit: Audit, new_status: str) -> tuple[bool, str]:
        """監査ステータスを遷移する。"""
        current = audit.status
        valid_next = VALID_TRANSITIONS.get(current, [])

        if new_status not in valid_next:
            return (
                False,
                f"'{current}' → '{new_status}' は無効な遷移です。許可: {valid_next}",
            )

        old_status = audit.status
        audit.status = new_status

        # 自動日付設定
        now = datetime.now(tz=UTC).date()
        if new_status == "in_progress" and not audit.actual_start:
            audit.actual_start = now
        elif new_status == "completed":
            audit.actual_end = now

        audit.save()
        logger.info("Audit %s: %s → %s", audit.audit_id, old_status, new_status)
        return True, f"ステータスを '{new_status}' に更新しました"

    @staticmethod
    def get_overdue_caps() -> list[dict[str, Any]]:
        """期限超過のCAPを取得する。"""
        now = datetime.now(tz=UTC).date()
        findings = AuditFinding.objects.exclude(cap_status="closed").filter(
            cap_due_date__lt=now,
        )
        return [
            {
                "finding_id": f.finding_id,
                "title": f.title,
                "due_date": str(f.cap_due_date),
                "days_overdue": (now - f.cap_due_date).days,
                "audit": str(f.audit),
            }
            for f in findings
        ]

    @staticmethod
    def get_upcoming_caps(days: int = 7) -> list[dict[str, Any]]:
        """期限間近のCAPを取得する。"""
        now = datetime.now(tz=UTC).date()
        deadline = now + timedelta(days=days)
        findings = AuditFinding.objects.exclude(cap_status="closed").filter(
            cap_due_date__gte=now,
            cap_due_date__lte=deadline,
        )
        return [
            {
                "finding_id": f.finding_id,
                "title": f.title,
                "due_date": str(f.cap_due_date),
                "days_remaining": (f.cap_due_date - now).days,
                "audit": str(f.audit),
            }
            for f in findings
        ]

    @staticmethod
    def auto_complete_audit(audit: Audit) -> tuple[bool, str]:
        """全所見のCAPがクローズされたら監査を自動完了する。"""
        open_findings = audit.findings.exclude(cap_status="closed").count()
        if open_findings > 0:
            return False, f"未クローズの所見が {open_findings} 件あります"

        if audit.status == "in_progress":
            audit.status = "completed"
            audit.actual_end = datetime.now(tz=UTC).date()
            audit.save()
            logger.info("Audit %s auto-completed (all CAPs closed)", audit.audit_id)
            return True, "全CAPクローズにより自動完了"
        return (
            False,
            f"現在のステータス '{audit.status}' では自動完了できません",
        )
