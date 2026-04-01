"""GRCユーザーシリアライザ."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import GRCUser


class GRCUserSerializer(serializers.ModelSerializer):
    """GRCUser全フィールドシリアライザ（管理者向け）."""

    class Meta:
        model = GRCUser
        fields: list[str] = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "department",
            "display_name",
            "phone",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields: list[str] = ["id", "date_joined", "last_login"]
        extra_kwargs: dict[str, dict[str, bool]] = {
            "password": {"write_only": True, "required": True},
        }

    def create(self, validated_data: dict[str, Any]) -> GRCUser:
        password: str = validated_data.pop("password")
        user: GRCUser = GRCUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance: GRCUser, validated_data: dict[str, Any]) -> GRCUser:
        password: str | None = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """読み取り用プロフィールシリアライザ（パスワード除外）."""

    role_display: serializers.CharField = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = GRCUser
        fields: list[str] = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "department",
            "display_name",
            "phone",
            "is_active",
            "date_joined",
            "last_login",
        ]
        read_only_fields: list[str] = [
            "id",
            "username",
            "role",
            "is_active",
            "date_joined",
            "last_login",
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT取得時にユーザー情報も返却するシリアライザ."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = super().validate(attrs)
        user: GRCUser = self.user  # type: ignore[assignment]
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "role_display": user.get_role_display(),
            "display_name": str(user),
            "department": user.department,
        }
        return data
