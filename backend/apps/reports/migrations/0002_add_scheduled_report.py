"""Migration: add ScheduledReport model."""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="ScheduledReport",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200, verbose_name="スケジュール名")),
                ("report_type", models.CharField(max_length=30)),
                (
                    "frequency",
                    models.CharField(
                        choices=[("daily", "毎日"), ("weekly", "毎週"), ("monthly", "毎月")],
                        default="weekly",
                        max_length=20,
                    ),
                ),
                ("recipients", models.JSONField(default=list, verbose_name="受信者メールアドレスリスト")),
                ("is_active", models.BooleanField(default=True)),
                ("last_run", models.DateTimeField(blank=True, null=True)),
                ("next_run", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "レポートスケジュール",
                "verbose_name_plural": "レポートスケジュール",
                "ordering": ["-created_at"],
            },
        ),
    ]
