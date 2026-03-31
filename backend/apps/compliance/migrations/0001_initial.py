"""Initial migration for compliance app - ComplianceRequirement model."""

import uuid

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ComplianceRequirement",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "req_id",
                    models.CharField(max_length=30, unique=True),
                ),
                (
                    "framework",
                    models.CharField(
                        choices=[
                            ("construction_law", "建設業法"),
                            ("quality_law", "品確法"),
                            ("safety_law", "労安法"),
                            ("iso27001", "ISO27001"),
                            ("nist_csf", "NIST CSF 2.0"),
                            ("iso20000", "ISO20000"),
                            ("subcontract_law", "下請法"),
                        ],
                        max_length=50,
                    ),
                ),
                ("category", models.CharField(blank=True, max_length=100)),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                (
                    "article_ref",
                    models.CharField(blank=True, help_text="条文番号", max_length=100),
                ),
                ("is_mandatory", models.BooleanField(default=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "frequency",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("annual", "年次"),
                            ("quarterly", "四半期"),
                            ("monthly", "月次"),
                            ("ongoing", "継続的"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "compliance_status",
                    models.CharField(
                        choices=[
                            ("compliant", "準拠"),
                            ("non_compliant", "非準拠"),
                            ("partial", "部分的準拠"),
                            ("unknown", "未評価"),
                        ],
                        default="unknown",
                        max_length=20,
                    ),
                ),
                (
                    "evidence_ids",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.UUIDField(),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_requirements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("last_assessed_at", models.DateTimeField(blank=True, null=True)),
                ("next_assessment", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "法令要件",
                "verbose_name_plural": "法令要件",
                "ordering": ["framework", "req_id"],
            },
        ),
    ]
