"""経営事項審査（経審）P点計算テスト"""
from apps.compliance.services.keishin_calculator import (
    KeishinCalculator,
    KeishinInput,
)


class TestKeishinCalculator:
    """経審計算のテスト"""

    def setup_method(self):
        self.calc = KeishinCalculator()

    def test_x1_large_company(self):
        """完工高1000億以上 → 最高点2309"""
        assert self.calc.calculate_x1(100_000_000) == 2309

    def test_x1_medium_company(self):
        """完工高50億 → 1499"""
        assert self.calc.calculate_x1(5_000_000) == 1499

    def test_x1_small_company(self):
        """完工高1億 → 799"""
        assert self.calc.calculate_x1(120_000) == 799

    def test_x1_minimum(self):
        """完工高0 → 最低点397"""
        assert self.calc.calculate_x1(0) == 397

    def test_p_calculation(self):
        """P点の総合計算"""
        input_data = KeishinInput(
            completed_construction_amount=5_000_000,  # 50億
            equity_capital=500_000,  # 5億
            average_profit=50_000,  # 5000万
            y_score=800,
            technical_staff_score=1000,
            prime_contract_score=800,
            social_score=900,
        )
        result = self.calc.calculate(input_data)
        assert result.p > 0
        assert result.x1 == 1499
        assert result.grade in ("A", "B", "C", "D", "E")

    def test_grade_a(self):
        """P点1200以上 → A等級"""
        assert self.calc._determine_grade(1200) == "A"
        assert self.calc._determine_grade(1500) == "A"

    def test_grade_b(self):
        """P点900-1199 → B等級"""
        assert self.calc._determine_grade(900) == "B"
        assert self.calc._determine_grade(1199) == "B"

    def test_grade_c(self):
        """P点700-899 → C等級"""
        assert self.calc._determine_grade(700) == "C"

    def test_grade_d(self):
        """P点500-699 → D等級"""
        assert self.calc._determine_grade(500) == "D"

    def test_grade_e(self):
        """P点499以下 → E等級"""
        assert self.calc._determine_grade(499) == "E"


class TestComplianceChecker:
    """コンプライアンスチェッカーのテスト"""

    def test_full_compliance(self):
        from apps.compliance.services.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()
        reqs = [
            {"compliance_status": "compliant"},
            {"compliance_status": "compliant"},
        ]
        result = checker.calculate_compliance_rate(reqs)
        assert result["rate"] == 100.0

    def test_zero_compliance(self):
        from apps.compliance.services.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()
        reqs = [
            {"compliance_status": "non_compliant"},
            {"compliance_status": "unknown"},
        ]
        result = checker.calculate_compliance_rate(reqs)
        assert result["rate"] == 0.0

    def test_empty_requirements(self):
        from apps.compliance.services.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()
        result = checker.calculate_compliance_rate([])
        assert result["total"] == 0
        assert result["rate"] == 0.0

    def test_by_framework(self):
        from apps.compliance.services.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()
        reqs = [
            {"framework": "construction_law", "compliance_status": "compliant"},
            {"framework": "construction_law", "compliance_status": "non_compliant"},
            {"framework": "safety_law", "compliance_status": "compliant"},
        ]
        result = checker.calculate_by_framework(reqs)
        assert "construction_law" in result
        assert result["construction_law"]["rate"] == 50.0
        assert result["safety_law"]["rate"] == 100.0
