# Generated by Django 5.0.6 on 2024-10-30 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspections", "0014_deficiencynotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="deficiency",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="homeinspection",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
