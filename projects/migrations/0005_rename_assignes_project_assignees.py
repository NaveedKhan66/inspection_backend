# Generated by Django 5.0.6 on 2024-06-10 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_alter_project_assignes"),
    ]

    operations = [
        migrations.RenameField(
            model_name="project",
            old_name="assignes",
            new_name="assignees",
        ),
    ]
