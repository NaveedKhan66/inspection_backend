from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
from project_utils.choices import ExtendedChoices


class User(AbstractUser):
    USER_TYPES = ExtendedChoices(
        (1, "admin", "Admin"),
        (2, "builder", "Builder"),
        (3, "trade", "Trade"),
        (4, "client", "Client"),
    )
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, db_index=True, editable=False
    )
    first_login = models.BooleanField(default=True)
    email = models.EmailField(_("email address"), unique=True)
    user_type = models.PositiveSmallIntegerField(
        choices=USER_TYPES, default=USER_TYPES.client
    )

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
