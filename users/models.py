from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_login = models.BooleanField(default=True)
    pass
