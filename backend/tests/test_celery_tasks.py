"""Celery タスクの正常系テスト

各 shared_task の戻り値・データ構造を検証する。
全テストは DB アクセスが必要なため @pytest.mark.django_db + @pytest.mark.integration。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest


# ---------------------------------------------------------------------------
# compliance タスク
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestCheckAssessmentDeadlines:
    """compliance.check_assessment_deadlines タスク"""

    def test_returns_empty_when_no_requirements(self) -> None:
        from apps.compliance.tasks import check_assessment_deadlines

        result = check_assessment_deadlines()
        assert result["upcoming_assessments"] == 0
        assert result["requirements"] == []

    def test_detects_upcoming_assessment(self) -> None:
        from apps.compliance.models import ComplianceRequirement
        from apps.compliance.tasks import check_assessment_deadlines

        today = datetime.now(tz=UTC).date()
        ComplianceRequirement.objects.create(
            req_id="KEN-TASK-001",
            framework="construction_law",
            title="評価期限テスト",
            compliance_status="unknown",
            next_assessment=today + timedelta(days=10),
        )
        result = check_assessment_deadlines()
        assert result["upcoming_assessments"] == 1
        assert result["requirements"][0]["req_id"] == "KEN-TASK-001"
        assert result["requirements"][0]["days_until"] == 10

    def test_ignores_compliant_requirements(self) -> None:
        """compliance_status が compliant の要件は除外される"""
        from apps.compliance.models import ComplianceRequirement
        from apps.compliance.tasks import check_assessment_deadlines

        today = datetime.now(tz=UTC).date()
        ComplianceRequirement.objects.create(
            req_id="KEN-TASK-002",
            framework="iso27001",
            title="準拠済み",
            compliance_status="compliant",
            next_assessment=today + timedelta(days=5),
        )
        result = check_assessment_deadlines()
        assert result["upcoming_assessments"] == 0

    def test_ignores_past_assessment(self) -> None:
        """next_assessment が過去日の要件は除外される"""
        from apps.compliance.models import ComplianceRequirement
        from apps.compliance.tasks import check_assessment_deadlines

        today = datetime.now(tz=UTC).date()
        ComplianceRequirement.objects.create(
            req_id="KEN-TASK-003",
            framework="quality_law",
            title="期限切れ",
            compliance_status="non_compliant",
            next_assessment=today - timedelta(days=5),
        )
        result = check_assessment_deadlines()
        assert result["upcoming_assessments"] == 0

    def test_ignores_far_future_assessment(self) -> None:
        """next_assessment が30日超先の要件は除外される"""
        from apps.compliance.models import ComplianceRequirement
        from apps.compliance.tasks import check_assessment_deadlines

        today = datetime.now(tz=UTC).date()
        ComplianceRequirement.objects.create(
            req_id="KEN-TASK-004",
            framework="safety_law",
            title="遠い未来",
            compliance_status="partial",
            next_assessment=today + timedelta(days=60),
        )
        result = check_assessment_deadlines()
        assert result["upcoming_assessments"] == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestGenerateComplianceReport:
    """compliance.generate_compliance_report タスク"""

    def test_returns_empty_when_no_data(self) -> None:
        from apps.compliance.tasks import generate_compliance_report

        result = generate_compliance_report()
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_returns_framework_rates(self) -> None:
        from apps.compliance.models import ComplianceRequirement
        from apps.compliance.tasks import generate_compliance_report

        ComplianceRequirement.objects.create(
            req_id="KEN-RPT-001",
            framework="construction_law",
            title="建設業許可",
            compliance_status="compliant",
        )
        ComplianceRequirement.objects.create(
            req_id="KEN-RPT-002",
            framework="construction_law",
            title="経審",
            compliance_status="non_compliant",
        )
        result = generate_compliance_report()
        assert "construction_law" in result
        assert result["construction_law"]["total"] == 2
        assert result["construction_law"]["compliant"] == 1
        assert result["construction_law"]["rate"] == 50.0

    def test_skips_empty_frameworks(self) -> None:
        """データのないフレームワークはスキップされる"""
        from apps.compliance.models import ComplianceRequirement
        from apps.compliance.tasks import generate_compliance_report

        ComplianceRequirement.objects.create(
            req_id="KEN-RPT-003",
            framework="iso27001",
            title="ISO要件",
            compliance_status="compliant",
        )
        result = generate_compliance_report()
        assert "iso27001" in result
        assert "construction_law" not in result


# ---------------------------------------------------------------------------
# controls タスク
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestCheckControlReviews:
    """controls.check_control_reviews タスク"""

    def test_returns_empty_when_no_controls(self) -> None:
        from apps.controls.tasks import check_control_reviews

        result = check_control_reviews()
        assert result["upcoming_reviews"] == 0
        assert result["controls"] == []

    def test_detects_upcoming_review(self) -> None:
        from apps.controls.models import ISO27001Control
        from apps.controls.tasks import check_control_reviews

        today = datetime.now(tz=UTC).date()
        ISO27001Control.objects.create(
            control_id="A.5.99",
            domain="organizational",
            title="レビュー期限テスト",
            is_applicable=True,
            review_date=today + timedelta(days=7),
        )
        result = check_control_reviews()
        assert result["upcoming_reviews"] == 1

    def test_ignores_non_applicable_controls(self) -> None:
        """適用除外の管理策は対象外"""
        from apps.controls.models import ISO27001Control
        from apps.controls.tasks import check_control_reviews

        today = datetime.now(tz=UTC).date()
        ISO27001Control.objects.create(
            control_id="A.7.99",
            domain="physical",
            title="除外管理策",
            is_applicable=False,
            review_date=today + timedelta(days=5),
        )
        result = check_control_reviews()
        assert result["upcoming_reviews"] == 0

    def test_ignores_far_future_review(self) -> None:
        """review_date が14日超先の管理策は対象外"""
        from apps.controls.models import ISO27001Control
        from apps.controls.tasks import check_control_reviews

        today = datetime.now(tz=UTC).date()
        ISO27001Control.objects.create(
            control_id="A.8.99",
            domain="technological",
            title="遠い将来",
            is_applicable=True,
            review_date=today + timedelta(days=30),
        )
        result = check_control_reviews()
        assert result["upcoming_reviews"] == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestCalculateSoAStatus:
    """controls.calculate_soa_status タスク"""

    def test_returns_zero_when_no_controls(self) -> None:
        from apps.controls.tasks import calculate_soa_status

        result = calculate_soa_status()
        assert result["total_applicable"] == 0
        assert result["compliance_rate"] == 0

    def test_calculates_status(self) -> None:
        from apps.controls.models import ISO27001Control
        from apps.controls.tasks import calculate_soa_status

        ISO27001Control.objects.create(
            control_id="A.5.50",
            domain="organizational",
            title="SOAテスト1",
            is_applicable=True,
            implementation_status="implemented",
        )
        ISO27001Control.objects.create(
            control_id="A.5.51",
            domain="organizational",
            title="SOAテスト2",
            is_applicable=True,
            implementation_status="in_progress",
        )
        ISO27001Control.objects.create(
            control_id="A.5.52",
            domain="organizational",
            title="SOAテスト3",
            is_applicable=True,
            implementation_status="not_started",
        )
        ISO27001Control.objects.create(
            control_id="A.7.50",
            domain="physical",
            title="除外",
            is_applicable=False,
        )
        result = calculate_soa_status()
        assert result["total_applicable"] == 3
        assert result["implemented"] == 1
        assert result["in_progress"] == 1
        assert result["not_started"] == 1
        assert result["compliance_rate"] == round(1 / 3 * 100, 1)

    def test_returns_required_keys(self) -> None:
        from apps.controls.tasks import calculate_soa_status

        result = calculate_soa_status()
        for key in ("total_applicable", "implemented", "in_progress", "not_started", "compliance_rate"):
            assert key in result


# ---------------------------------------------------------------------------
# risks タスク
# ---------------------------------------------------------------------------
@pytest.mark.django_db
@pytest.mark.integration
class TestCheckReviewDeadlines:
    """risks.check_review_deadlines タスク"""

    def test_returns_empty_when_no_risks(self) -> None:
        from apps.risks.tasks import check_review_deadlines

        result = check_review_deadlines()
        assert result["upcoming_reviews"] == 0
        assert result["risks"] == []

    def test_detects_upcoming_review(self) -> None:
        from apps.risks.models import Risk
        from apps.risks.tasks import check_review_deadlines

        today = datetime.now(tz=UTC).date()
        Risk.objects.create(
            risk_id="RISK-RV-001",
            title="レビュー期限テスト",
            category="IT",
            likelihood_inherent=3,
            impact_inherent=3,
            status="open",
            review_date=today + timedelta(days=3),
        )
        result = check_review_deadlines()
        assert result["upcoming_reviews"] == 1
        assert result["risks"][0]["risk_id"] == "RISK-RV-001"
        assert result["risks"][0]["days_until"] == 3

    def test_ignores_closed_risks(self) -> None:
        """closed リスクは対象外"""
        from apps.risks.models import Risk
        from apps.risks.tasks import check_review_deadlines

        today = datetime.now(tz=UTC).date()
        Risk.objects.create(
            risk_id="RISK-RV-002",
            title="クローズ済み",
            category="IT",
            likelihood_inherent=2,
            impact_inherent=2,
            status="closed",
            review_date=today + timedelta(days=3),
        )
        result = check_review_deadlines()
        assert result["upcoming_reviews"] == 0

    def test_ignores_far_future_review(self) -> None:
        """review_date が7日超先のリスクは対象外"""
        from apps.risks.models import Risk
        from apps.risks.tasks import check_review_deadlines

        today = datetime.now(tz=UTC).date()
        Risk.objects.create(
            risk_id="RISK-RV-003",
            title="遠い未来",
            category="IT",
            likelihood_inherent=2,
            impact_inherent=2,
            status="open",
            review_date=today + timedelta(days=30),
        )
        result = check_review_deadlines()
        assert result["upcoming_reviews"] == 0

    def test_review_today_is_included(self) -> None:
        """review_date が今日のリスクは対象"""
        from apps.risks.models import Risk
        from apps.risks.tasks import check_review_deadlines

        today = datetime.now(tz=UTC).date()
        Risk.objects.create(
            risk_id="RISK-RV-004",
            title="今日レビュー",
            category="IT",
            likelihood_inherent=2,
            impact_inherent=2,
            status="open",
            review_date=today,
        )
        result = check_review_deadlines()
        assert result["upcoming_reviews"] == 1
        assert result["risks"][0]["days_until"] == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestGenerateRiskSummary:
    """risks.generate_risk_summary タスク"""

    def test_returns_zero_when_no_risks(self) -> None:
        from apps.risks.tasks import generate_risk_summary

        result = generate_risk_summary()
        assert result["total"] == 0
        assert result["open"] == 0
        assert result["critical"] == 0

    def test_generates_summary(self) -> None:
        from apps.risks.models import Risk
        from apps.risks.tasks import generate_risk_summary

        Risk.objects.create(
            risk_id="RISK-GS-001",
            title="サマリテスト1",
            category="IT",
            likelihood_inherent=5,
            impact_inherent=5,
            status="open",
        )
        Risk.objects.create(
            risk_id="RISK-GS-002",
            title="サマリテスト2",
            category="Construction",
            likelihood_inherent=1,
            impact_inherent=1,
            status="closed",
        )
        Risk.objects.create(
            risk_id="RISK-GS-003",
            title="サマリテスト3",
            category="Legal",
            likelihood_inherent=3,
            impact_inherent=4,
            status="in_progress",
        )
        result = generate_risk_summary()
        assert result["total"] == 3
        assert result["open"] == 1
        assert result["in_progress"] == 1
        assert result["closed"] == 1
        assert result["critical"] == 1
        assert result["high"] == 1

    def test_returns_required_keys(self) -> None:
        from apps.risks.tasks import generate_risk_summary

        result = generate_risk_summary()
        for key in ("total", "open", "in_progress", "closed", "critical", "high"):
            assert key in result
