# Generated by Django 5.0.6 on 2024-06-08 19:25

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_user_address_user_city_user_postal_code_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="builder",
            name="team",
        ),
        migrations.RemoveField(
            model_name="builder",
            name="vbn",
        ),
        migrations.AlterField(
            model_name="user",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("builder", "Builder"),
                    ("trade", "Trade"),
                    ("client", "Client"),
                    ("employee", "Employee"),
                ],
                default="client",
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name="BuilderEmployee",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("role", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "builder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employees",
                        to="users.builder",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employee",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
