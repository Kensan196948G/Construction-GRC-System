"""GRC認証・ユーザー管理ビュー."""

from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import GRCUser
from apps.accounts.permissions import IsGRCAdmin
from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    GRCUserSerializer,
    UserProfileSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT取得（ユーザー情報付き）."""

    serializer_class = CustomTokenObtainPairSerializer  # type: ignore[assignment]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """ログインユーザーのプロフィール取得・更新.

    GET  /api/v1/auth/profile/ - プロフィール取得
    PATCH /api/v1/auth/profile/ - プロフィール更新
    """

    serializer_class = UserProfileSerializer
    permission_classes: list[type] = [IsAuthenticated]

    def get_object(self) -> GRCUser:
        return self.request.user  # type: ignore[return-value]


class UserListView(generics.ListCreateAPIView):
    """ユーザー一覧・作成（GRC管理者のみ）.

    GET  /api/v1/auth/users/ - ユーザー一覧
    POST /api/v1/auth/users/ - ユーザー作成
    """

    queryset = GRCUser.objects.all().order_by("username")
    serializer_class = GRCUserSerializer
    permission_classes: list[type] = [IsAuthenticated, IsGRCAdmin]
    filterset_fields: list[str] = ["role", "department", "is_active"]
    search_fields: list[str] = ["username", "email", "display_name", "department"]
    ordering_fields: list[str] = ["username", "date_joined", "role"]
