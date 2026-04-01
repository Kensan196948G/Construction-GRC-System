"""コンプライアンス準拠率チェックサービス"""

from __future__ import annotations

from typing import Any


class ComplianceChecker:
    """法令別・全体の準拠率を計算するサービス"""

    FRAMEWORK_LABELS = {
        "construction_law": "建設業法",
        "quality_law": "品確法",
        "safety_law": "労安法",
        "iso27001": "ISO27001",
        "nist_csf": "NIST CSF 2.0",
        "iso20000": "ISO20000",
        "subcontract_law": "下請法",
    }

    def calculate_compliance_rate(self, requirements: list[dict[str, Any]]) -> dict:
        """全体の準拠率を算出"""
        total = len(requirements)
        if total == 0:
            return {"total": 0, "compliant": 0, "rate": 0.0}

        compliant = sum(1 for r in requirements if r.get("compliance_status") == "compliant")
        partial = sum(1 for r in requirements if r.get("compliance_status") == "partial")

        return {
            "total": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": total - compliant - partial,
            "rate": round(compliant / total * 100, 1),
            "effective_rate": round((compliant + partial * 0.5) / total * 100, 1),
        }

    def calculate_by_framework(self, requirements: list[dict[str, Any]]) -> dict:
        """法令別の準拠率を算出"""
        by_framework: dict[str, list] = {}
        for req in requirements:
            fw = req.get("framework", "unknown")
            if fw not in by_framework:
                by_framework[fw] = []
            by_framework[fw].append(req)

        result = {}
        for fw, reqs in by_framework.items():
            rate_data = self.calculate_compliance_rate(reqs)
            rate_data["label"] = self.FRAMEWORK_LABELS.get(fw, fw)
            result[fw] = rate_data

        return result

    def get_non_compliant_items(self, requirements: list[dict[str, Any]]) -> list[dict]:
        """非準拠項目の一覧を取得"""
        return [r for r in requirements if r.get("compliance_status") in ("non_compliant", "unknown")]

    def get_upcoming_assessments(self, requirements: list[dict[str, Any]], days: int = 30) -> list[dict]:
        """今後N日以内に評価期限が到来する要件を取得"""
        from datetime import UTC, datetime, timedelta

        cutoff = datetime.now(tz=UTC).date() + timedelta(days=days)
        return [r for r in requirements if r.get("next_assessment") and r["next_assessment"] <= str(cutoff)]
