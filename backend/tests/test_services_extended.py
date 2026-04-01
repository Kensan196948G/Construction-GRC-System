"""サービス層の拡張テスト

ComplianceRateService / RiskHeatmapService / SoAGenerator / AuditStatisticsService
の各サービスクラスを網羅的にテストする。

DB依存テストには @pytest.mark.django_db + @pytest.mark.integration を付与。
DB不要のロジックテストはマーカーなしで実行可能。
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from apps.controls.services import ComplianceRateService
from apps.risks.services import RiskHeatmapService


# ---------------------------------------------------------------------------
# ComplianceRateService — DB不要テスト（Mock使用）
# ---------------------------------------------------------------------------
class TestComplianceRateServiceOverallMocked:
    """ComplianceRateService.calculate_overall_rate のMockテスト"""

    def _make_mock_qs(self, total: int, applicable: int, status_counts: list[dict[str, Any]]) -> MagicMock:
        """管理策のモッククエリセットを生成する"""
        qs = MagicMock()
        qs.count.return_value = total

        applicable_qs = MagicMock()
        applicable_qs.count.return_value = applicable
        applicable_qs.values.return_value.annotate.return_value = status_counts
        qs.filter.return_value = applicable_qs

        return qs

    def test_overall_rate_100_percent(self) -> None:
        """全管理策が実施済みなら100%"""
        qs = self._make_mock_qs(
            total=10,
            applicable=10,
            status_counts=[{"implementation_status": "implemented", "count": 10}],
        )
        result = ComplianceRateService.calculate_overall_rate(queryset=qs)
        assert result["compliance_rate"] == 100.0
        assert result["implemented"] == 10

    def test_overall_rate_zero_when_nothing_implemented(self) -> None:
        """実施済みがゼロなら0%"""
        qs = self._make_mock_qs(
            total=10,
            applicable=10,
            status_counts=[{"implementation_status": "not_started", "count": 10}],
        )
        result = ComplianceRateService.calculate_overall_rate(queryset=qs)
        assert result["compliance_rate"] == 0.0
        assert result["implemented"] == 0

    def test_overall_rate_partial(self) -> None:
        """部分的な実施率が正しく計算される"""
        qs = self._make_mock_qs(
            total=20,
            applicable=20,
            status_counts=[
                {"implementation_status": "implemented", "count": 15},
                {"implementation_status": "in_progress", "count": 5},
            ],
        )
        result = ComplianceRateService.calculate_overall_rate(queryset=qs)
        assert result["compliance_rate"] == 75.0

    def test_overall_rate_zero_applicable(self) -> None:
        """適用対象がゼロなら 0.0%"""
        qs = self._make_mock_qs(total=5, applicable=0, status_counts=[])
        result = ComplianceRateService.calculate_overall_rate(queryset=qs)
        assert result["compliance_rate"] == 0.0

    def test_overall_rate_returns_required_keys(self) -> None:
        """戻り値に必須キーが含まれる"""
        qs = self._make_mock_qs(total=5, applicable=5, status_counts=[])
        result = ComplianceRateService.calculate_overall_rate(queryset=qs)
        for key in ("total", "applicable", "implemented", "compliance_rate", "by_status"):
            assert key in result


class TestComplianceRateServiceByDomainMocked:
    """ComplianceRateService.calculate_by_domain のMockテスト"""

    def test_by_domain_returns_list(self) -> None:
        """戻り値がリストである"""
        qs = MagicMock()
        domain_qs = MagicMock()
        domain_qs.count.return_value = 0
        qs.filter.return_value = domain_qs

        result = ComplianceRateService.calculate_by_domain(queryset=qs)
        assert isinstance(result, list)

    def test_by_domain_skips_empty_domains(self) -> None:
        """管理策のないドメインはスキップされる"""
        qs = MagicMock()
        domain_qs = MagicMock()
        domain_qs.count.return_value = 0
        qs.filter.return_value = domain_qs

        result = ComplianceRateService.calculate_by_domain(queryset=qs)
        assert len(result) == 0


class TestComplianceRateServiceTrend:
    """ComplianceRateService.calculate_trend のテスト"""

    def test_trend_returns_correct_month_count(self) -> None:
        """指定月数分のデータが返される"""
        qs = MagicMock()
        applicable_qs = MagicMock()
        applicable_qs.count.return_value = 0
        qs.filter.return_value = applicable_qs

        result = ComplianceRateService.calculate_trend(months=3, queryset=qs)
        assert len(result) == 3

    def test_trend_returns_six_months_by_default(self) -> None:
        """デフォルトは6ヶ月"""
        qs = MagicMock()
        applicable_qs = MagicMock()
        applicable_qs.count.return_value = 0
        qs.filter.return_value = applicable_qs

        result = ComplianceRateService.calculate_trend(queryset=qs)
        assert len(result) == 6

    def test_trend_entry_has_required_keys(self) -> None:
        """トレンドエントリに必須キーが含まれる"""
        qs = MagicMock()
        applicable_qs = MagicMock()
        applicable_qs.count.return_value = 10
        # filter for implemented controls
        filter_qs = MagicMock()
        filter_qs.count.return_value = 5
        applicable_qs.filter.return_value = filter_qs
        qs.filter.return_value = applicable_qs

        result = ComplianceRateService.calculate_trend(months=1, queryset=qs)
        assert len(result) == 1
        entry = result[0]
        for key in ("month", "implemented", "applicable", "compliance_rate"):
            assert key in entry

    def test_trend_zero_applicable_gives_zero_rate(self) -> None:
        """適用対象ゼロなら各月の rate は 0.0"""
        qs = MagicMock()
        applicable_qs = MagicMock()
        applicable_qs.count.return_value = 0
        applicable_qs.filter.return_value = applicable_qs
        qs.filter.return_value = applicable_qs

        result = ComplianceRateService.calculate_trend(months=2, queryset=qs)
        for entry in result:
            assert entry["compliance_rate"] == 0.0


# ---------------------------------------------------------------------------
# RiskHeatmapService — 拡張テスト
# ---------------------------------------------------------------------------
class TestRiskHeatmapServiceExtended:
    """RiskHeatmapService の拡張テスト"""

    def test_generate_heatmap_data_with_risks(self) -> None:
        """リスクデータありの場合、count が加算される"""
        mock_risk = MagicMock()
        mock_risk.risk_id = "RISK-001"
        mock_risk.title = "テストリスク"
        mock_risk.likelihood_inherent = 3
        mock_risk.impact_inherent = 4

        qs = MagicMock()
        qs.only.return_value = [mock_risk]

        data = RiskHeatmapService.generate_heatmap_data(queryset=qs)
        # (3,4) のセルの count が 1 であること
        cell = data["matrix"][2][3]  # 0-indexed: row=2 (likelihood=3), col=3 (impact=4)
        assert cell["count"] == 1

    def test_generate_heatmap_data_risks_list(self) -> None:
        """risks リストにリスクが含まれる"""
        mock_risk = MagicMock()
        mock_risk.risk_id = "RISK-002"
        mock_risk.title = "リスクB"
        mock_risk.likelihood_inherent = 5
        mock_risk.impact_inherent = 5

        qs = MagicMock()
        qs.only.return_value = [mock_risk]

        data = RiskHeatmapService.generate_heatmap_data(queryset=qs)
        assert len(data["risks"]) == 1
        assert data["risks"][0]["risk_id"] == "RISK-002"
        assert data["risks"][0]["level"] == "CRITICAL"

    def test_generate_heatmap_data_multiple_risks_same_cell(self) -> None:
        """同じセルに複数リスクが入るとcount加算"""
        risk1 = MagicMock()
        risk1.risk_id = "RISK-A"
        risk1.title = "A"
        risk1.likelihood_inherent = 2
        risk1.impact_inherent = 2

        risk2 = MagicMock()
        risk2.risk_id = "RISK-B"
        risk2.title = "B"
        risk2.likelihood_inherent = 2
        risk2.impact_inherent = 2

        qs = MagicMock()
        qs.only.return_value = [risk1, risk2]

        data = RiskHeatmapService.generate_heatmap_data(queryset=qs)
        cell = data["matrix"][1][1]
        assert cell["count"] == 2

    def test_risk_summary_with_mock(self) -> None:
        """get_risk_summary がモックQSで正しく動作する"""
        mock_risk = MagicMock()
        mock_risk.likelihood_inherent = 5
        mock_risk.impact_inherent = 5

        qs = MagicMock()
        qs.count.return_value = 1
        qs.values.return_value.annotate.return_value = []
        qs.only.return_value = [mock_risk]

        summary = RiskHeatmapService.get_risk_summary(queryset=qs)
        assert summary["total"] == 1
        assert "by_level" in summary
        assert "by_status" in summary
        assert "by_category" in summary
        assert summary["by_level"]["CRITICAL"] == 1

    def test_risk_summary_empty_qs(self) -> None:
        """空クエリセットのサマリー"""
        qs = MagicMock()
        qs.count.return_value = 0
        qs.values.return_value.annotate.return_value = []
        qs.only.return_value = []

        summary = RiskHeatmapService.get_risk_summary(queryset=qs)
        assert summary["total"] == 0
        assert summary["by_level"] == {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    def test_risk_summary_level_colors(self) -> None:
        """level_colors に全4レベルが含まれる"""
        qs = MagicMock()
        qs.count.return_value = 0
        qs.values.return_value.annotate.return_value = []
        qs.only.return_value = []

        summary = RiskHeatmapService.get_risk_summary(queryset=qs)
        assert len(summary["level_colors"]) == 4
        assert "#22c55e" in summary["level_colors"].values()


# ---------------------------------------------------------------------------
# SoAGenerator — Mockテスト
# ---------------------------------------------------------------------------
class TestSoAGeneratorBuildSoAData:
    """SoAGenerator._build_soa_data のテスト"""

    def test_build_soa_data_returns_list(self) -> None:
        """戻り値がリストである"""
        from apps.reports.services import SoAGenerator

        mock_ctrl = MagicMock()
        mock_ctrl.control_id = "A.5.1"
        mock_ctrl.domain = "organizational"
        mock_ctrl.title = "テスト管理策"
        mock_ctrl.description = "テスト"
        mock_ctrl.is_applicable = True
        mock_ctrl.exclusion_reason = ""
        mock_ctrl.implementation_status = "implemented"
        mock_ctrl.implementation_notes = "完了"
        mock_ctrl.owner = None
        mock_ctrl.evidence_required = ["doc1"]
        mock_ctrl.nist_csf_mapping = ["GV.PO-01"]
        mock_ctrl.last_reviewed_at = None
        mock_ctrl.get_domain_display.return_value = "組織的管理策"
        mock_ctrl.get_implementation_status_display.return_value = "実施済み"

        with patch("apps.reports.services.ISO27001Control") as mock_model:
            mock_model.objects.all.return_value.order_by.return_value = [mock_ctrl]
            result = SoAGenerator._build_soa_data()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["control_id"] == "A.5.1"
        assert result[0]["is_applicable"] is True
        assert result[0]["implementation_status"] == "implemented"

    def test_build_soa_data_excluded_control(self) -> None:
        """除外管理策の exclusion_reason が正しくセットされる"""
        from apps.reports.services import SoAGenerator

        mock_ctrl = MagicMock()
        mock_ctrl.control_id = "A.7.1"
        mock_ctrl.domain = "physical"
        mock_ctrl.title = "物理的入退管理"
        mock_ctrl.description = ""
        mock_ctrl.is_applicable = False
        mock_ctrl.exclusion_reason = "クラウドのみのため物理アクセスなし"
        mock_ctrl.implementation_status = "not_started"
        mock_ctrl.implementation_notes = ""
        mock_ctrl.owner = None
        mock_ctrl.evidence_required = []
        mock_ctrl.nist_csf_mapping = []
        mock_ctrl.last_reviewed_at = None
        mock_ctrl.get_domain_display.return_value = "物理的管理策"
        mock_ctrl.get_implementation_status_display.return_value = "未着手"

        with patch("apps.reports.services.ISO27001Control") as mock_model:
            mock_model.objects.all.return_value.order_by.return_value = [mock_ctrl]
            result = SoAGenerator._build_soa_data()

        assert result[0]["is_applicable"] is False
        assert result[0]["exclusion_reason"] == "クラウドのみのため物理アクセスなし"


class TestSoAGeneratorSummaryStatistics:
    """SoAGenerator._get_summary_statistics のテスト"""

    def test_summary_all_applicable(self) -> None:
        """全管理策が適用の場合"""
        from apps.reports.services import SoAGenerator

        soa_data = [
            {"is_applicable": True, "implementation_status": "implemented", "domain": "organizational"},
            {"is_applicable": True, "implementation_status": "in_progress", "domain": "people"},
            {"is_applicable": True, "implementation_status": "implemented", "domain": "organizational"},
        ]
        result = SoAGenerator._get_summary_statistics(soa_data)
        assert result["total_controls"] == 3
        assert result["applicable"] == 3
        assert result["not_applicable"] == 0
        assert result["by_status"]["implemented"] == 2
        assert result["by_status"]["in_progress"] == 1

    def test_summary_with_exclusions(self) -> None:
        """除外あり"""
        from apps.reports.services import SoAGenerator

        soa_data = [
            {"is_applicable": True, "implementation_status": "implemented", "domain": "organizational"},
            {"is_applicable": False, "implementation_status": "not_started", "domain": "physical"},
        ]
        result = SoAGenerator._get_summary_statistics(soa_data)
        assert result["applicable"] == 1
        assert result["not_applicable"] == 1

    def test_summary_domain_breakdown(self) -> None:
        """ドメイン別の内訳が正しい"""
        from apps.reports.services import SoAGenerator

        soa_data = [
            {"is_applicable": True, "implementation_status": "implemented", "domain": "organizational"},
            {"is_applicable": True, "implementation_status": "not_started", "domain": "organizational"},
            {"is_applicable": True, "implementation_status": "implemented", "domain": "technological"},
        ]
        result = SoAGenerator._get_summary_statistics(soa_data)
        assert result["by_domain"]["organizational"]["total"] == 2
        assert result["by_domain"]["organizational"]["implemented"] == 1
        assert result["by_domain"]["technological"]["implemented"] == 1

    def test_summary_empty_data(self) -> None:
        """空データ"""
        from apps.reports.services import SoAGenerator

        result = SoAGenerator._get_summary_statistics([])
        assert result["total_controls"] == 0
        assert result["applicable"] == 0

    def test_summary_has_generated_at(self) -> None:
        """generated_at キーが含まれる"""
        from apps.reports.services import SoAGenerator

        result = SoAGenerator._get_summary_statistics([])
        assert "generated_at" in result


class TestSoAGeneratorPdfData:
    """SoAGenerator.generate_pdf_data のテスト"""

    def test_pdf_data_structure(self) -> None:
        """PDF用データに必須キーが含まれる"""
        from apps.reports.services import SoAGenerator

        mock_ctrl = MagicMock()
        mock_ctrl.control_id = "A.5.1"
        mock_ctrl.domain = "organizational"
        mock_ctrl.title = "テスト"
        mock_ctrl.description = ""
        mock_ctrl.is_applicable = True
        mock_ctrl.exclusion_reason = ""
        mock_ctrl.implementation_status = "implemented"
        mock_ctrl.implementation_notes = ""
        mock_ctrl.owner = None
        mock_ctrl.evidence_required = []
        mock_ctrl.nist_csf_mapping = []
        mock_ctrl.last_reviewed_at = None
        mock_ctrl.get_domain_display.return_value = "組織的管理策"
        mock_ctrl.get_implementation_status_display.return_value = "実施済み"

        with patch("apps.reports.services.ISO27001Control") as mock_model:
            mock_model.objects.all.return_value.order_by.return_value = [mock_ctrl]
            result = SoAGenerator.generate_pdf_data()

        for key in ("title", "generated_at", "controls", "summary", "domains"):
            assert key in result
        assert len(result["controls"]) == 1
        assert len(result["domains"]) == 1


# ---------------------------------------------------------------------------
# AuditStatisticsService — Mockテスト
# ---------------------------------------------------------------------------
class TestAuditStatisticsServiceFindingsSummary:
    """AuditStatisticsService.get_findings_summary のテスト"""

    def test_findings_summary_with_all_types(self) -> None:
        """全所見タイプがある場合のサマリー"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        qs.values.return_value.annotate.return_value = [
            {"finding_type": "major_nc", "count": 2},
            {"finding_type": "minor_nc", "count": 3},
            {"finding_type": "observation", "count": 5},
            {"finding_type": "positive", "count": 1},
        ]
        result = AuditStatisticsService.get_findings_summary(queryset=qs)
        assert result["total"] == 11
        assert result["nonconformities"] == 5
        assert result["observations"] == 5
        assert result["positive_findings"] == 1

    def test_findings_summary_empty(self) -> None:
        """所見なしの場合"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        qs.values.return_value.annotate.return_value = []
        result = AuditStatisticsService.get_findings_summary(queryset=qs)
        assert result["total"] == 0
        assert result["nonconformities"] == 0

    def test_findings_summary_only_positive(self) -> None:
        """優良事項のみの場合"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        qs.values.return_value.annotate.return_value = [
            {"finding_type": "positive", "count": 4},
        ]
        result = AuditStatisticsService.get_findings_summary(queryset=qs)
        assert result["total"] == 4
        assert result["nonconformities"] == 0
        assert result["positive_findings"] == 4

    def test_findings_summary_returns_required_keys(self) -> None:
        """戻り値に必須キーが含まれる"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        qs.values.return_value.annotate.return_value = []
        result = AuditStatisticsService.get_findings_summary(queryset=qs)
        for key in ("total", "by_type", "nonconformities", "observations", "positive_findings"):
            assert key in result


class TestAuditStatisticsServiceCAPSummary:
    """AuditStatisticsService.get_cap_status_summary のテスト"""

    def test_cap_summary_all_closed(self) -> None:
        """全CAP完了の場合"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        cap_qs = MagicMock()
        cap_qs.values.return_value.annotate.return_value = [
            {"cap_status": "closed", "count": 5},
        ]
        overdue_qs = MagicMock()
        overdue_qs.count.return_value = 0
        cap_qs.filter.return_value.exclude.return_value = overdue_qs
        qs.filter.return_value = cap_qs

        result = AuditStatisticsService.get_cap_status_summary(queryset=qs)
        assert result["total_caps"] == 5
        assert result["completion_rate"] == 100.0
        assert result["overdue"] == 0

    def test_cap_summary_none_completed(self) -> None:
        """未完了の場合"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        cap_qs = MagicMock()
        cap_qs.values.return_value.annotate.return_value = [
            {"cap_status": "open", "count": 3},
            {"cap_status": "in_progress", "count": 2},
        ]
        overdue_qs = MagicMock()
        overdue_qs.count.return_value = 1
        cap_qs.filter.return_value.exclude.return_value = overdue_qs
        qs.filter.return_value = cap_qs

        result = AuditStatisticsService.get_cap_status_summary(queryset=qs)
        assert result["total_caps"] == 5
        assert result["completion_rate"] == 0.0
        assert result["overdue"] == 1

    def test_cap_summary_mixed_status(self) -> None:
        """混在ステータス"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        cap_qs = MagicMock()
        cap_qs.values.return_value.annotate.return_value = [
            {"cap_status": "open", "count": 1},
            {"cap_status": "in_progress", "count": 1},
            {"cap_status": "verified", "count": 1},
            {"cap_status": "closed", "count": 1},
        ]
        overdue_qs = MagicMock()
        overdue_qs.count.return_value = 0
        cap_qs.filter.return_value.exclude.return_value = overdue_qs
        qs.filter.return_value = cap_qs

        result = AuditStatisticsService.get_cap_status_summary(queryset=qs)
        assert result["total_caps"] == 4
        assert result["completion_rate"] == 50.0

    def test_cap_summary_empty(self) -> None:
        """CAP要件なし"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        cap_qs = MagicMock()
        cap_qs.values.return_value.annotate.return_value = []
        overdue_qs = MagicMock()
        overdue_qs.count.return_value = 0
        cap_qs.filter.return_value.exclude.return_value = overdue_qs
        qs.filter.return_value = cap_qs

        result = AuditStatisticsService.get_cap_status_summary(queryset=qs)
        assert result["total_caps"] == 0
        assert result["completion_rate"] == 0.0

    def test_cap_summary_returns_required_keys(self) -> None:
        """戻り値に必須キーが含まれる"""
        from apps.audits.services import AuditStatisticsService

        qs = MagicMock()
        cap_qs = MagicMock()
        cap_qs.values.return_value.annotate.return_value = []
        overdue_qs = MagicMock()
        overdue_qs.count.return_value = 0
        cap_qs.filter.return_value.exclude.return_value = overdue_qs
        qs.filter.return_value = cap_qs

        result = AuditStatisticsService.get_cap_status_summary(queryset=qs)
        for key in ("total_caps", "by_status", "completion_rate", "overdue"):
            assert key in result


# ---------------------------------------------------------------------------
# ComplianceRateService — DB統合テスト
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestComplianceRateServiceDB:
    """ComplianceRateService のDB統合テスト"""

    def test_overall_rate_with_real_controls(self) -> None:
        """実DBでの全体準拠率"""
        from apps.controls.models import ISO27001Control

        ISO27001Control.objects.create(
            control_id="A.5.1",
            domain="organizational",
            title="テスト管理策1",
            is_applicable=True,
            implementation_status="implemented",
        )
        ISO27001Control.objects.create(
            control_id="A.5.2",
            domain="organizational",
            title="テスト管理策2",
            is_applicable=True,
            implementation_status="not_started",
        )
        result = ComplianceRateService.calculate_overall_rate()
        assert result["total"] == 2
        assert result["applicable"] == 2
        assert result["implemented"] == 1
        assert result["compliance_rate"] == 50.0

    def test_by_domain_with_real_controls(self) -> None:
        """実DBでのドメイン別準拠率"""
        from apps.controls.models import ISO27001Control

        ISO27001Control.objects.create(
            control_id="A.5.10",
            domain="organizational",
            title="組織管理策",
            is_applicable=True,
            implementation_status="implemented",
        )
        ISO27001Control.objects.create(
            control_id="A.8.10",
            domain="technological",
            title="技術管理策",
            is_applicable=True,
            implementation_status="not_started",
        )
        result = ComplianceRateService.calculate_by_domain()
        domains = {r["domain"] for r in result}
        assert "organizational" in domains
        assert "technological" in domains

        org = next(r for r in result if r["domain"] == "organizational")
        assert org["compliance_rate"] == 100.0

    def test_trend_with_real_controls(self) -> None:
        """実DBでのトレンド"""
        from apps.controls.models import ISO27001Control

        ISO27001Control.objects.create(
            control_id="A.5.20",
            domain="organizational",
            title="トレンドテスト",
            is_applicable=True,
            implementation_status="implemented",
        )
        result = ComplianceRateService.calculate_trend(months=3)
        assert len(result) == 3
        # 最新月は実施済み1件なので compliance_rate > 0
        assert result[-1]["compliance_rate"] > 0


# ---------------------------------------------------------------------------
# RiskHeatmapService — DB統合テスト
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestRiskHeatmapServiceDB:
    """RiskHeatmapService のDB統合テスト"""

    def test_heatmap_data_with_real_risk(self) -> None:
        """実DBでのヒートマップ生成"""
        from apps.risks.models import Risk

        Risk.objects.create(
            risk_id="RISK-HM-001",
            title="ヒートマップテスト",
            category="IT",
            likelihood_inherent=4,
            impact_inherent=5,
            status="open",
        )
        data = RiskHeatmapService.generate_heatmap_data()
        assert data["matrix"][3][4]["count"] == 1
        assert len(data["risks"]) == 1
        assert data["risks"][0]["level"] == "CRITICAL"

    def test_risk_summary_with_real_risks(self) -> None:
        """実DBでのリスクサマリー"""
        from apps.risks.models import Risk

        Risk.objects.create(
            risk_id="RISK-SUM-001",
            title="サマリテスト1",
            category="IT",
            likelihood_inherent=1,
            impact_inherent=1,
            status="open",
        )
        Risk.objects.create(
            risk_id="RISK-SUM-002",
            title="サマリテスト2",
            category="Construction",
            likelihood_inherent=5,
            impact_inherent=5,
            status="closed",
        )
        summary = RiskHeatmapService.get_risk_summary()
        assert summary["total"] == 2
        assert summary["by_level"]["LOW"] == 1
        assert summary["by_level"]["CRITICAL"] == 1
        assert "IT" in summary["by_category"]
        assert "Construction" in summary["by_category"]


# ---------------------------------------------------------------------------
# AuditStatisticsService — DB統合テスト
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestAuditStatisticsServiceDB:
    """AuditStatisticsService のDB統合テスト"""

    def _create_audit(self) -> Any:
        """テスト用監査を作成"""
        from apps.audits.models import Audit

        return Audit.objects.create(
            audit_id="AUD-SVC-001",
            title="サービステスト監査",
            audit_type="ISO27001定期監査",
            target_department="IT部門",
            planned_start="2026-04-01",
            planned_end="2026-04-15",
            status="completed",
        )

    def test_findings_summary_db(self) -> None:
        """実DBでの所見サマリー"""
        from apps.audits.models import AuditFinding
        from apps.audits.services import AuditStatisticsService

        audit = self._create_audit()
        AuditFinding.objects.create(
            audit=audit,
            finding_id="FND-SVC-001",
            finding_type="major_nc",
            title="重大不適合テスト",
            description="テスト",
        )
        AuditFinding.objects.create(
            audit=audit,
            finding_id="FND-SVC-002",
            finding_type="observation",
            title="観察事項テスト",
            description="テスト",
        )
        result = AuditStatisticsService.get_findings_summary(audit=audit)
        assert result["total"] == 2
        assert result["nonconformities"] == 1
        assert result["observations"] == 1

    def test_cap_summary_db(self) -> None:
        """実DBでのCAP集計"""
        from apps.audits.models import AuditFinding
        from apps.audits.services import AuditStatisticsService

        audit = self._create_audit()
        AuditFinding.objects.create(
            audit=audit,
            finding_id="FND-CAP-001",
            finding_type="minor_nc",
            title="軽微不適合",
            description="テスト",
            cap_required=True,
            cap_status="closed",
            cap_due_date="2026-03-01",
        )
        AuditFinding.objects.create(
            audit=audit,
            finding_id="FND-CAP-002",
            finding_type="major_nc",
            title="重大不適合",
            description="テスト",
            cap_required=True,
            cap_status="open",
            cap_due_date="2026-03-01",
        )
        result = AuditStatisticsService.get_cap_status_summary(audit=audit)
        assert result["total_caps"] == 2
        assert result["completion_rate"] == 50.0
        # cap_due_date が過去で open のものが overdue
        assert result["overdue"] == 1
