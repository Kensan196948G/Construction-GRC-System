"""統合GRCダッシュボードAPI

経営層が1画面で全体像を把握するための統合APIエンドポイント。
リスク・コンプライアンス・管理策・監査の主要KPIを一括返却。
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audits.models import Audit, AuditFinding
from apps.compliance.models import ComplianceRequirement
from apps.controls.models import ISO27001Control
from apps.risks.models import Risk


class GRCDashboardView(APIView):
    """統合GRCダッシュボード

    GET /api/v1/dashboard/
    全KPIを一括で返す経営層向けエンドポイント。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Any) -> Response:
        return Response(
            {
                "risks": self._risk_summary(),
                "compliance": self._compliance_summary(),
                "controls": self._controls_summary(),
                "audits": self._audit_summary(),
            }
        )

    @staticmethod
    def _risk_summary() -> dict[str, Any]:
        qs = Risk.objects.all()
        total = qs.count()
        if total == 0:
            return {"total": 0, "by_level": {}, "by_status": {}, "by_category": {}}

        by_level: dict[str, int] = {}
        for risk in qs:
            level = risk.risk_level
            by_level[level] = by_level.get(level, 0) + 1

        return {
            "total": total,
            "by_level": by_level,
            "by_status": {
                "open": qs.filter(status="open").count(),
                "in_progress": qs.filter(status="in_progress").count(),
                "closed": qs.filter(status="closed").count(),
                "accepted": qs.filter(status="accepted").count(),
            },
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
