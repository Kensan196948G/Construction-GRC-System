"""多言語対応ユーティリティ

Accept-Language ヘッダーに基づく言語切替をサポート。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest

# API レスポンス用の翻訳辞書
TRANSLATIONS = {
    "ja": {
        "risk_created": "リスクが作成されました",
        "risk_updated": "リスクが更新されました",
        "compliance_updated": "準拠状況が更新されました",
        "audit_completed": "監査が完了しました",
        "unauthorized": "認証が必要です",
        "forbidden": "権限がありません",
        "not_found": "リソースが見つかりません",
    },
    "en": {
        "risk_created": "Risk created successfully",
        "risk_updated": "Risk updated successfully",
        "compliance_updated": "Compliance status updated",
        "audit_completed": "Audit completed",
        "unauthorized": "Authentication required",
        "forbidden": "Permission denied",
        "not_found": "Resource not found",
    },
}


def get_locale(request: HttpRequest) -> str:
    """リクエストから言語を取得する。"""
    accept = request.META.get("HTTP_ACCEPT_LANGUAGE", "ja")
    if "en" in accept.lower():
        return "en"
    return "ja"


def translate(key: str, locale: str = "ja") -> str:
    """翻訳キーから翻訳文字列を取得する。"""
    return TRANSLATIONS.get(locale, TRANSLATIONS["ja"]).get(key, key)
