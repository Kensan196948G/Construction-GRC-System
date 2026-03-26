"""管理策準拠率計算サービス

ISO27001管理策の準拠率をドメイン別・全体・トレンドで算出する
サービスレイヤー。
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from apps.controls.models import ISO27001Control


class ComplianceRateService:
    """管理策準拠率の計算サービス"""

    @staticmethod
    def calculate_overall_rate(
        queryset: QuerySet[ISO27001Control] | None = None,
    ) -> dict[str, Any]:
        """全管理策の準拠率を算出する。

        「実施済み」の管理策数 / 適用対象の管理策数 で算出。

        Args:
            queryset: 対象管理策のクエリセット（Noneの場合は全件）

        Returns:
            {
                "total": int,
                "applicable": int,
                "implemented": int,
                "compliance_rate": float,  # 0.0 - 100.0
                "by_status": {status: count, ...},
            }
        """
        if queryset is None:
            queryset = ISO27001Control.objects.all()

        total: int = queryset.count()
        applicable_qs = queryset.filter(is_applicable=True)
        applicable: int = applicable_qs.count()

        status_counts: dict[str, int] = {}
        for entry in applicable_qs.values("implementation_status").annotate(
            count=Count("id")
        ):
            status_counts[entry["implementation_status"]] = entry["count"]

        implemented: int = status_counts.get("implemented", 0)
        compliance_rate: float = (
            round((implemented / applicable) * 100, 1) if applicable > 0 else 0.0
        )

        return {
            "total": total,
            "applicable": applicable,
            "implemented": implemented,
            "compliance_rate": compliance_rate,
            "by_status": status_counts,
        }

    @classmethod
    def calculate_by_domain(
        cls,
        queryset: QuerySet[ISO27001Control] | None = None,
    ) -> list[dict[str, Any]]:
        """ドメイン別の準拠率を算出する。

        Args:
            queryset: 対象管理策のクエリセット

        Returns:
            ドメインごとの準拠率リスト:
            [
                {
                    "domain": str,
                    "domain_display": str,
                    "total": int,
                    "applicable": int,
                    "implemented": int,
                    "compliance_rate": float,
                },
                ...
            ]
        """
        if queryset is None:
            queryset = ISO27001Control.objects.all()

        domain_labels: dict[str, str] = dict(ISO27001Control.Domain.choices)
        results: list[dict[str, Any]] = []

        for domain_key, domain_display in domain_labels.items():
            domain_qs = queryset.filter(domain=domain_key)
            total = domain_qs.count()
            if total == 0:
                continue

            applicable = domain_qs.filter(is_applicable=True).count()
            implemented = domain_qs.filter(
                is_applicable=True,
                implementation_status="implemented",
            ).count()
            compliance_rate = (
                round((implemented / applicable) * 100, 1)
                if applicable > 0
                else 0.0
            )

            results.append({
                "domain": domain_key,
                "domain_display": domain_display,
                "total": total,
                "applicable": applicable,
                "implemented": implemented,
                "compliance_rate": compliance_rate,
            })

        return results

    @classmethod
    def calculate_trend(
        cls,
        months: int = 6,
        queryset: QuerySet[ISO27001Control] | None = None,
    ) -> list[dict[str, Any]]:
        """過去N ヶ月の準拠率推移を算出する。

        管理策の updated_at をもとに、各月末時点での「実施済み」数の
        累積推移を概算で返す。

        Args:
            months: 遡る月数（デフォルト6）
            queryset: 対象管理策のクエリセット

        Returns:
            月別の準拠率リスト:
            [
                {"month": "2026-01", "implemented": int, "applicable": int, "compliance_rate": float},
                ...
            ]
        """
        if queryset is None:
            queryset = ISO27001Control.objects.all()

        now = timezone.now()
        applicable_count: int = queryset.filter(is_applicable=True).count()
        trend: list[dict[str, Any]] = []

        for i in range(months - 1, -1, -1):
            # 月の末日を概算（翌月の1日 - 1日）
            year = now.year
            month = now.month - i
            while month <= 0:
                month += 12
                year -= 1

            month_label = f"{year}-{month:02d}"

            # その月末までに「実施済み」になった管理策数
            # updated_at がその月末以前で implementation_status=implemented のものを数える
            if month == 12:
                next_year, next_month = year + 1, 1
            else:
                next_year, next_month = year, month + 1

            cutoff = timezone.datetime(next_year, next_month, 1, tzinfo=timezone.utc)

            implemented = queryset.filter(
                is_applicable=True,
                implementation_status="implemented",
                updated_at__lt=cutoff,
            ).count()

            compliance_rate = (
                round((implemented / applicable_count) * 100, 1)
                if applicable_count > 0
                else 0.0
            )

            trend.append({
                "month": month_label,
                "implemented": implemented,
                "applicable": applicable_count,
                "compliance_rate": compliance_rate,
            })

        return trend
