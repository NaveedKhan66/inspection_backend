# Generated by Django 5.0.6 on 2024-07-05 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0014_alter_project_postal_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="home",
            name="enrollment_no",
            field=models.IntegerField(unique=True),
        ),
    ]