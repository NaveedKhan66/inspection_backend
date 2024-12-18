# Generated by Django 5.0.6 on 2024-12-18 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0013_blacklistedtoken"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trade",
            name="builder",
        ),
        migrations.AddField(
            model_name="trade",
            name="builder",
            field=models.ManyToManyField(related_name="trades", to="users.builder"),
        ),
    ]