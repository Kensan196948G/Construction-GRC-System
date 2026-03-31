"""GRCUser管理画面設定."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import GRCUser


@admin.register(GRCUser)
class GRCUserAdmin(UserAdmin):
    """GRCユーザー管理画面."""

    list_display: list[str] = [
        "username",
        "email",
        "display_name",
        "role",
        "department",
        "is_active",
    ]
    list_filter: list[str] = ["role", "department", "is_active", "is_staff"]
    search_fields: list[str] = ["username", "email", "display_name", "department"]
    ordering: list[str] = ["username"]

    fieldsets = UserAdmin.fieldsets + (  # type: ignore[operator]
        (
            "GRC情報",
            {
                "fields": ("role", "department", "display_name", "phone"),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (  # type: ignore[operator]
        (
            "GRC情報",
            {
                "fields": ("role", "department", "display_name", "phone"),
            },
        ),
    )
