# Generated by Django 5.0.6 on 2024-06-26 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0013_alter_home_warranty_start_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="postal_code",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
