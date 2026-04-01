"""Initial migration for frameworks app - Framework model."""

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Framework",
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
                ("code", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("name_ja", models.CharField(max_length=200)),
                ("version", models.CharField(max_length=20)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("security", "セキュリティ"),
                            ("compliance", "コンプライアンス"),
                            ("legal", "法令"),
                            ("quality", "品質"),
                        ],
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("official_url", models.URLField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "フレームワーク定義",
                "verbose_name_plural": "フレームワーク定義",
                "ordering": ["code"],
            },
        ),
    ]
