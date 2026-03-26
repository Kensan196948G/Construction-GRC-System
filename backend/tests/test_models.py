"""モデル定義のバリデーションテスト（DB不要）"""


class TestRiskModelDefinition:
    """Riskモデルの定義テスト"""

    def test_risk_category_choices(self):
        from apps.risks.models import Risk
        categories = [c[0] for c in Risk.Category.choices]
        assert "IT" in categories
        assert "Construction" in categories
        assert "Legal" in categories

    def test_treatment_strategy_choices(self):
        from apps.risks.models import Risk
        strategies = [s[0] for s in Risk.TreatmentStrategy.choices]
        assert set(strategies) == {"accept", "mitigate", "transfer", "avoid"}

    def test_status_choices(self):
        from apps.risks.models import Risk
        statuses = [s[0] for s in Risk.Status.choices]
        assert "open" in statuses
        assert "closed" in statuses

    def test_risk_score_calculation(self):
        from apps.risks.models import Risk
        risk = Risk(likelihood_inherent=5, impact_inherent=5)
        assert risk.risk_score_inherent == 25

    def test_risk_level_boundaries(self):
        from apps.risks.models import Risk
        # LOW: 1-4
        assert Risk(likelihood_inherent=1, impact_inherent=1).risk_level == "LOW"
        assert Risk(likelihood_inherent=2, impact_inherent=2).risk_level == "LOW"
        # MEDIUM: 5-9
        assert Risk(likelihood_inherent=3, impact_inherent=2).risk_level == "MEDIUM"
        # HIGH: 10-14
        assert Risk(likelihood_inherent=3, impact_inherent=4).risk_level == "HIGH"
        # CRITICAL: 15-25
        assert Risk(likelihood_inherent=5, impact_inherent=5).risk_level == "CRITICAL"


class TestISO27001ControlModelDefinition:
    """ISO27001Controlモデルの定義テスト"""

    def test_domain_choices(self):
        from apps.controls.models import ISO27001Control
        domains = [d[0] for d in ISO27001Control.Domain.choices]
        assert set(domains) == {"organizational", "people", "physical", "technological"}

    def test_implementation_status_choices(self):
        from apps.controls.models import ISO27001Control
        statuses = [s[0] for s in ISO27001Control.ImplementationStatus.choices]
        assert "not_started" in statuses
        assert "implemented" in statuses


class TestComplianceRequirementModelDefinition:
    """ComplianceRequirementモデルの定義テスト"""

    def test_framework_choices(self):
        from apps.compliance.models import ComplianceRequirement
        frameworks = [f[0] for f in ComplianceRequirement.Framework.choices]
        assert "construction_law" in frameworks
        assert "quality_law" in frameworks
        assert "safety_law" in frameworks
        assert "iso27001" in frameworks

    def test_compliance_status_choices(self):
        from apps.compliance.models import ComplianceRequirement
        statuses = [s[0] for s in ComplianceRequirement.ComplianceStatus.choices]
        assert set(statuses) == {"compliant", "non_compliant", "partial", "unknown"}


class TestAuditModelDefinition:
    """Auditモデルの定義テスト"""

    def test_finding_type_choices(self):
        from apps.audits.models import AuditFinding
        types = [t[0] for t in AuditFinding.FindingType.choices]
        assert "major_nc" in types
        assert "minor_nc" in types
        assert "observation" in types
        assert "positive" in types
