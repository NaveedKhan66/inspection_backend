# Generated by Django 5.0.6 on 2024-06-26 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_user_phone_no"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="postal_code",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]