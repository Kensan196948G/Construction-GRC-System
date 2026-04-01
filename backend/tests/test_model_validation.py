"""モデルバリデーション詳細テスト

各モデルのフィールド選択肢、計算プロパティ、ステータス遷移、
メタデータを網羅的に検証する。DB不要テストとDB必須テストの混合。
"""

from __future__ import annotations

import pytest

from apps.audits.models import Audit, AuditFinding
from apps.compliance.models import ComplianceRequirement
from apps.controls.models import ISO27001Control, NistCSFCategory
from apps.frameworks.models import Framework
from apps.reports.models import Report
from apps.risks.models import Risk


# ---------------------------------------------------------------------------
# Risk モデル
# ---------------------------------------------------------------------------
class TestRiskCategoryChoices:
    """Risk.Category の選択肢テスト"""

    def test_has_six_categories(self) -> None:
        assert len(Risk.Category.choices) == 6

    def test_all_expected_categories_present(self) -> None:
        values = {c[0] for c in Risk.Category.choices}
        expected = {"IT", "Physical", "Legal", "Construction", "Financial", "Operational"}
        assert values == expected

    def test_category_labels_are_japanese(self) -> None:
        labels = {c[1] for c in Risk.Category.choices}
        assert "IT・情報セキュリティ" in labels
        assert "建設・施工" in labels


class TestRiskTreatmentStrategy:
    """Risk.TreatmentStrategy の選択肢テスト"""

    def test_has_four_strategies(self) -> None:
        assert len(Risk.TreatmentStrategy.choices) == 4

    def test_all_strategies_present(self) -> None:
        values = {s[0] for s in Risk.TreatmentStrategy.choices}
        assert values == {"accept", "mitigate", "transfer", "avoid"}

    def test_strategy_labels(self) -> None:
        labels = dict(Risk.TreatmentStrategy.choices)
        assert labels["accept"] == "受容"
        assert labels["mitigate"] == "軽減"
        assert labels["transfer"] == "移転"
        assert labels["avoid"] == "回避"


class TestRiskStatus:
    """Risk.Status の選択肢テスト"""

    def test_has_four_statuses(self) -> None:
        assert len(Risk.Status.choices) == 4

    def test_all_statuses_present(self) -> None:
        values = {s[0] for s in Risk.Status.choices}
        assert values == {"open", "in_progress", "closed", "accepted"}

    def test_default_status_is_open(self) -> None:
        risk = Risk(likelihood_inherent=1, impact_inherent=1)
        assert risk.status == "open"


class TestRiskScoreCalculation:
    """Risk のスコア計算プロパティテスト"""

    @pytest.mark.parametrize(
        ("likelihood", "impact", "expected_score"),
        [
            (1, 1, 1),
            (1, 5, 5),
            (5, 1, 5),
            (3, 3, 9),
            (5, 5, 25),
            (2, 4, 8),
            (4, 2, 8),
        ],
    )
    def test_risk_score_inherent(self, likelihood: int, impact: int, expected_score: int) -> None:
        risk = Risk(likelihood_inherent=likelihood, impact_inherent=impact)
        assert risk.risk_score_inherent == expected_score

    def test_risk_score_residual_with_values(self) -> None:
        risk = Risk(
            likelihood_inherent=5,
            impact_inherent=5,
            likelihood_residual=2,
            impact_residual=3,
        )
        assert risk.risk_score_residual == 6

    def test_risk_score_residual_none_when_missing(self) -> None:
        risk = Risk(likelihood_inherent=5, impact_inherent=5)
        assert risk.risk_score_residual is None

    def test_risk_score_residual_none_when_partial(self) -> None:
        """likelihood_residual のみ設定の場合 None"""
        risk = Risk(likelihood_inherent=5, impact_inherent=5, likelihood_residual=2)
        assert risk.risk_score_residual is None


