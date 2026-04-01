"""多言語対応ユーティリティテスト

grc/i18n.py の translate / get_locale を検証。
"""

from __future__ import annotations

from unittest.mock import MagicMock

from django.test import TestCase

from grc.i18n import TRANSLATIONS, get_locale, translate


class TestTranslate(TestCase):
    """translate 関数のテスト"""

    def test_japanese_default(self) -> None:
        result = translate("risk_created")
        assert result == "リスクが作成されました"

    def test_japanese_explicit(self) -> None:
        result = translate("risk_created", "ja")
        assert result == "リスクが作成されました"

    def test_english(self) -> None:
        result = translate("risk_created", "en")
        assert result == "Risk created successfully"

    def test_unknown_key_returns_key(self) -> None:
        result = translate("nonexistent_key", "ja")
        assert result == "nonexistent_key"

    def test_unknown_locale_falls_back_to_japanese(self) -> None:
        result = translate("risk_created", "fr")
        assert result == "リスクが作成されました"

    def test_all_japanese_keys(self) -> None:
        """全ての日本語翻訳キーが取得可能"""
        for key in TRANSLATIONS["ja"]:
            result = translate(key, "ja")
            assert result != key, f"Key {key} returned itself"

    def test_all_english_keys(self) -> None:
        """全ての英語翻訳キーが取得可能"""
        for key in TRANSLATIONS["en"]:
            result = translate(key, "en")
            assert result != key, f"Key {key} returned itself"

    def test_japanese_and_english_have_same_keys(self) -> None:
        """日英で同じキーセットが定義されている"""
        assert set(TRANSLATIONS["ja"].keys()) == set(TRANSLATIONS["en"].keys())

    def test_unauthorized_message(self) -> None:
        assert translate("unauthorized", "ja") == "認証が必要です"
        assert translate("unauthorized", "en") == "Authentication required"

    def test_forbidden_message(self) -> None:
        assert translate("forbidden", "ja") == "権限がありません"
        assert translate("forbidden", "en") == "Permission denied"

    def test_not_found_message(self) -> None:
        assert translate("not_found", "ja") == "リソースが見つかりません"
        assert translate("not_found", "en") == "Resource not found"


class TestGetLocale(TestCase):
    """get_locale 関数のテスト"""

    def _make_request(self, accept_language: str | None = None) -> MagicMock:
        request = MagicMock()
        if accept_language is not None:
            request.META = {"HTTP_ACCEPT_LANGUAGE": accept_language}
        else:
            request.META = {}
        return request

    def test_default_is_japanese(self) -> None:
        """Accept-Languageヘッダなしの場合はja"""
        request = self._make_request()
        assert get_locale(request) == "ja"

    def test_japanese_header(self) -> None:
        request = self._make_request("ja")
        assert get_locale(request) == "ja"

    def test_english_header(self) -> None:
        request = self._make_request("en-US,en;q=0.9")
        assert get_locale(request) == "en"

    def test_english_simple(self) -> None:
        request = self._make_request("en")
        assert get_locale(request) == "en"

    def test_mixed_prefers_english_when_present(self) -> None:
        """enが含まれていればenを返す"""
        request = self._make_request("ja,en;q=0.8")
        assert get_locale(request) == "en"

    def test_french_falls_back_to_japanese(self) -> None:
        """enが含まれない場合はjaにフォールバック"""
        request = self._make_request("fr-FR,fr;q=0.9")
        assert get_locale(request) == "ja"
