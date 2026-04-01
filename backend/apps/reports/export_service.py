"""データエクスポートサービス"""

from __future__ import annotations

import csv
import io
from typing import Any

from openpyxl import Workbook


class ExportService:
    """QuerySetをCSV/Excelバイトに変換するサービス。"""

    @staticmethod
    def queryset_to_csv(
        queryset: Any,
        fields: list[tuple[str, str]],
    ) -> bytes:
        """QuerySetをCSVバイトに変換。

        Args:
            queryset: Django QuerySet
            fields: [(field_name, header_label), ...]

        Returns:
            BOM付きUTF-8エンコードされたCSVバイト列
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([label for _, label in fields])
        for obj in queryset:
            row: list[str] = []
            for field_name, _ in fields:
                val = getattr(obj, field_name, "")
                if callable(val):
                    val = val()
                row.append(str(val) if val is not None else "")
            writer.writerow(row)
        return output.getvalue().encode("utf-8-sig")  # BOM付きUTF-8

    @staticmethod
    def queryset_to_excel(
        queryset: Any,
        fields: list[tuple[str, str]],
        sheet_name: str = "Data",
    ) -> bytes:
        """QuerySetをExcelバイトに変換。

        Args:
            queryset: Django QuerySet
            fields: [(field_name, header_label), ...]
            sheet_name: シート名

        Returns:
            Excelバイナリ
        """
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        ws.append([label for _, label in fields])
        for obj in queryset:
            row: list[str] = []
            for field_name, _ in fields:
                val = getattr(obj, field_name, "")
                if callable(val):
                    val = val()
                row.append(str(val) if val is not None else "")
            ws.append(row)
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()


# ── フィールド定義 ──────────────────────────────────────────

RISK_FIELDS: list[tuple[str, str]] = [
    ("risk_id", "リスクID"),
    ("title", "タイトル"),
    ("category", "カテゴリ"),
    ("likelihood_inherent", "発生可能性"),
    ("impact_inherent", "影響度"),
    ("risk_level", "リスクレベル"),
    ("status", "ステータス"),
    ("treatment_strategy", "対応戦略"),
    ("risk_owner", "リスクオーナー"),
]

CONTROL_FIELDS: list[tuple[str, str]] = [
    ("control_id", "管理策ID"),
    ("title", "タイトル"),
    ("domain", "ドメイン"),
    ("implementation_status", "実施状況"),
    ("is_applicable", "適用"),
    ("owner", "担当者"),
]

COMPLIANCE_FIELDS: list[tuple[str, str]] = [
    ("req_id", "要件ID"),
    ("framework", "フレームワーク"),
    ("title", "タイトル"),
    ("category", "カテゴリ"),
    ("compliance_status", "準拠状況"),
    ("is_mandatory", "必須"),
    ("frequency", "頻度"),
]

AUDIT_FIELDS: list[tuple[str, str]] = [
    ("audit_id", "監査ID"),
    ("title", "タイトル"),
    ("audit_type", "種別"),
    ("status", "ステータス"),
    ("target_department", "対象部門"),
    ("planned_start", "開始予定"),
    ("planned_end", "終了予定"),
]

AUDIT_FINDING_FIELDS: list[tuple[str, str]] = [
    ("finding_id", "所見ID"),
    ("audit", "監査"),
    ("finding_type", "種別"),
    ("title", "タイトル"),
    ("cap_status", "CAP状況"),
    ("cap_owner", "CAP担当者"),
    ("cap_due_date", "CAP期限"),
]
