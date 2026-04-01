"""監査ワークフローサービステスト

AuditWorkflowService のステータス遷移・CAP期限チェックを検証。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from django.test import TestCase

from apps.audits.models import Audit, AuditFinding
from apps.audits.workflow import VALID_TRANSITIONS, AuditWorkflowService


class TestAuditWorkflowTransitions(TestCase):
    """ステータス遷移テスト"""

    def _create_audit(self, status: str = "planned") -> Audit:
        return Audit.objects.create(
            audit_id=f"AUD-TEST-{Audit.objects.count() + 1:03d}",
            title="Test Audit",
            audit_type="ISO27001定期監査",
            target_department="IT部門",
            planned_start=datetime.now(tz=UTC).date(),
            planned_end=datetime.now(tz=UTC).date() + timedelta(days=30),
            status=status,
        )

    def test_planned_to_in_progress(self) -> None:
        audit = self._create_audit("planned")
        ok, msg = AuditWorkflowService.transition_status(audit, "in_progress")
        assert ok is True
        audit.refresh_from_db()
        assert audit.status == "in_progress"

    def test_planned_to_cancelled(self) -> None:
        audit = self._create_audit("planned")
        ok, msg = AuditWorkflowService.transition_status(audit, "cancelled")
        assert ok is True
        audit.refresh_from_db()
        assert audit.status == "cancelled"

    def test_in_progress_to_completed(self) -> None:
        audit = self._create_audit("in_progress")
        ok, msg = AuditWorkflowService.transition_status(audit, "completed")
        assert ok is True
        audit.refresh_from_db()
        assert audit.status == "completed"
        assert audit.actual_end is not None

    def test_completed_to_closed(self) -> None:
        audit = self._create_audit("completed")
        ok, msg = AuditWorkflowService.transition_status(audit, "closed")
        assert ok is True

    def test_invalid_planned_to_completed(self) -> None:
        """planned -> completed は無効"""
        audit = self._create_audit("planned")
        ok, msg = AuditWorkflowService.transition_status(audit, "completed")
        assert ok is False
        assert "無効な遷移" in msg

    def test_invalid_closed_to_any(self) -> None:
        """closed からの遷移は全て無効"""
        audit = self._create_audit("closed")
        ok, msg = AuditWorkflowService.transition_status(audit, "planned")
        assert ok is False

    def test_invalid_cancelled_to_any(self) -> None:
        """cancelled からの遷移は全て無効"""
        audit = self._create_audit("cancelled")
        ok, msg = AuditWorkflowService.transition_status(audit, "in_progress")
        assert ok is False

    def test_in_progress_sets_actual_start(self) -> None:
        """in_progress遷移時にactual_startが自動設定される"""
        audit = self._create_audit("planned")
        assert audit.actual_start is None
        AuditWorkflowService.transition_status(audit, "in_progress")
        audit.refresh_from_db()
        assert audit.actual_start is not None

    def test_completed_sets_actual_end(self) -> None:
        """completed遷移時にactual_endが自動設定される"""
        audit = self._create_audit("in_progress")
        assert audit.actual_end is None
        AuditWorkflowService.transition_status(audit, "completed")
        audit.refresh_from_db()
        assert audit.actual_end is not None

    def test_valid_transitions_map_completeness(self) -> None:
        """VALID_TRANSITIONS に全ステータスが定義されている"""
        expected_statuses = {"planned", "in_progress", "completed", "closed", "cancelled"}
        assert set(VALID_TRANSITIONS.keys()) == expected_statuses


class TestAuditWorkflowCAPChecks(TestCase):
    """CAP期限チェックテスト"""

    def _create_audit_with_finding(
        self,
        cap_status: str = "open",
        cap_due_date=None,
    ) -> tuple[Audit, AuditFinding]:
        audit = Audit.objects.create(
            audit_id=f"AUD-CAP-{Audit.objects.count() + 1:03d}",
            title="CAP Test Audit",
            audit_type="ISO27001定期監査",
            target_department="IT部門",
            planned_start=datetime.now(tz=UTC).date(),
            planned_end=datetime.now(tz=UTC).date() + timedelta(days=30),
            status="in_progress",
        )
        finding = AuditFinding.objects.create(
            audit=audit,
            finding_id=f"F-CAP-{AuditFinding.objects.count() + 1:03d}",
            finding_type="minor_nc",
            title="Test Finding",
            description="Test description",
            cap_status=cap_status,
            cap_due_date=cap_due_date,
        )
        return audit, finding

    def test_get_overdue_caps_empty(self) -> None:
        result = AuditWorkflowService.get_overdue_caps()
        assert result == []

    def test_get_overdue_caps_with_overdue(self) -> None:
        past_date = datetime.now(tz=UTC).date() - timedelta(days=5)
        self._create_audit_with_finding(cap_status="open", cap_due_date=past_date)
        result = AuditWorkflowService.get_overdue_caps()
        assert len(result) == 1
        assert result[0]["days_overdue"] >= 5

    def test_get_overdue_caps_excludes_closed(self) -> None:
        past_date = datetime.now(tz=UTC).date() - timedelta(days=5)
        self._create_audit_with_finding(cap_status="closed", cap_due_date=past_date)
        result = AuditWorkflowService.get_overdue_caps()
        assert len(result) == 0

    def test_get_upcoming_caps_empty(self) -> None:
        result = AuditWorkflowService.get_upcoming_caps()
        assert result == []

    def test_get_upcoming_caps_within_window(self) -> None:
        future_date = datetime.now(tz=UTC).date() + timedelta(days=3)
        self._create_audit_with_finding(cap_status="open", cap_due_date=future_date)
        result = AuditWorkflowService.get_upcoming_caps(days=7)
        assert len(result) == 1
        assert result[0]["days_remaining"] >= 2

    def test_get_upcoming_caps_outside_window(self) -> None:
        future_date = datetime.now(tz=UTC).date() + timedelta(days=30)
        self._create_audit_with_finding(cap_status="open", cap_due_date=future_date)
        result = AuditWorkflowService.get_upcoming_caps(days=7)
        assert len(result) == 0


class TestAuditAutoComplete(TestCase):
    """自動完了テスト"""

    def _create_audit_with_findings(self, statuses: list[str]) -> Audit:
        audit = Audit.objects.create(
            audit_id=f"AUD-AC-{Audit.objects.count() + 1:03d}",
            title="Auto Complete Test",
            audit_type="ISO27001定期監査",
            target_department="IT部門",
            planned_start=datetime.now(tz=UTC).date(),
            planned_end=datetime.now(tz=UTC).date() + timedelta(days=30),
            status="in_progress",
        )
        for i, status in enumerate(statuses):
            AuditFinding.objects.create(
                audit=audit,
                finding_id=f"F-AC-{AuditFinding.objects.count() + 1:03d}",
                finding_type="minor_nc",
                title=f"Finding {i}",
                description="desc",
                cap_status=status,
            )
        return audit

    def test_auto_complete_all_closed(self) -> None:
        audit = self._create_audit_with_findings(["closed", "closed"])
        ok, msg = AuditWorkflowService.auto_complete_audit(audit)
        assert ok is True
        audit.refresh_from_db()
        assert audit.status == "completed"

    def test_auto_complete_with_open_findings(self) -> None:
        audit = self._create_audit_with_findings(["closed", "open"])
        ok, msg = AuditWorkflowService.auto_complete_audit(audit)
        assert ok is False
        assert "未クローズ" in msg

    def test_auto_complete_wrong_status(self) -> None:
        audit = self._create_audit_with_findings(["closed"])
        audit.status = "planned"
        audit.save()
        ok, msg = AuditWorkflowService.auto_complete_audit(audit)
        assert ok is False
        assert "自動完了できません" in msg
