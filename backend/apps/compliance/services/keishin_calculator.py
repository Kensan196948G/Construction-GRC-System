"""経営事項審査（経審）P点シミュレーション計算サービス

建設業法第27条の23に基づく経営事項審査の総合評定値（P点）を計算する。
P = 0.25×X1 + 0.15×X2 + 0.20×Y + 0.25×Z + 0.15×W

X1: 完成工事高評点
X2: 自己資本額・平均利益額評点
Y:  経営状況評点
Z:  技術力評点
W:  その他社会性等評点
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KeishinInput:
    """経審計算入力データ"""

    # X1: 完成工事高（千円）
    completed_construction_amount: int
    # X2: 自己資本額（千円）、平均利益額（千円）
    equity_capital: int
    average_profit: int
    # Y: 経営状況分析（純支払利息比率、負債回転期間、売上高経常利益率等）
    y_score: int  # 経営状況分析機関からの評点（0-1595）
    # Z: 技術職員数、元請完工高
    technical_staff_score: int  # 技術職員数値（0-2366）
    prime_contract_score: int  # 元請完成工事高評点（0-2441）
    # W: 社会性等
    social_score: int  # 社会性等評点（0-1966）


@dataclass
class KeishinResult:
    """経審計算結果"""

    x1: int  # 完成工事高評点
    x2: int  # 自己資本額・利益額評点
    y: int  # 経営状況評点
    z: int  # 技術力評点
    w: int  # 社会性等評点
    p: int  # 総合評定値（P点）
    grade: str  # 等級（参考）


class KeishinCalculator:
    """経営事項審査 P点計算"""

    # 完成工事高区分テーブル（簡略版）
    X1_TABLE = [
        (100_000_000, 2309),  # 1000億以上
        (50_000_000, 2109),
        (30_000_000, 1959),
        (20_000_000, 1841),
        (12_000_000, 1709),
        (8_000_000, 1609),
        (5_000_000, 1499),
        (2_500_000, 1359),
        (1_200_000, 1209),
        (800_000, 1129),
        (500_000, 1039),
        (250_000, 919),
        (120_000, 799),
        (80_000, 739),
        (50_000, 669),
        (25_000, 579),
        (10_000, 469),
        (0, 397),
    ]

    def calculate_x1(self, amount: int) -> int:
        """完成工事高評点の算出"""
        for threshold, score in self.X1_TABLE:
            if amount >= threshold:
                return score
        return 397

    def calculate_x2(self, equity: int, profit: int) -> int:
        """自己資本額・平均利益額評点の算出（簡略版）"""
        equity_score = min(max(int(equity / 10_000) * 2 + 454, 454), 2280)
        profit_score = min(max(int(profit / 1_000) + 500, 0), 2280)
        return int(equity_score * 0.5 + profit_score * 0.5)

    def calculate_z(self, tech_score: int, prime_score: int) -> int:
        """技術力評点の算出"""
        return int(tech_score * 0.8 + prime_score * 0.2)

    def calculate(self, input_data: KeishinInput) -> KeishinResult:
        """総合評定値（P点）の算出"""
        x1 = self.calculate_x1(input_data.completed_construction_amount)
        x2 = self.calculate_x2(input_data.equity_capital, input_data.average_profit)
        y = min(max(input_data.y_score, 0), 1595)
        z = self.calculate_z(input_data.technical_staff_score, input_data.prime_contract_score)
        w = min(max(input_data.social_score, 0), 1966)

        p = int(0.25 * x1 + 0.15 * x2 + 0.20 * y + 0.25 * z + 0.15 * w)

        grade = self._determine_grade(p)

        return KeishinResult(x1=x1, x2=x2, y=y, z=z, w=w, p=p, grade=grade)

    def _determine_grade(self, p: int) -> str:
        """P点に基づく等級判定（参考値）"""
        if p >= 1200:
            return "A"
        elif p >= 900:
            return "B"
        elif p >= 700:
            return "C"
        elif p >= 500:
            return "D"
        return "E"
