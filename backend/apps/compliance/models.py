import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class ComplianceRequirement(models.Model):
    """法令・規格要件管理"""

    class Framework(models.TextChoices):
        CONSTRUCTION_LAW = "construction_law", "建設業法"
        QUALITY_LAW = "quality_law", "品確法"
        SAFETY_LAW = "safety_law", "労安法"
        ISO27001 = "iso27001", "ISO27001"
        NIST_CSF = "nist_csf", "NIST CSF 2.0"
        ISO20000 = "iso20000", "ISO20000"
        SUBCONTRACT_LAW = "subcontract_law", "下請法"

    class ComplianceStatus(models.TextChoices):
        COMPLIANT = "compliant", "準拠"
        NON_COMPLIANT = "non_compliant", "非準拠"
        PARTIAL = "partial", "部分的準拠"
        UNKNOWN = "unknown", "未評価"

    class Frequency(models.TextChoices):
        ANNUAL = "annual", "年次"
        QUARTERLY = "quarterly", "四半期"
        MONTHLY = "monthly", "月次"
        ONGOING = "ongoing", "継続的"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    req_id = models.CharField(max_length=30, unique=True)
    framework = models.CharField(max_length=50, choices=Framework.choices)
    category = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    article_ref = models.CharField(max_length=100, blank=True, help_text="条文番号")
    is_mandatory = models.BooleanField(default=True)
    due_date = models.DateField(null=True, blank=True)
    frequency = models.CharField(max_length=30, choices=Frequency.choices, blank=True)

    # 準拠状況
    compliance_status = models.CharField(
        max_length=20, choices=ComplianceStatus.choices, default=ComplianceStatus.UNKNOWN
    )
    evidence_ids = ArrayField(models.UUIDField(), default=list, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_requirements",
    )
    last_assessed_at = models.DateTimeField(null=True, blank=True)
    next_assessment = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["framework", "req_id"]
        verbose_name = "法令要件"
        verbose_name_plural = "法令要件"

    def __str__(self):
        return f"{self.req_id}: {self.title}"
