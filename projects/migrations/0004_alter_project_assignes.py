# Generated by Django 5.0.6 on 2024-06-10 19:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_alter_project_builder"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="assignes",
            field=models.ManyToManyField(
                related_name="employee_projects", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
