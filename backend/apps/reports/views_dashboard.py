"""統合GRCダッシュボードAPI

経営層が1画面で全体像を把握するための統合APIエンドポイント。
リスク・コンプライアンス・管理策・監査の主要KPIを一括返却。
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audits.models import Audit, AuditFinding
from apps.compliance.models import ComplianceRequirement
from apps.controls.models import ISO27001Control
from apps.risks.models import Risk
from grc.cache import CACHE_TTL, cache_key, get_or_set


class GRCDashboardView(APIView):
    """統合GRCダッシュボード

    GET /api/v1/dashboard/
    全KPIを一括で返す経営層向けエンドポイント。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> Response:
        def _build():
            return {
                "risks": self._risk_summary(),
                "compliance": self._compliance_summary(),
                "controls": self._controls_summary(),
                "audits": self._audit_summary(),
            }

        data = get_or_set(cache_key("dashboard"), _build, CACHE_TTL["dashboard"])
        return Response(data)

    @staticmethod
    def _risk_summary() -> dict[str, Any]:
        qs = Risk.objects.all()
        total = qs.count()
        if total == 0:
            return {"total": 0, "by_level": {}, "by_status": {}, "by_category": {}}

        # DB側でrisk_score (likelihood * impact) を計算してレベル別集計
        scored = qs.annotate(
            risk_score=F("likelihood_inherent") * F("impact_inherent"),
        )
        by_level = {
            "CRITICAL": scored.filter(risk_score__gte=15).count(),
            "HIGH": scored.filter(risk_score__gte=10, risk_score__lt=15).count(),
            "MEDIUM": scored.filter(risk_score__gte=5, risk_score__lt=10).count(),
            "LOW": scored.filter(risk_score__lt=5).count(),
        }

        # ステータス別をDB一括集計
        by_status = dict(qs.values("status").annotate(count=Count("id")).values_list("status", "count"))

        return {
            "total": total,
            "by_level": by_level,
            "by_status": by_status,
            "by_category": dict(qs.values("category").annotate(count=Count("id")).values_list("category", "count")),
        }

    @staticmethod
    def _compliance_summary() -> dict[str, Any]:
        qs = ComplianceRequirement.objects.all()
        total = qs.count()
        compliant = qs.filter(compliance_status="compliant").count()
        return {
            "total": total,
            "compliant": compliant,
            "non_compliant": qs.filter(compliance_status="non_compliant").count(),
            "partial": qs.filter(compliance_status="partial").count(),
            "unknown": qs.filter(compliance_status="unknown").count(),
            "rate": round(compliant / total * 100, 1) if total > 0 else 0,
        }

    @staticmethod
    def _controls_summary() -> dict[str, Any]:
        qs = ISO27001Control.objects.filter(is_applicable=True)
        total = qs.count()
        implemented = qs.filter(implementation_status="implemented").count()
        return {
            "total_applicable": total,
            "implemented": implemented,
            "in_progress": qs.filter(implementation_status="in_progress").count(),
            "not_started": qs.filter(implementation_status="not_started").count(),
            "partially": qs.filter(implementation_status="partially_implemented").count(),
            "rate": round(implemented / total * 100, 1) if total > 0 else 0,
        }

    @staticmethod
    def _audit_summary() -> dict[str, Any]:
        audits = Audit.objects.all()
        findings = AuditFinding.objects.all()
        return {
            "total_audits": audits.count(),
            "completed": audits.filter(status="completed").count(),
            "in_progress": audits.filter(status="in_progress").count(),
            "planned": audits.filter(status="planned").count(),
            "total_findings": findings.count(),
            "open_findings": findings.exclude(cap_status="closed").count(),
            "by_type": {
                "major_nc": findings.filter(finding_type="major_nc").count(),
                "minor_nc": findings.filter(finding_type="minor_nc").count(),
                "observation": findings.filter(finding_type="observation").count(),
                "good_practice": findings.filter(finding_type="good_practice").count(),
            },
        }
