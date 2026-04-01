import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("audits", "0002_add_closed_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityLog",
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
                    "action",
                    models.CharField(
                        choices=[
                            ("create", "作成"),
                            ("update", "更新"),
                            ("delete", "削除"),
                            ("status_change", "ステータス変更"),
                            ("login", "ログイン"),
                            ("export", "エクスポート"),
                        ],
                        max_length=20,
                    ),
                ),
                ("model_name", models.CharField(max_length=100)),
                ("object_id", models.CharField(blank=True, max_length=100)),
                ("object_repr", models.CharField(blank=True, max_length=300)),
                ("changes", models.JSONField(blank=True, default=dict)),
                (
                    "ip_address",
                    models.GenericIPAddressField(blank=True, null=True),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "アクティビティログ",
                "verbose_name_plural": "アクティビティログ",
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(
                        fields=["-timestamp"],
                        name="audits_acti_timesta_idx",
                    ),
                    models.Index(
                        fields=["model_name", "-timestamp"],
                        name="audits_acti_model_n_idx",
                    ),
                ],
            },
        ),
    ]
