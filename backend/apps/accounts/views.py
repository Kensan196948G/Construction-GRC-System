"""GRC認証・ユーザー管理ビュー."""

from __future__ import annotations

import base64
import io

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import GRCUser
from apps.accounts.permissions import IsGRCAdmin
from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    GRCUserSerializer,
    UserProfileSerializer,
)
from apps.accounts.totp import generate_totp_secret, get_provisioning_uri, verify_totp


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


class TOTPSetupView(APIView):
    """2FA設定開始: 秘密鍵生成 + QRコード URI 返却."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.totp_secret:
            user.totp_secret = generate_totp_secret()
            user.save(update_fields=["totp_secret"])
        uri = get_provisioning_uri(user.totp_secret, user.username)
        try:
            import qrcode

            img = qrcode.make(uri)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_base64 = base64.b64encode(buf.getvalue()).decode()
        except ImportError:
            qr_base64 = ""
        return Response(
            {
                "secret": user.totp_secret,
                "provisioning_uri": uri,
                "qr_code_base64": qr_base64,
            }
        )


class TOTPVerifyView(APIView):
    """2FA 検証: トークン確認 → 有効化."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token", "")
        user = request.user
        if not user.totp_secret:
            return Response(
                {"error": "2FAが設定されていません"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if verify_totp(user.totp_secret, str(token)):
            user.totp_enabled = True
            user.save(update_fields=["totp_enabled"])
            return Response({"message": "2FAを有効化しました"})
        return Response(
            {"error": "無効なトークンです"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TOTPDisableView(APIView):
    """2FA 無効化."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.totp_enabled = False
        user.totp_secret = ""
        user.save(update_fields=["totp_enabled", "totp_secret"])
        return Response({"message": "2FAを無効化しました"})