class TestRiskLevelProperty:
    """Risk.risk_level プロパティの境界値テスト"""

    @pytest.mark.parametrize(
        ("likelihood", "impact", "expected_level"),
        [
            (1, 1, "LOW"),
            (2, 2, "LOW"),
            (1, 4, "LOW"),
            (4, 1, "LOW"),
            (1, 5, "MEDIUM"),
            (5, 1, "MEDIUM"),
            (3, 3, "MEDIUM"),
            (2, 5, "HIGH"),
            (5, 2, "HIGH"),
            (3, 4, "HIGH"),
            (4, 3, "HIGH"),
            (3, 5, "CRITICAL"),
            (5, 3, "CRITICAL"),
            (5, 5, "CRITICAL"),
            (4, 4, "CRITICAL"),
        ],
    )
    def test_risk_level(self, likelihood: int, impact: int, expected_level: str) -> None:
        risk = Risk(likelihood_inherent=likelihood, impact_inherent=impact)
        assert risk.risk_level == expected_level

    def test_risk_level_all_25_combinations_valid(self) -> None:
        """全25通りが有効なレベルを返す"""
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        for li in range(1, 6):
            for im in range(1, 6):
                risk = Risk(likelihood_inherent=li, impact_inherent=im)
                assert risk.risk_level in valid_levels


class TestRiskStrRepresentation:
    """Risk.__str__ テスト"""

    def test_str_format(self) -> None:
        risk = Risk(risk_id="RISK-001", title="テスト", likelihood_inherent=1, impact_inherent=1)
        assert str(risk) == "RISK-001: テスト"


class TestRiskMeta:
    """Risk の Meta クラステスト"""

    def test_ordering(self) -> None:
        assert Risk._meta.ordering == ["-created_at"]

    def test_verbose_name(self) -> None:
        assert Risk._meta.verbose_name == "リスク"


# ---------------------------------------------------------------------------
# ComplianceRequirement モデル
# ---------------------------------------------------------------------------
class TestComplianceRequirementFrameworkChoices:
    """ComplianceRequirement.Framework の選択肢テスト"""

    def test_has_seven_frameworks(self) -> None:
        assert len(ComplianceRequirement.Framework.choices) == 7

    def test_includes_construction_laws(self) -> None:
        values = {f[0] for f in ComplianceRequirement.Framework.choices}
        assert "construction_law" in values
        assert "quality_law" in values
        assert "safety_law" in values

    def test_includes_standards(self) -> None:
        values = {f[0] for f in ComplianceRequirement.Framework.choices}
        assert "iso27001" in values
        assert "nist_csf" in values

    def test_includes_subcontract_law(self) -> None:
        values = {f[0] for f in ComplianceRequirement.Framework.choices}
        assert "subcontract_law" in values


class TestComplianceStatusChoices:
    """ComplianceRequirement.ComplianceStatus の選択肢テスト"""

    def test_has_four_statuses(self) -> None:
        assert len(ComplianceRequirement.ComplianceStatus.choices) == 4

    def test_all_statuses_present(self) -> None:
        values = {s[0] for s in ComplianceRequirement.ComplianceStatus.choices}
        assert values == {"compliant", "non_compliant", "partial", "unknown"}

    def test_default_status_is_unknown(self) -> None:
        req = ComplianceRequirement()
        assert req.compliance_status == "unknown"


class TestComplianceFrequencyChoices:
    """ComplianceRequirement.Frequency の選択肢テスト"""

    def test_has_four_frequencies(self) -> None:
        assert len(ComplianceRequirement.Frequency.choices) == 4

    def test_all_frequencies_present(self) -> None:
        values = {f[0] for f in ComplianceRequirement.Frequency.choices}
        assert values == {"annual", "quarterly", "monthly", "ongoing"}


class TestComplianceRequirementStr:
    """ComplianceRequirement.__str__ テスト"""

    def test_str_format(self) -> None:
        req = ComplianceRequirement(req_id="KEN-001", title="テスト要件")
        assert str(req) == "KEN-001: テスト要件"


class TestComplianceRequirementMeta:
    """ComplianceRequirement の Meta テスト"""

    def test_ordering(self) -> None:
        assert ComplianceRequirement._meta.ordering == ["framework", "req_id"]

    def test_verbose_name(self) -> None:
        assert ComplianceRequirement._meta.verbose_name == "法令要件"


