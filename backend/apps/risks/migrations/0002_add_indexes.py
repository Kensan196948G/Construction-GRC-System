from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("risks", "0001_initial")]

    operations = [
        migrations.AddIndex(
            model_name="risk",
            index=models.Index(fields=["status"], name="idx_risk_status"),
        ),
        migrations.AddIndex(
            model_name="risk",
            index=models.Index(fields=["category"], name="idx_risk_category"),
        ),
        migrations.AddIndex(
            model_name="risk",
            index=models.Index(fields=["category", "status"], name="idx_risk_cat_status"),
        ),
    ]
