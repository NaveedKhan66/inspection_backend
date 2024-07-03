# Generated by Django 5.0.6 on 2024-06-29 15:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspections", "0007_deficiency_home_inspection"),
    ]

    operations = [
        migrations.AlterField(
            model_name="deficiency",
            name="home_inspection",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="deficiencies",
                to="inspections.homeinspection",
            ),
        ),
    ]