# ---------------------------------------------------------------------------
# Audit モデル
# ---------------------------------------------------------------------------
class TestAuditStatusChoices:
    """Audit.Status の選択肢テスト"""

    def test_has_four_statuses(self) -> None:
        assert len(Audit.Status.choices) == 4

    def test_all_statuses_present(self) -> None:
        values = {s[0] for s in Audit.Status.choices}
        assert values == {"planned", "in_progress", "completed", "cancelled"}

    def test_status_labels_japanese(self) -> None:
        labels = dict(Audit.Status.choices)
        assert labels["planned"] == "計画済み"
        assert labels["completed"] == "完了"
        assert labels["cancelled"] == "中止"

    def test_default_status_is_planned(self) -> None:
        audit = Audit()
        assert audit.status == "planned"


class TestAuditStr:
    """Audit.__str__ テスト"""

    def test_str_format(self) -> None:
        audit = Audit(audit_id="AUD-001", title="テスト監査")
        assert str(audit) == "AUD-001: テスト監査"


class TestAuditMeta:
    """Audit の Meta テスト"""

    def test_ordering(self) -> None:
        assert Audit._meta.ordering == ["-planned_start"]

    def test_verbose_name(self) -> None:
        assert Audit._meta.verbose_name == "監査"


# ---------------------------------------------------------------------------
# AuditFinding モデル
# ---------------------------------------------------------------------------
class TestAuditFindingTypeChoices:
    """AuditFinding.FindingType の選択肢テスト"""

    def test_has_four_types(self) -> None:
        assert len(AuditFinding.FindingType.choices) == 4

    def test_all_types_present(self) -> None:
        values = {t[0] for t in AuditFinding.FindingType.choices}
        assert values == {"major_nc", "minor_nc", "observation", "positive"}

    def test_type_labels_japanese(self) -> None:
        labels = dict(AuditFinding.FindingType.choices)
        assert labels["major_nc"] == "重大不適合"
        assert labels["minor_nc"] == "軽微不適合"
        assert labels["observation"] == "観察事項"
        assert labels["positive"] == "優良事項"


class TestAuditFindingCAPStatusChoices:
    """AuditFinding.CAPStatus の選択肢テスト"""

    def test_has_four_statuses(self) -> None:
        assert len(AuditFinding.CAPStatus.choices) == 4

    def test_all_statuses_present(self) -> None:
        values = {s[0] for s in AuditFinding.CAPStatus.choices}
        assert values == {"open", "in_progress", "verified", "closed"}

    def test_default_cap_status_is_open(self) -> None:
        finding = AuditFinding()
        assert finding.cap_status == "open"

    def test_default_cap_required_is_true(self) -> None:
        finding = AuditFinding()
        assert finding.cap_required is True


class TestAuditFindingStr:
    """AuditFinding.__str__ テスト"""

    def test_str_format(self) -> None:
        finding = AuditFinding(finding_id="FND-001", title="テスト所見")
        assert str(finding) == "FND-001: テスト所見"


class TestAuditFindingMeta:
    """AuditFinding の Meta テスト"""

    def test_ordering(self) -> None:
        assert AuditFinding._meta.ordering == ["finding_id"]


# ---------------------------------------------------------------------------
# Report モデル
# ---------------------------------------------------------------------------
class TestReportTypeChoices:
    """Report.ReportType の選択肢テスト"""

    def test_has_six_types(self) -> None:
        assert len(Report.ReportType.choices) == 6

    def test_all_types_present(self) -> None:
        values = {t[0] for t in Report.ReportType.choices}
        expected = {
            "grc_dashboard",
            "iso27001_annual",
            "compliance_status",
            "risk_trend",
            "soa",
            "audit_report",
        }
        assert values == expected

    def test_type_labels_japanese(self) -> None:
        labels = dict(Report.ReportType.choices)
        assert labels["grc_dashboard"] == "経営層GRCダッシュボード"
        assert labels["soa"] == "適用宣言書（SoA）"
        assert labels["audit_report"] == "監査報告書"


class TestReportFormat:
    """Report のフォーマットフィールドテスト"""

    def test_default_format_is_pdf(self) -> None:
        report = Report()
        assert report.format == "pdf"


class TestReportMeta:
    """Report の Meta テスト"""

    def test_ordering(self) -> None:
        assert Report._meta.ordering == ["-created_at"]

    def test_verbose_name(self) -> None:
        assert Report._meta.verbose_name == "レポート"


