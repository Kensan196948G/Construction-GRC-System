"""Initial migration for controls app - ISO27001Control model."""
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
            name="ISO27001Control",
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
                    "control_id",
                    models.CharField(
                        help_text="例: A.5.1",
                        max_length=10,
                        unique=True,
                    ),
                ),
                (
                    "domain",
                    models.CharField(
                        choices=[
                            ("organizational", "組織的管理策"),
                            ("people", "人的管理策"),
                            ("physical", "物理的管理策"),
                            ("technological", "技術的管理策"),
                        ],
                        max_length=100,
                    ),
                ),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                ("implementation_guidance", models.TextField(blank=True)),
                ("is_applicable", models.BooleanField(default=True)),
                ("exclusion_reason", models.TextField(blank=True)),
                (
                    "implementation_status",
                    models.CharField(
                        choices=[
                            ("not_started", "未着手"),
                            ("in_progress", "実施中"),
                            ("implemented", "実施済み"),
                            ("partially_implemented", "部分的に実施"),
                        ],
                        default="not_started",
                        max_length=30,
                    ),
                ),
                ("implementation_notes", models.TextField(blank=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_controls",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "evidence_required",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=200),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                (
                    "nist_csf_mapping",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=20),
                        blank=True,
                        default=list,
                        size=None,
                    ),
                ),
                ("review_date", models.DateField(blank=True, null=True)),
                ("last_reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "ISO27001管理策",
                "verbose_name_plural": "ISO27001管理策",
                "ordering": ["control_id"],
            },
        ),
    ]
