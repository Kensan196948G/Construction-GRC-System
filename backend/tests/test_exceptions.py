"""GRC例外クラス・例外ハンドラーテスト."""

from unittest.mock import MagicMock, patch

from rest_framework import status
from rest_framework.exceptions import NotFound

from grc.exception_handler import grc_exception_handler
from grc.exceptions import (
    ComplianceStateError,
    GRCBaseException,
    InsufficientPermissionError,
    ResourceNotFoundError,
    RiskAssessmentError,
)


class TestGRCBaseException:
    """GRCBaseException テスト."""

    def test_default_status_code(self):
        exc = GRCBaseException()
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_default_detail(self):
        exc = GRCBaseException()
        assert exc.detail == "内部エラーが発生しました。"

    def test_default_code(self):
        exc = GRCBaseException()
        assert exc.default_code == "grc_error"

    def test_custom_detail(self):
        exc = GRCBaseException(detail="カスタムエラー")
        assert exc.detail == "カスタムエラー"


class TestResourceNotFoundError:
    """ResourceNotFoundError テスト."""

    def test_status_code(self):
        exc = ResourceNotFoundError()
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_default_detail(self):
        exc = ResourceNotFoundError()
        assert exc.detail == "指定されたリソースが見つかりません。"

    def test_default_code(self):
        exc = ResourceNotFoundError()
        assert exc.default_code == "resource_not_found"

    def test_custom_detail(self):
        exc = ResourceNotFoundError(detail="リスクが見つかりません")
        assert exc.detail == "リスクが見つかりません"


class TestComplianceStateError:
    """ComplianceStateError テスト."""

    def test_status_code(self):
        exc = ComplianceStateError()
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_default_detail(self):
        exc = ComplianceStateError()
        assert exc.detail == "コンプライアンス状態の矛盾が検出されました。"

    def test_default_code(self):
        exc = ComplianceStateError()
        assert exc.default_code == "compliance_state_error"


class TestInsufficientPermissionError:
    """InsufficientPermissionError テスト."""

    def test_status_code(self):
        exc = InsufficientPermissionError()
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_default_detail(self):
        exc = InsufficientPermissionError()
        assert exc.detail == "この操作に必要な権限がありません。"

    def test_default_code(self):
        exc = InsufficientPermissionError()
        assert exc.default_code == "insufficient_permission"


class TestRiskAssessmentError:
    """RiskAssessmentError テスト."""

    def test_status_code(self):
        exc = RiskAssessmentError()
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_default_detail(self):
        exc = RiskAssessmentError()
        assert exc.detail == "リスク評価パラメータが不正です。"

    def test_default_code(self):
        exc = RiskAssessmentError()
        assert exc.default_code == "risk_assessment_error"


class TestGRCExceptionHandler:
    """grc_exception_handler テスト."""

    def _make_context(self):
        return {"view": MagicMock(), "request": MagicMock()}

    def test_handles_drf_exception(self):
        """DRF例外が正しくハンドリングされることを確認."""
        exc = NotFound("見つかりません")
        context = self._make_context()
        response = grc_exception_handler(exc, context)
        assert response is not None
        assert response.status_code == 404
        assert response.data["status_code"] == 404

    def test_handles_grc_exception(self):
        """GRC例外が正しくハンドリングされることを確認."""
        exc = ResourceNotFoundError()
        context = self._make_context()
        response = grc_exception_handler(exc, context)
        assert response is not None
        assert response.status_code == 404
        assert response.data["status_code"] == 404
        assert response.data["error_code"] == "resource_not_found"

    def test_handles_unhandled_exception(self):
        """未処理例外が500レスポンスを返すことを確認."""
        exc = ValueError("unexpected error")
        context = self._make_context()
        with patch("grc.exception_handler.logger"):
            response = grc_exception_handler(exc, context)
        assert response is not None
        assert response.status_code == 500
        assert response.data["error_code"] == "internal_error"
        assert response.data["status_code"] == 500

    def test_error_code_in_response(self):
        """error_codeフィールドがレスポンスに含まれることを確認."""
        exc = ComplianceStateError()
        context = self._make_context()
        response = grc_exception_handler(exc, context)
        assert "error_code" in response.data
        assert response.data["error_code"] == "compliance_state_error"

    def test_status_code_in_response(self):
        """status_codeフィールドがレスポンスに含まれることを確認."""
        exc = InsufficientPermissionError()
        context = self._make_context()
        response = grc_exception_handler(exc, context)
        assert "status_code" in response.data
        assert response.data["status_code"] == 403