# ---------------------------------------------------------------------------
# ISO27001Control モデル
# ---------------------------------------------------------------------------
class TestISO27001ControlDomainChoices:
    """ISO27001Control.Domain の選択肢テスト"""

    def test_has_four_domains(self) -> None:
        assert len(ISO27001Control.Domain.choices) == 4

    def test_all_domains_present(self) -> None:
        values = {d[0] for d in ISO27001Control.Domain.choices}
        assert values == {"organizational", "people", "physical", "technological"}

    def test_domain_labels_japanese(self) -> None:
        labels = dict(ISO27001Control.Domain.choices)
        assert labels["organizational"] == "組織的管理策"
        assert labels["people"] == "人的管理策"
        assert labels["physical"] == "物理的管理策"
        assert labels["technological"] == "技術的管理策"


class TestISO27001ControlImplementationStatus:
    """ISO27001Control.ImplementationStatus の選択肢テスト"""

    def test_has_four_statuses(self) -> None:
        assert len(ISO27001Control.ImplementationStatus.choices) == 4

    def test_all_statuses_present(self) -> None:
        values = {s[0] for s in ISO27001Control.ImplementationStatus.choices}
        assert values == {"not_started", "in_progress", "implemented", "partially_implemented"}

    def test_default_status_is_not_started(self) -> None:
        ctrl = ISO27001Control()
        assert ctrl.implementation_status == "not_started"

    def test_default_is_applicable_true(self) -> None:
        ctrl = ISO27001Control()
        assert ctrl.is_applicable is True


class TestISO27001ControlStr:
    """ISO27001Control.__str__ テスト"""

    def test_str_format(self) -> None:
        ctrl = ISO27001Control(control_id="A.5.1", title="テスト管理策")
        assert str(ctrl) == "A.5.1: テスト管理策"


class TestISO27001ControlMeta:
    """ISO27001Control の Meta テスト"""

    def test_ordering(self) -> None:
        assert ISO27001Control._meta.ordering == ["control_id"]

    def test_verbose_name(self) -> None:
        assert ISO27001Control._meta.verbose_name == "ISO27001管理策"


# ---------------------------------------------------------------------------
# NistCSFCategory モデル
# ---------------------------------------------------------------------------
class TestNistCSFCategoryStr:
    """NistCSFCategory.__str__ テスト"""

    def test_str_format(self) -> None:
        cat = NistCSFCategory(category_id="GV.OC", category_name_ja="組織コンテキスト")
        assert str(cat) == "GV.OC: 組織コンテキスト"


class TestNistCSFCategoryMeta:
    """NistCSFCategory の Meta テスト"""

    def test_ordering(self) -> None:
        assert NistCSFCategory._meta.ordering == ["category_id"]


# ---------------------------------------------------------------------------
# Framework モデル
# ---------------------------------------------------------------------------
class TestFrameworkCategoryChoices:
    """Framework.Category の選択肢テスト"""

    def test_has_four_categories(self) -> None:
        assert len(Framework.Category.choices) == 4

    def test_all_categories_present(self) -> None:
        values = {c[0] for c in Framework.Category.choices}
        assert values == {"security", "compliance", "legal", "quality"}

    def test_category_labels_japanese(self) -> None:
        labels = dict(Framework.Category.choices)
        assert labels["security"] == "セキュリティ"
        assert labels["legal"] == "法令"


class TestFrameworkDefaults:
    """Framework のデフォルト値テスト"""

    def test_default_is_active_true(self) -> None:
        fw = Framework()
        assert fw.is_active is True


class TestFrameworkStr:
    """Framework.__str__ テスト"""

    def test_str_format(self) -> None:
        fw = Framework(code="iso27001", name_ja="ISO27001")
        assert str(fw) == "iso27001: ISO27001"


class TestFrameworkMeta:
    """Framework の Meta テスト"""

    def test_ordering(self) -> None:
        assert Framework._meta.ordering == ["code"]

    def test_verbose_name(self) -> None:
        assert Framework._meta.verbose_name == "フレームワーク定義"


