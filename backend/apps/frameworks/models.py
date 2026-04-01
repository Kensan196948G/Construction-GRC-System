import uuid

from django.db import models


class Framework(models.Model):
    """フレームワーク定義"""

    class Category(models.TextChoices):
        SECURITY = "security", "セキュリティ"
        COMPLIANCE = "compliance", "コンプライアンス"
        LEGAL = "legal", "法令"
        QUALITY = "quality", "品質"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True, help_text='例: "iso27001", "nist_csf_2", "construction_law"')
    name = models.CharField(max_length=200)
    name_ja = models.CharField(max_length=200)
    version = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    is_active = models.BooleanField(default=True)
    official_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "フレームワーク定義"
        verbose_name_plural = "フレームワーク定義"

    def __str__(self):
        return f"{self.code}: {self.name_ja}"
