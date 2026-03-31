"""リスクヒートマップサービス

リスク評価データからヒートマップ生成、リスクレベル判定、
サマリー統計を提供するサービスレイヤー。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Count, QuerySet

from apps.risks.models import Risk


@dataclass(frozen=True)
class RiskLevelDefinition:
    """リスクレベル定義"""

    name: str
    min_score: int
    max_score: int
    color: str


# リスクレベル定義（スコア昇順）
RISK_LEVELS: list[RiskLevelDefinition] = [
    RiskLevelDefinition(name="LOW", min_score=1, max_score=4, color="#22c55e"),
    RiskLevelDefinition(name="MEDIUM", min_score=5, max_score=9, color="#eab308"),
    RiskLevelDefinition(name="HIGH", min_score=10, max_score=14, color="#f97316"),
    RiskLevelDefinition(name="CRITICAL", min_score=15, max_score=25, color="#dc2626"),
]

RISK_LEVEL_MAP: dict[str, RiskLevelDefinition] = {rl.name: rl for rl in RISK_LEVELS}


class RiskHeatmapService:
    """リスクヒートマップの生成・分析サービス"""

    @staticmethod
    def calculate_risk_level(likelihood: int, impact: int) -> str:
        """発生可能性と影響度からリスクレベルを算出する。

        Args:
            likelihood: 発生可能性 (1-5)
            impact: 影響度 (1-5)

        Returns:
            リスクレベル文字列 ("LOW" | "MEDIUM" | "HIGH" | "CRITICAL")

        Raises:
            ValueError: likelihood または impact が 1-5 の範囲外の場合
        """
        if not (1 <= likelihood <= 5):
            raise ValueError(f"likelihood must be 1-5, got {likelihood}")
        if not (1 <= impact <= 5):
            raise ValueError(f"impact must be 1-5, got {impact}")

        score: int = likelihood * impact

        for level in reversed(RISK_LEVELS):
            if score >= level.min_score:
                return level.name

        return "LOW"

    @staticmethod
    def get_risk_color(level: str) -> str:
        """リスクレベルに対応する色コードを返す。

        Args:
            level: リスクレベル名

        Returns:
            HEX色コード
        """
        definition = RISK_LEVEL_MAP.get(level)
        if definition is None:
            return "#9ca3af"  # gray fallback
        return definition.color

    @classmethod
    def generate_heatmap_data(cls, queryset: QuerySet[Risk] | None = None) -> dict[str, Any]:
        """5x5ヒートマップデータを生成する。

        Args:
            queryset: 対象リスクのクエリセット（Noneの場合は全件）

        Returns:
            ヒートマップ描画に必要なデータ構造:
            {
                "matrix": [[{count, level, color}, ...], ...],  # 5x5
                "risks": [{risk_id, title, likelihood, impact, level, color}, ...],
                "axis_labels": {"likelihood": [...], "impact": [...]},
            }
        """
        if queryset is None:
            queryset = Risk.objects.all()

        # 5x5マトリクスの初期化（likelihood=行, impact=列）
        matrix: list[list[dict[str, Any]]] = []
        for likelihood in range(1, 6):
            row: list[dict[str, Any]] = []
            for impact in range(1, 6):
                level = cls.calculate_risk_level(likelihood, impact)
                row.append(
                    {
                        "likelihood": likelihood,
                        "impact": impact,
                        "count": 0,
                        "level": level,
                        "color": cls.get_risk_color(level),
                    }
                )
            matrix.append(row)

        # リスクをマトリクスに配置
        risks_data: list[dict[str, Any]] = []
        for risk in queryset.only("risk_id", "title", "likelihood_inherent", "impact_inherent"):
            li = risk.likelihood_inherent
            im = risk.impact_inherent
            level = cls.calculate_risk_level(li, im)
            matrix[li - 1][im - 1]["count"] += 1
            risks_data.append(
                {
                    "risk_id": risk.risk_id,
                    "title": risk.title,
                    "likelihood": li,
                    "impact": im,
                    "score": li * im,
                    "level": level,
                    "color": cls.get_risk_color(level),
                }
            )

        return {
            "matrix": matrix,
            "risks": risks_data,
            "axis_labels": {
                "likelihood": ["1: 極めて低い", "2: 低い", "3: 中程度", "4: 高い", "5: 極めて高い"],
                "impact": ["1: 軽微", "2: 小", "3: 中", "4: 大", "5: 甚大"],
            },
        }

    @classmethod
    def get_risk_summary(cls, queryset: QuerySet[Risk] | None = None) -> dict[str, Any]:
        """リスクサマリー統計を返す。

        Args:
            queryset: 対象リスクのクエリセット

        Returns:
            {
                "total": int,
                "by_level": {"LOW": n, "MEDIUM": n, "HIGH": n, "CRITICAL": n},
                "by_status": {"open": n, ...},
                "by_category": {"IT": n, ...},
                "level_colors": {"LOW": "#22c55e", ...},
            }
        """
        if queryset is None:
            queryset = Risk.objects.all()

        # ステータス別集計
        status_counts: dict[str, int] = {}
        for entry in queryset.values("status").annotate(count=Count("id")):
            status_counts[entry["status"]] = entry["count"]

        # カテゴリ別集計
        category_counts: dict[str, int] = {}
        for entry in queryset.values("category").annotate(count=Count("id")):
            category_counts[entry["category"]] = entry["count"]

        # レベル別集計（Pythonで計算）
        level_counts: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for risk in queryset.only("likelihood_inherent", "impact_inherent"):
            level = cls.calculate_risk_level(risk.likelihood_inherent, risk.impact_inherent)
            level_counts[level] += 1

        level_colors: dict[str, str] = {rl.name: rl.color for rl in RISK_LEVELS}

        return {
            "total": queryset.count(),
            "by_level": level_counts,
            "by_status": status_counts,
            "by_category": category_counts,
            "level_colors": level_colors,
        }
