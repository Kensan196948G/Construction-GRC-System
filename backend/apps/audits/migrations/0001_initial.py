"""Initial migration for audits app - Audit and AuditFinding models."""

import uuid

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
            name="Audit",
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
                    "audit_id",
                    models.CharField(
                        help_text="例: AUD-2026-001",
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                (
                    "audit_type",
                    models.CharField(help_text="例: ISO27001定期監査", max_length=50),
                ),
                ("target_department", models.CharField(max_length=100)),
                (
                    "lead_auditor",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="led_audits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("planned_start", models.DateField()),
                ("planned_end", models.DateField()),
                ("actual_start", models.DateField(blank=True, null=True)),
                ("actual_end", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "計画済み"),
                            ("in_progress", "実施中"),
                            ("completed", "完了"),
                            ("cancelled", "中止"),
                        ],
                        default="planned",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "監査",
                "verbose_name_plural": "監査",
                "ordering": ["-planned_start"],
            },
        ),
        migrations.CreateModel(
            name="AuditFinding",
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
                    "audit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="findings",
                        to="audits.audit",
                    ),
                ),
                (
                    "finding_id",
                    models.CharField(max_length=20, unique=True),
                ),
                (
                    "finding_type",
                    models.CharField(
                        choices=[
                            ("major_nc", "重大不適合"),
                            ("minor_nc", "軽微不適合"),
                            ("observation", "観察事項"),
                            ("positive", "優良事項"),
                        ],
                        max_length=20,
                    ),
                ),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField()),
                ("evidence", models.TextField(blank=True)),
                ("root_cause", models.TextField(blank=True)),
                ("cap_required", models.BooleanField(default=True)),
                ("cap_description", models.TextField(blank=True)),
                (
                    "cap_owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_caps",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("cap_due_date", models.DateField(blank=True, null=True)),
                (
                    "cap_status",
                    models.CharField(
                        choices=[
                            ("open", "オープン"),
                            ("in_progress", "対応中"),
                            ("verified", "検証済み"),
                            ("closed", "クローズ"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "監査所見",
                "verbose_name_plural": "監査所見",
                "ordering": ["finding_id"],
            },
        ),
    ]
