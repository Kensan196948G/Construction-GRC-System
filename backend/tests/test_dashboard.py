"""統合GRCダッシュボードAPIテスト

GRCDashboardView の各サマリーメソッドを空DB・データ有りの両パターンで検証。
"""

from __future__ import annotations

from django.test import TestCase

from apps.reports.views_dashboard import GRCDashboardView


class TestGRCDashboardViewEmptyDB(TestCase):
    """ダッシュボードAPI ユニットテスト（空DB）"""

    def test_risk_summary_empty(self) -> None:
        result = GRCDashboardView._risk_summary()
        assert result["total"] == 0

    def test_risk_summary_empty_by_level(self) -> None:
        result = GRCDashboardView._risk_summary()
        assert result["by_level"] == {}

    def test_risk_summary_empty_by_status(self) -> None:
        result = GRCDashboardView._risk_summary()
        assert result["by_status"] == {}

    def test_compliance_summary_empty(self) -> None:
        result = GRCDashboardView._compliance_summary()
        assert result["total"] == 0
        assert result["rate"] == 0

    def test_controls_summary_empty(self) -> None:
        result = GRCDashboardView._controls_summary()
        assert result["total_applicable"] == 0
        assert result["rate"] == 0

    def test_audit_summary_empty(self) -> None:
        result = GRCDashboardView._audit_summary()
        assert result["total_audits"] == 0

    def test_risk_summary_has_required_keys(self) -> None:
        result = GRCDashboardView._risk_summary()
        for key in ("total", "by_level", "by_status"):
            assert key in result, f"Missing key: {key}"

    def test_compliance_summary_has_required_keys(self) -> None:
        result = GRCDashboardView._compliance_summary()
        for key in ("total", "compliant", "non_compliant", "partial", "unknown", "rate"):
            assert key in result, f"Missing key: {key}"

    def test_controls_summary_has_required_keys(self) -> None:
        result = GRCDashboardView._controls_summary()
        for key in ("total_applicable", "implemented", "in_progress", "not_started", "rate"):
            assert key in result, f"Missing key: {key}"

    def test_audit_summary_has_required_keys(self) -> None:
        result = GRCDashboardView._audit_summary()
        for key in ("total_audits", "completed", "in_progress", "planned", "total_findings"):
            assert key in result, f"Missing key: {key}"

    def test_audit_summary_has_findings_keys(self) -> None:
        result = GRCDashboardView._audit_summary()
        assert "open_findings" in result
        assert "by_type" in result

    def test_audit_summary_by_type_keys(self) -> None:
        result = GRCDashboardView._audit_summary()
        by_type = result["by_type"]
        for key in ("major_nc", "minor_nc", "observation", "good_practice"):
            assert key in by_type, f"Missing by_type key: {key}"
