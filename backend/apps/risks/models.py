import uuid

from django.conf import settings
from django.db import models


class Risk(models.Model):
    """リスクレジスター: リスクの登録・評価・対応計画・ステータス管理"""

    class Category(models.TextChoices):
        IT = "IT", "IT・情報セキュリティ"
        PHYSICAL = "Physical", "物理的セキュリティ"
        LEGAL = "Legal", "法令・コンプライアンス"
        CONSTRUCTION = "Construction", "建設・施工"
        FINANCIAL = "Financial", "財務"
        OPERATIONAL = "Operational", "オペレーショナル"

    class TreatmentStrategy(models.TextChoices):
        ACCEPT = "accept", "受容"
        MITIGATE = "mitigate", "軽減"
        TRANSFER = "transfer", "移転"
        AVOID = "avoid", "回避"

    class Status(models.TextChoices):
        OPEN = "open", "オープン"
        IN_PROGRESS = "in_progress", "対応中"
        CLOSED = "closed", "クローズ"
        ACCEPTED = "accepted", "受容済み"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    risk_id = models.CharField(max_length=20, unique=True, help_text="例: RISK-IT-001")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=Category.choices)
    source = models.CharField(max_length=50, blank=True)

    # 固有リスク評価
    likelihood_inherent = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], help_text="発生可能性 (1-5)"
    )
    impact_inherent = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], help_text="影響度 (1-5)"
    )

    # 残存リスク評価
    likelihood_residual = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True
    )
    impact_residual = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True
    )

    # 対応
    treatment_strategy = models.CharField(
        max_length=20, choices=TreatmentStrategy.choices, blank=True
    )
    treatment_plan = models.TextField(blank=True)
    risk_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_risks",
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    # タイムスタンプ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "リスク"
        verbose_name_plural = "リスク"

    def __str__(self):
        return f"{self.risk_id}: {self.title}"

    @property
    def risk_score_inherent(self):
        return self.likelihood_inherent * self.impact_inherent

    @property
    def risk_score_residual(self):
        if self.likelihood_residual and self.impact_residual:
            return self.likelihood_residual * self.impact_residual
        return None

    @property
    def risk_level(self):
        score = self.risk_score_inherent
        if score >= 15:
            return "CRITICAL"
        if score >= 10:
            return "HIGH"
        if score >= 5:
            return "MEDIUM"
        return "LOW"
