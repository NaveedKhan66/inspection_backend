# Generated by Django 5.0.6 on 2024-06-29 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspections", "0003_deficiencyreview"),
    ]

    operations = [
        migrations.AddField(
            model_name="deficiency",
            name="is_reviewed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="deficiencyreview",
            name="inspector_name",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
