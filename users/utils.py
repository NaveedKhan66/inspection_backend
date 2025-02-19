from inspection_backend.settings import EMAIL_HOST_USER
from inspection_backend.settings import RESET_PASSOWRD_LINK
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from users.models import BuilderEmployee
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

User = get_user_model()


def send_reset_email(email, token):
    link = f"{RESET_PASSOWRD_LINK}?token={token}"
    send_mail(
        "Reset your password",
        f"Click the link to set your password: {link}",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )


def send_trade_welcome_email(trade, builder):
    subject = f"You have been added to {builder.user.first_name}'s Trade List"
    message = render_to_string(
        "trade_welcome_email.html",
        {
            "trade": trade,
            "builder": builder,
        },
    )

    msg = EmailMultiAlternatives(
        subject,
        "",
        EMAIL_HOST_USER,
        [trade.user.email],
    )
    msg.attach_alternative(message, "text/html")
    msg.send()


def create_employee_for_builder(instance):
    email_parts = instance.email.split("@")
    employee_email = f"{email_parts[0]}+team@{email_parts[1]}"

    # Create the Employee user
    employee_user = User.objects.create(
        username=employee_email,
        email=employee_email,
        user_type="employee",
        first_name=instance.first_name if instance.first_name else "",
        last_name=instance.last_name if instance.last_name else "",
    )
    employee_user.set_unusable_password()
    employee_user.save()

    # Create the Employee instance
    BuilderEmployee.objects.create(
        user=employee_user, builder=instance.builder, role="Builder"
    )


def set_password_for_employee(instance, password):
    email_parts = instance.email.split("@")
    employee_email = f"{email_parts[0]}+team@{email_parts[1]}"
    try:
        employee = User.objects.get(email=employee_email)
        employee.set_password(password)
        employee.save()
    except User.DoesNotExist:
        return
