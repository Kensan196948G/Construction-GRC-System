"""サービス層のユニットテスト

DB不要のロジックテストを中心に、サービスクラスの振る舞いを検証する。
"""

from __future__ import annotations

import pytest

from apps.risks.services import RISK_LEVEL_MAP, RiskHeatmapService


class TestRiskLevelCalculation:
    """RiskHeatmapService.calculate_risk_level のテスト（全4レベル）"""

    def test_risk_level_low_min(self) -> None:
        """スコア1（1x1）はLOW"""
        assert RiskHeatmapService.calculate_risk_level(1, 1) == "LOW"

    def test_risk_level_low_max(self) -> None:
        """スコア4（1x4, 2x2, 4x1）はLOW"""
        assert RiskHeatmapService.calculate_risk_level(1, 4) == "LOW"
        assert RiskHeatmapService.calculate_risk_level(2, 2) == "LOW"
        assert RiskHeatmapService.calculate_risk_level(4, 1) == "LOW"

    def test_risk_level_medium_min(self) -> None:
        """スコア5（1x5, 5x1）はMEDIUM"""
        assert RiskHeatmapService.calculate_risk_level(1, 5) == "MEDIUM"
        assert RiskHeatmapService.calculate_risk_level(5, 1) == "MEDIUM"

    def test_risk_level_medium_max(self) -> None:
        """スコア9（3x3）はMEDIUM"""
        assert RiskHeatmapService.calculate_risk_level(3, 3) == "MEDIUM"

    def test_risk_level_high_min(self) -> None:
        """スコア10（2x5, 5x2）はHIGH"""
        assert RiskHeatmapService.calculate_risk_level(2, 5) == "HIGH"
        assert RiskHeatmapService.calculate_risk_level(5, 2) == "HIGH"

    def test_risk_level_high_max(self) -> None:
        """スコア14はHIGH（ただし整数の組合せでは不可なので近似値で確認）"""
        # 3x4=12, 4x3=12 はHIGH
        assert RiskHeatmapService.calculate_risk_level(3, 4) == "HIGH"
        assert RiskHeatmapService.calculate_risk_level(4, 3) == "HIGH"

    def test_risk_level_critical_min(self) -> None:
        """スコア15（3x5, 5x3）はCRITICAL"""
        assert RiskHeatmapService.calculate_risk_level(3, 5) == "CRITICAL"
        assert RiskHeatmapService.calculate_risk_level(5, 3) == "CRITICAL"

    def test_risk_level_critical_max(self) -> None:
        """スコア25（5x5）はCRITICAL"""
        assert RiskHeatmapService.calculate_risk_level(5, 5) == "CRITICAL"

    def test_risk_level_invalid_likelihood_raises(self) -> None:
        """範囲外のlikelihoodでValueError"""
        with pytest.raises(ValueError, match="likelihood"):
            RiskHeatmapService.calculate_risk_level(0, 3)
        with pytest.raises(ValueError, match="likelihood"):
            RiskHeatmapService.calculate_risk_level(6, 3)

    def test_risk_level_invalid_impact_raises(self) -> None:
        """範囲外のimpactでValueError"""
        with pytest.raises(ValueError, match="impact"):
            RiskHeatmapService.calculate_risk_level(3, 0)
        with pytest.raises(ValueError, match="impact"):
            RiskHeatmapService.calculate_risk_level(3, 6)

    def test_all_combinations_have_valid_level(self) -> None:
        """全25通りの組合せが有効なレベルを返す"""
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        for li in range(1, 6):
            for im in range(1, 6):
                level = RiskHeatmapService.calculate_risk_level(li, im)
                assert level in valid_levels, f"Invalid level for ({li}, {im}): {level}"


class TestRiskColors:
    """リスクレベルの色コードテスト"""

    def test_low_color(self) -> None:
        assert RiskHeatmapService.get_risk_color("LOW") == "#22c55e"

    def test_medium_color(self) -> None:
        assert RiskHeatmapService.get_risk_color("MEDIUM") == "#eab308"

    def test_high_color(self) -> None:
        assert RiskHeatmapService.get_risk_color("HIGH") == "#f97316"

    def test_critical_color(self) -> None:
        assert RiskHeatmapService.get_risk_color("CRITICAL") == "#dc2626"

    def test_unknown_level_returns_fallback(self) -> None:
        assert RiskHeatmapService.get_risk_color("UNKNOWN") == "#9ca3af"


