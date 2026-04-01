import uuid

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models


class ISO27001Control(models.Model):
    """ISO27001:2022 管理策（全93管理策）"""

    class Domain(models.TextChoices):
        ORGANIZATIONAL = "organizational", "組織的管理策"
        PEOPLE = "people", "人的管理策"
        PHYSICAL = "physical", "物理的管理策"
        TECHNOLOGICAL = "technological", "技術的管理策"

    class ImplementationStatus(models.TextChoices):
        NOT_STARTED = "not_started", "未着手"
        IN_PROGRESS = "in_progress", "実施中"
        IMPLEMENTED = "implemented", "実施済み"
        PARTIALLY = "partially_implemented", "部分的に実施"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    control_id = models.CharField(max_length=10, unique=True, help_text="例: A.5.1")
    domain = models.CharField(max_length=100, choices=Domain.choices)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    implementation_guidance = models.TextField(blank=True)

    # 適用宣言書 (SoA)
    is_applicable = models.BooleanField(default=True)
    exclusion_reason = models.TextField(blank=True)

    # 実施状況
    implementation_status = models.CharField(
        max_length=30,
        choices=ImplementationStatus.choices,
        default=ImplementationStatus.NOT_STARTED,
    )
    implementation_notes = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_controls",
    )

    # 証跡
    evidence_required = ArrayField(models.CharField(max_length=200), default=list, blank=True)

    # NIST CSF マッピング
    nist_csf_mapping = ArrayField(models.CharField(max_length=20), default=list, blank=True)

    # レビュー
    review_date = models.DateField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["control_id"]
        verbose_name = "ISO27001管理策"
        verbose_name_plural = "ISO27001管理策"

    def __str__(self):
        return f"{self.control_id}: {self.title}"


class NistCSFCategory(models.Model):
    """NIST CSF 2.0 カテゴリ"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    function_id = models.CharField(max_length=10)
    function_name = models.CharField(max_length=50)
    function_name_ja = models.CharField(max_length=50)
    category_id = models.CharField(max_length=20, unique=True)
    category_name = models.CharField(max_length=200)
    category_name_ja = models.CharField(max_length=200)
    description = models.TextField()
    description_en = models.TextField(blank=True)

    class Meta:
        ordering = ["category_id"]
        verbose_name = "NIST CSFカテゴリ"
        verbose_name_plural = "NIST CSFカテゴリ"

    def __str__(self):
        return f"{self.category_id}: {self.category_name_ja}"


class Evidence(models.Model):
    """ISO27001 証跡（エビデンス）ファイル"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    control = models.ForeignKey(
        ISO27001Control,
        on_delete=models.CASCADE,
        related_name="evidences",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="evidences/%Y/%m/")
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "証跡ファイル"
        verbose_name_plural = "証跡ファイル"

    def __str__(self):
        return f"{self.control.control_id}: {self.title}"
