# Generated by Django 5.0.6 on 2024-08-15 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspections", "0012_homeinspection_owner_visibility"),
    ]

    operations = [
        migrations.AddField(
            model_name="homeinspection",
            name="inspector",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
