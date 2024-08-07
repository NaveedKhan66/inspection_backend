from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser if not exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        if email:
            email = email.lower()
        if username:
            username = username.lower()
        if not User.objects.filter(email=email, username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password, user_type="admin"
            )
            self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
