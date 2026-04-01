"""Add NistCSFCategory model."""

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NistCSFCategory",
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
                ("function_id", models.CharField(max_length=10)),
                ("function_name", models.CharField(max_length=50)),
                ("function_name_ja", models.CharField(max_length=50)),
                (
                    "category_id",
                    models.CharField(max_length=20, unique=True),
                ),
                ("category_name", models.CharField(max_length=200)),
                ("category_name_ja", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("description_en", models.TextField(blank=True, default="")),
            ],
            options={
                "verbose_name": "NIST CSFカテゴリ",
                "verbose_name_plural": "NIST CSFカテゴリ",
                "ordering": ["category_id"],
            },
        ),
    ]
