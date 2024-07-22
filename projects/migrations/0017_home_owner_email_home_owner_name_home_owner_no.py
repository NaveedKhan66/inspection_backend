# Generated by Django 5.0.6 on 2024-07-16 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0016_alter_home_enrollment_no"),
    ]

    operations = [
        migrations.AddField(
            model_name="home",
            name="owner_email",
            field=models.EmailField(
                blank=True, max_length=254, null=True, verbose_name="email address"
            ),
        ),
        migrations.AddField(
            model_name="home",
            name="owner_name",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="home",
            name="owner_no",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]