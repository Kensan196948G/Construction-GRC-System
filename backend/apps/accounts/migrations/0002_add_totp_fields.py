"""Migration: add totp_secret and totp_enabled fields to GRCUser."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]
    operations = [
        migrations.AddField(
            model_name="grcuser",
            name="totp_secret",
            field=models.CharField(blank=True, default="", max_length=64, verbose_name="TOTP秘密鍵"),
        ),
        migrations.AddField(
            model_name="grcuser",
            name="totp_enabled",
            field=models.BooleanField(default=False, verbose_name="2FA有効"),
        ),
    ]
