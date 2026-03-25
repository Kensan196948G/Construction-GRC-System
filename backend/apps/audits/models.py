import uuid

from django.conf import settings
from django.db import models


class Audit(models.Model):
    """内部監査計画"""

    class Status(models.TextChoices):
        PLANNED = "planned", "計画済み"
        IN_PROGRESS = "in_progress", "実施中"
        COMPLETED = "completed", "完了"
        CANCELLED = "cancelled", "中止"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_id = models.CharField(max_length=20, unique=True, help_text="例: AUD-2026-001")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    audit_type = models.CharField(max_length=50, help_text="例: ISO27001定期監査")
    target_department = models.CharField(max_length=100)

    lead_auditor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="led_audits",
    )
    planned_start = models.DateField()
    planned_end = models.DateField()
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-planned_start"]
        verbose_name = "監査"
        verbose_name_plural = "監査"

    def __str__(self):
        return f"{self.audit_id}: {self.title}"


class AuditFinding(models.Model):
    """監査所見"""

    class FindingType(models.TextChoices):
        MAJOR_NC = "major_nc", "重大不適合"
        MINOR_NC = "minor_nc", "軽微不適合"
        OBSERVATION = "observation", "観察事項"
        POSITIVE = "positive", "優良事項"

    class CAPStatus(models.TextChoices):
        OPEN = "open", "オープン"
        IN_PROGRESS = "in_progress", "対応中"
        VERIFIED = "verified", "検証済み"
        CLOSED = "closed", "クローズ"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name="findings")
    finding_id = models.CharField(max_length=20, unique=True)
    finding_type = models.CharField(max_length=20, choices=FindingType.choices)
    title = models.CharField(max_length=300)
    description = models.TextField()
    evidence = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)

    # 是正処置 (CAP)
    cap_required = models.BooleanField(default=True)
    cap_description = models.TextField(blank=True)
    cap_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_caps",
    )
    cap_due_date = models.DateField(null=True, blank=True)
    cap_status = models.CharField(
        max_length=20, choices=CAPStatus.choices, default=CAPStatus.OPEN
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["finding_id"]
        verbose_name = "監査所見"
        verbose_name_plural = "監査所見"

    def __str__(self):
        return f"{self.finding_id}: {self.title}"
