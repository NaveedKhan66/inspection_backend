# Generated by Django 5.0.6 on 2024-06-12 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0011_home_project"),
    ]

    operations = [
        migrations.AlterField(
            model_name="home",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="homes",
                to="projects.project",
            ),
        ),
    ]
