"""Initial migration for risks app - Risk model."""

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
            name="Risk",
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
                    "risk_id",
                    models.CharField(
                        help_text="例: RISK-IT-001",
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("title", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("IT", "IT・情報セキュリティ"),
                            ("Physical", "物理的セキュリティ"),
                            ("Legal", "法令・コンプライアンス"),
                            ("Construction", "建設・施工"),
                            ("Financial", "財務"),
                            ("Operational", "オペレーショナル"),
                        ],
                        max_length=50,
                    ),
                ),
                ("source", models.CharField(blank=True, max_length=50)),
                (
                    "likelihood_inherent",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        help_text="発生可能性 (1-5)",
                    ),
                ),
                (
                    "impact_inherent",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        help_text="影響度 (1-5)",
                    ),
                ),
                (
                    "likelihood_residual",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        null=True,
                    ),
                ),
                (
                    "impact_residual",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        null=True,
                    ),
                ),
                (
                    "treatment_strategy",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("accept", "受容"),
                            ("mitigate", "軽減"),
                            ("transfer", "移転"),
                            ("avoid", "回避"),
                        ],
                        max_length=20,
                    ),
                ),
                ("treatment_plan", models.TextField(blank=True)),
                (
                    "risk_owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_risks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("target_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "オープン"),
                            ("in_progress", "対応中"),
                            ("closed", "クローズ"),
                            ("accepted", "受容済み"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("review_date", models.DateField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "リスク",
                "verbose_name_plural": "リスク",
                "ordering": ["-created_at"],
            },
        ),
    ]
