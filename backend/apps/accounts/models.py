"""GRCユーザーモデル定義."""
from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class GRCUser(AbstractUser):
    """建設業GRCシステム用カスタムユーザーモデル."""

    class Role(models.TextChoices):
        GRC_ADMIN = "grc_admin", "GRC管理者"
        RISK_OWNER = "risk_owner", "リスクオーナー"
        COMPLIANCE_OFFICER = "compliance_officer", "コンプライアンス担当"
        AUDITOR = "auditor", "内部監査員"
        EXECUTIVE = "executive", "経営層"
        GENERAL = "general", "一般部門担当"

    role: models.CharField[str, str] = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.GENERAL,
        verbose_name="ロール",
    )
    department: models.CharField[str, str] = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="部署",
    )
    display_name: models.CharField[str, str] = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="表示名",
    )
    phone: models.CharField[str, str] = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="電話番号",
    )

    class Meta:
        verbose_name = "GRCユーザー"
        verbose_name_plural = "GRCユーザー"
        ordering = ["username"]

    def __str__(self) -> str:
        return self.display_name or self.get_full_name() or self.username
