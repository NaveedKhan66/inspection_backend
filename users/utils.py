from inspection_backend.settings import EMAIL_HOST_USER
from inspection_backend.settings import RESET_PASSOWRD_LINK
from django.core.mail import send_mail


def send_reset_email(email, token):
    link = f"{RESET_PASSOWRD_LINK}?token={token}"
    send_mail(
        "Reset your password",
        f"Click the link to set your password: {link}",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
