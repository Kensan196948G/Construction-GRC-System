"""リスク管理モジュール テスト"""


class TestRiskModel:
    """Risk モデルのテスト"""

    def test_risk_score_inherent_calculation(self):
        """固有リスクスコア計算: 発生可能性 × 影響度"""
        from apps.risks.models import Risk

        risk = Risk(likelihood_inherent=4, impact_inherent=5)
        assert risk.risk_score_inherent == 20

    def test_risk_level_critical(self):
        """リスクレベル: スコア15以上はCRITICAL"""
        from apps.risks.models import Risk

        risk = Risk(likelihood_inherent=5, impact_inherent=4)
        assert risk.risk_level == "CRITICAL"

    def test_risk_level_high(self):
        """リスクレベル: スコア10-14はHIGH"""
        from apps.risks.models import Risk

        risk = Risk(likelihood_inherent=3, impact_inherent=4)
        assert risk.risk_level == "HIGH"

    def test_risk_level_medium(self):
        """リスクレベル: スコア5-9はMEDIUM"""
        from apps.risks.models import Risk

        risk = Risk(likelihood_inherent=2, impact_inherent=3)
        assert risk.risk_level == "MEDIUM"

    def test_risk_level_low(self):
        """リスクレベル: スコア1-4はLOW"""
        from apps.risks.models import Risk

        risk = Risk(likelihood_inherent=1, impact_inherent=2)
        assert risk.risk_level == "LOW"

    def test_residual_risk_score_none_when_not_set(self):
        """残存リスクスコア: 未設定時はNone"""
        from apps.risks.models import Risk

        risk = Risk(likelihood_inherent=3, impact_inherent=3)
        assert risk.risk_score_residual is None

    def test_residual_risk_score_calculated(self):
        """残存リスクスコア: 設定時は計算される"""
        from apps.risks.models import Risk

        risk = Risk(
            likelihood_inherent=4,
            impact_inherent=4,
            likelihood_residual=2,
            impact_residual=2,
        )
        assert risk.risk_score_residual == 4
