"""GRCロールベースパーミッション."""
from __future__ import annotations

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.accounts.models import GRCUser


class IsGRCAdmin(BasePermission):
    """GRC管理者のみ許可."""

    message = "GRC管理者権限が必要です。"

    def has_permission(self, request: Request, view: APIView) -> bool:
        user: Any = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == GRCUser.Role.GRC_ADMIN
        )


class IsAuditor(BasePermission):
    """内部監査員以上（監査員・GRC管理者）を許可."""

    message = "内部監査員以上の権限が必要です。"

    ALLOWED_ROLES: frozenset[str] = frozenset(
        {GRCUser.Role.AUDITOR, GRCUser.Role.GRC_ADMIN}
    )

    def has_permission(self, request: Request, view: APIView) -> bool:
        user: Any = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in self.ALLOWED_ROLES
        )


class IsExecutiveOrAbove(BasePermission):
    """経営層+GRC管理者を許可."""

    message = "経営層以上の権限が必要です。"

    ALLOWED_ROLES: frozenset[str] = frozenset(
        {GRCUser.Role.EXECUTIVE, GRCUser.Role.GRC_ADMIN}
    )

    def has_permission(self, request: Request, view: APIView) -> bool:
        user: Any = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in self.ALLOWED_ROLES
        )


class RoleBasedPermission(BasePermission):
    """ロールに基づく汎用パーミッション.

    ビューに ``allowed_roles`` 属性 (Sequence[str]) を定義して利用する。

    使用例::

        class SomeView(APIView):
            permission_classes = [RoleBasedPermission]
            allowed_roles = [GRCUser.Role.GRC_ADMIN, GRCUser.Role.AUDITOR]
    """

    message = "この操作に必要なロールがありません。"

    def has_permission(self, request: Request, view: APIView) -> bool:
        user: Any = request.user
        if not (user and user.is_authenticated):
            return False
        allowed_roles: list[str] | tuple[str, ...] = getattr(
            view, "allowed_roles", []
        )
        if not allowed_roles:
            return True
        return getattr(user, "role", None) in allowed_roles
