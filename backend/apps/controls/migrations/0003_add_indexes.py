from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("controls", "0002_nistcsfcategory")]

    operations = [
        migrations.AddIndex(
            model_name="iso27001control",
            index=models.Index(fields=["implementation_status"], name="idx_ctrl_impl_status"),
        ),
        migrations.AddIndex(
            model_name="iso27001control",
            index=models.Index(
                fields=["domain", "implementation_status"],
                name="idx_ctrl_domain_status",
            ),
        ),
    ]
