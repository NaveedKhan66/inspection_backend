from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    USER_TYPES = (
        ("admin", "Admin"),
        ("builder", "Builder"),
        ("trade", "Trade"),
        ("client", "Client"),
        ("employee", "Employee"),
    )
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, db_index=True, editable=False
    )
    first_login = models.BooleanField(default=True)
    email = models.EmailField(_("email address"), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default="client")
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=610, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.IntegerField(null=True, blank=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.id} {self.email}"


class Builder(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, db_index=True, editable=False
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="builder")

    def __str__(self):
        return f"{self.user}"


class BuilderEmployee(models.Model):
    """Model class for employees of the builder"""

    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, db_index=True, editable=False
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    builder = models.ForeignKey(
        Builder, on_delete=models.CASCADE, related_name="employees"
    )
    role = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.builder}"


class Trade(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, db_index=True, editable=False
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trade")
    builder = models.ForeignKey(
        Builder, on_delete=models.CASCADE, related_name="trades"
    )

    def __str__(self):
        return f"{self.user} {self.builder}"


class Client(models.Model):
    """This is the model for Home Owner"""

    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, db_index=True, editable=False
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client")

    def __str__(self):
        return f"{self.user}"