# ---------------------------------------------------------------------------
# DB統合テスト: モデル作成・保存
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestRiskModelDB:
    """Risk モデルのDB保存テスト"""

    def test_create_and_retrieve(self) -> None:
        Risk.objects.create(
            risk_id="RISK-VAL-001",
            title="バリデーションテスト",
            category="IT",
            likelihood_inherent=3,
            impact_inherent=4,
            status="open",
        )
        retrieved = Risk.objects.get(risk_id="RISK-VAL-001")
        assert retrieved.title == "バリデーションテスト"
        assert retrieved.risk_score_inherent == 12
        assert retrieved.risk_level == "HIGH"

    def test_unique_risk_id(self) -> None:
        """risk_id の一意制約"""
        from django.db import IntegrityError

        Risk.objects.create(
            risk_id="RISK-VAL-UNQ",
            title="一意テスト1",
            category="IT",
            likelihood_inherent=1,
            impact_inherent=1,
        )
        with pytest.raises(IntegrityError):
            Risk.objects.create(
                risk_id="RISK-VAL-UNQ",
                title="一意テスト2",
                category="IT",
                likelihood_inherent=2,
                impact_inherent=2,
            )


@pytest.mark.django_db
@pytest.mark.integration
class TestComplianceRequirementModelDB:
    """ComplianceRequirement モデルのDB保存テスト"""

    def test_create_and_retrieve(self) -> None:
        ComplianceRequirement.objects.create(
            req_id="KEN-VAL-001",
            framework="construction_law",
            title="バリデーションテスト",
            compliance_status="unknown",
        )
        retrieved = ComplianceRequirement.objects.get(req_id="KEN-VAL-001")
        assert retrieved.framework == "construction_law"
        assert retrieved.compliance_status == "unknown"

    def test_unique_req_id(self) -> None:
        """req_id の一意制約"""
        from django.db import IntegrityError

        ComplianceRequirement.objects.create(
            req_id="KEN-VAL-UNQ",
            framework="iso27001",
            title="一意テスト1",
        )
        with pytest.raises(IntegrityError):
            ComplianceRequirement.objects.create(
                req_id="KEN-VAL-UNQ",
                framework="nist_csf",
                title="一意テスト2",
            )


@pytest.mark.django_db
@pytest.mark.integration
class TestAuditModelDB:
    """Audit モデルのDB保存テスト"""

    def test_create_audit_with_finding(self) -> None:
        audit = Audit.objects.create(
            audit_id="AUD-VAL-001",
            title="監査バリデーションテスト",
            audit_type="ISO27001定期監査",
            target_department="IT部門",
            planned_start="2026-04-01",
            planned_end="2026-04-15",
        )
        finding = AuditFinding.objects.create(
            audit=audit,
            finding_id="FND-VAL-001",
            finding_type="major_nc",
            title="テスト所見",
            description="テスト",
        )
        assert finding.audit == audit
        assert audit.findings.count() == 1

    def test_cascade_delete(self) -> None:
        """監査削除で所見も削除される"""
        audit = Audit.objects.create(
            audit_id="AUD-VAL-002",
            title="カスケードテスト",
            audit_type="ISO27001",
            target_department="IT部門",
            planned_start="2026-04-01",
            planned_end="2026-04-15",
        )
        AuditFinding.objects.create(
            audit=audit,
            finding_id="FND-VAL-002",
            finding_type="observation",
            title="削除テスト",
            description="テスト",
        )
        audit_id = audit.id
        audit.delete()
        assert AuditFinding.objects.filter(audit_id=audit_id).count() == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestISO27001ControlModelDB:
    """ISO27001Control モデルのDB保存テスト"""

    def test_create_and_retrieve(self) -> None:
        ISO27001Control.objects.create(
            control_id="A.5.99",
            domain="organizational",
            title="バリデーションテスト管理策",
            is_applicable=True,
            implementation_status="implemented",
        )
        retrieved = ISO27001Control.objects.get(control_id="A.5.99")
        assert retrieved.domain == "organizational"
        assert retrieved.is_applicable is True

    def test_unique_control_id(self) -> None:
        """control_id の一意制約"""
        from django.db import IntegrityError

        ISO27001Control.objects.create(
            control_id="A.5.98",
            domain="organizational",
            title="一意テスト1",
        )
        with pytest.raises(IntegrityError):
            ISO27001Control.objects.create(
                control_id="A.5.98",
                domain="people",
                title="一意テスト2",
            )