class TestHeatmapDataStructure:
    """RiskHeatmapService.generate_heatmap_data の構造テスト"""

    def test_heatmap_has_required_keys(self) -> None:
        """ヒートマップデータに必須キーが含まれる"""
        # generate_heatmap_dataはDBアクセスするため、空クエリセットで呼ぶ
        from unittest.mock import MagicMock

        empty_qs = MagicMock()
        empty_qs.only.return_value = []

        data = RiskHeatmapService.generate_heatmap_data(queryset=empty_qs)
        assert "matrix" in data
        assert "risks" in data
        assert "axis_labels" in data

    def test_matrix_is_5x5(self) -> None:
        """マトリクスが5x5である"""
        from unittest.mock import MagicMock

        empty_qs = MagicMock()
        empty_qs.only.return_value = []

        data = RiskHeatmapService.generate_heatmap_data(queryset=empty_qs)
        matrix = data["matrix"]
        assert len(matrix) == 5
        for row in matrix:
            assert len(row) == 5

    def test_matrix_cells_have_required_fields(self) -> None:
        """各セルに必須フィールドがある"""
        from unittest.mock import MagicMock

        empty_qs = MagicMock()
        empty_qs.only.return_value = []

        data = RiskHeatmapService.generate_heatmap_data(queryset=empty_qs)
        cell = data["matrix"][0][0]
        assert "likelihood" in cell
        assert "impact" in cell
        assert "count" in cell
        assert "level" in cell
        assert "color" in cell

    def test_axis_labels_structure(self) -> None:
        """軸ラベルが正しい構造を持つ"""
        from unittest.mock import MagicMock

        empty_qs = MagicMock()
        empty_qs.only.return_value = []

        data = RiskHeatmapService.generate_heatmap_data(queryset=empty_qs)
        labels = data["axis_labels"]
        assert "likelihood" in labels
        assert "impact" in labels
        assert len(labels["likelihood"]) == 5
        assert len(labels["impact"]) == 5

    def test_empty_queryset_returns_zero_counts(self) -> None:
        """空のクエリセットでは全セルのcountが0"""
        from unittest.mock import MagicMock

        empty_qs = MagicMock()
        empty_qs.only.return_value = []

        data = RiskHeatmapService.generate_heatmap_data(queryset=empty_qs)
        for row in data["matrix"]:
            for cell in row:
                assert cell["count"] == 0

    def test_matrix_corner_levels(self) -> None:
        """マトリクス四隅のレベルが正しい"""
        from unittest.mock import MagicMock

        empty_qs = MagicMock()
        empty_qs.only.return_value = []

        data = RiskHeatmapService.generate_heatmap_data(queryset=empty_qs)
        matrix = data["matrix"]
        # (1,1)=LOW, (1,5)=MEDIUM, (5,1)=MEDIUM, (5,5)=CRITICAL
        assert matrix[0][0]["level"] == "LOW"
        assert matrix[0][4]["level"] == "MEDIUM"
        assert matrix[4][0]["level"] == "MEDIUM"
        assert matrix[4][4]["level"] == "CRITICAL"


class TestRiskLevelDefinitions:
    """リスクレベル定義データのテスト"""

    def test_all_four_levels_defined(self) -> None:
        assert "LOW" in RISK_LEVEL_MAP
        assert "MEDIUM" in RISK_LEVEL_MAP
        assert "HIGH" in RISK_LEVEL_MAP
        assert "CRITICAL" in RISK_LEVEL_MAP

    def test_score_ranges_are_contiguous(self) -> None:
        """スコア範囲が連続的（ギャップなし）"""
        from apps.risks.services import RISK_LEVELS

        for i in range(len(RISK_LEVELS) - 1):
            assert RISK_LEVELS[i].max_score + 1 == RISK_LEVELS[i + 1].min_score

    def test_score_range_covers_1_to_25(self) -> None:
        """スコア範囲が1-25をカバーする"""
        from apps.risks.services import RISK_LEVELS

        assert RISK_LEVELS[0].min_score == 1
        assert RISK_LEVELS[-1].max_score == 25
