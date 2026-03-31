"""監査統計サービス

監査所見（Findings）と是正処置（CAP）の統計情報を
集約・分析するサービスレイヤー。
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, QuerySet
from django.utils import timezone

from apps.audits.models import Audit, AuditFinding


class AuditStatisticsService:
    """監査関連の統計情報を提供するサービス"""

    @staticmethod
    def get_findings_summary(
        audit: Audit | None = None,
        queryset: QuerySet[AuditFinding] | None = None,
    ) -> dict[str, Any]:
        """監査所見のサマリーを返す。

        Args:
            audit: 特定の監査に絞る場合に指定
            queryset: カスタムクエリセット（auditより優先）

        Returns:
            {
                "total": int,
                "by_type": {
                    "major_nc": int,
                    "minor_nc": int,
                    "observation": int,
                    "positive": int,
                },
                "nonconformities": int,
                "observations": int,
                "positive_findings": int,
            }
        """
        if queryset is None:
            queryset = AuditFinding.objects.all()
            if audit is not None:
                queryset = queryset.filter(audit=audit)

        type_counts: dict[str, int] = {
            "major_nc": 0,
            "minor_nc": 0,
            "observation": 0,
            "positive": 0,
        }
        for entry in queryset.values("finding_type").annotate(count=Count("id")):
            type_counts[entry["finding_type"]] = entry["count"]

        total: int = sum(type_counts.values())
        nonconformities: int = type_counts["major_nc"] + type_counts["minor_nc"]

        return {
            "total": total,
            "by_type": type_counts,
            "nonconformities": nonconformities,
            "observations": type_counts["observation"],
            "positive_findings": type_counts["positive"],
        }

    @staticmethod
    def get_cap_status_summary(
        audit: Audit | None = None,
        queryset: QuerySet[AuditFinding] | None = None,
    ) -> dict[str, Any]:
        """是正処置（CAP）ステータスのサマリーを返す。

        Args:
            audit: 特定の監査に絞る場合に指定
            queryset: カスタムクエリセット

        Returns:
            {
                "total_caps": int,
                "by_status": {
                    "open": int,
                    "in_progress": int,
                    "verified": int,
                    "closed": int,
                },
                "completion_rate": float,  # 0.0 - 100.0
                "overdue": int,
            }
        """
        if queryset is None:
            queryset = AuditFinding.objects.all()
            if audit is not None:
                queryset = queryset.filter(audit=audit)

        # CAP必須のもののみ
        cap_qs = queryset.filter(cap_required=True)

        status_counts: dict[str, int] = {
            "open": 0,
            "in_progress": 0,
            "verified": 0,
            "closed": 0,
        }
        for entry in cap_qs.values("cap_status").annotate(count=Count("id")):
            status_counts[entry["cap_status"]] = entry["count"]

        total_caps: int = sum(status_counts.values())
        completed: int = status_counts["verified"] + status_counts["closed"]
        completion_rate: float = round((completed / total_caps) * 100, 1) if total_caps > 0 else 0.0

        # 期限超過のCAP数
        today = timezone.now().date()
        overdue: int = (
            cap_qs.filter(
                cap_due_date__lt=today,
            )
            .exclude(
                cap_status__in=["verified", "closed"],
            )
            .count()
        )

        return {
            "total_caps": total_caps,
            "by_status": status_counts,
            "completion_rate": completion_rate,
            "overdue": overdue,
        }
