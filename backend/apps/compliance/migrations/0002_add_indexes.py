from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("compliance", "0001_initial")]

    operations = [
        migrations.AddIndex(
            model_name="compliancerequirement",
            index=models.Index(fields=["framework"], name="idx_compliance_framework"),
        ),
        migrations.AddIndex(
            model_name="compliancerequirement",
            index=models.Index(fields=["compliance_status"], name="idx_compliance_status"),
        ),
    ]
