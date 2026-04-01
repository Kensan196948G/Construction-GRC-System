"""Initial migration for reports app - Report model."""

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
            name="Report",
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
                ("title", models.CharField(max_length=300)),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            ("grc_dashboard", "経営層GRCダッシュボード"),
                            ("iso27001_annual", "ISO27001年次レポート"),
                            ("compliance_status", "規格別準拠レポート"),
                            ("risk_trend", "リスクトレンド分析"),
                            ("soa", "適用宣言書（SoA）"),
                            ("audit_report", "監査報告書"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "generated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "file_path",
                    models.FileField(blank=True, upload_to="reports/%Y/%m/"),
                ),
                (
                    "format",
                    models.CharField(default="pdf", help_text="pdf/xlsx", max_length=10),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "レポート",
                "verbose_name_plural": "レポート",
                "ordering": ["-created_at"],
            },
        ),
    ]
