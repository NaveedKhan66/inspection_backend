# Generated by Django 5.0.6 on 2025-02-17 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspections", "0015_deficiency_updated_at_homeinspection_updated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="deficiency",
            name="completion_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
