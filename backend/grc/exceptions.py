from rest_framework import status
from rest_framework.exceptions import APIException


class GRCBaseException(APIException):
    """GRCシステム基底例外"""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "内部エラーが発生しました。"
    default_code = "grc_error"


class ResourceNotFoundError(GRCBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "指定されたリソースが見つかりません。"
    default_code = "resource_not_found"


class ComplianceStateError(GRCBaseException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "コンプライアンス状態の矛盾が検出されました。"
    default_code = "compliance_state_error"


class InsufficientPermissionError(GRCBaseException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "この操作に必要な権限がありません。"
    default_code = "insufficient_permission"


class RiskAssessmentError(GRCBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "リスク評価パラメータが不正です。"
    default_code = "risk_assessment_error"
