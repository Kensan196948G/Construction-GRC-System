"""Add 'closed' status to Audit model."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audits", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="audit",
            name="status",
            field=models.CharField(
                choices=[
                    ("planned", "計画済み"),
                    ("in_progress", "実施中"),
                    ("completed", "完了"),
                    ("closed", "クローズ"),
                    ("cancelled", "中止"),
                ],
                default="planned",
                max_length=20,
            ),
        ),
    ]
