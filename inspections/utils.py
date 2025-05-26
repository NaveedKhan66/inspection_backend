from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from inspections.models import HomeInspectionReview
from inspection_backend.settings import EMAIL_HOST_USER
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from inspections.models import DeficiencyUpdateLog
from inspections.models import DeficiencyNotification
import threading
from datetime import date, datetime
from inspections.models import HomeInspection
import pytz

User = get_user_model()


def get_inspection_data(home_inspection: HomeInspection):
    builder = home_inspection.home.project.builder
    home = home_inspection.home
    home_owner_email = home.owner_email
    home_owner_name = home.owner_name
    enrollment_no = home.enrollment_no
    deficiencies = home_inspection.deficiencies.all()
    inspection_review_object = get_object_or_404(
        HomeInspectionReview, home_inspection=home_inspection
    )
    inspector_signature = inspection_review_object.inspector_signature_image
    owner_signature = inspection_review_object.owner_signature_image
    inspection_name = inspection_review_object.home_inspection.inspection.name
    address_list = [home.street_no, home.address, home.city]
    home_address = " ".join([a for a in address_list if a])

    # Get Ontario timezone
    ontario_tz = pytz.timezone("America/Toronto")
    # Get current UTC time and convert to Ontario timezone
    creation_date = (
        datetime.now(pytz.UTC).astimezone(ontario_tz).strftime("%B %d, %Y at %I:%M %p")
    )

    context = {
        "inspection_name": inspection_name,
        "builder": builder,
        "home_owner_email": home_owner_email,
        "home_owner_name": home_owner_name,
        "home_address": home_address,
        "enrollment_no": enrollment_no,
        "deficiencies": deficiencies,
        "inspector_signature": inspector_signature,
        "owner_signature": owner_signature,
        "inspector_name": home_inspection.inspector,
        "creation_date": creation_date,
    }
    return context


def generate_inspection_report_pdf(request, home_inspection):
    context = get_inspection_data(home_inspection)

    html_string = render_to_string("inspection_pdf.html", context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = BytesIO()
    html.write_pdf(pdf_file)
    return pdf_file


def send_inspection_report_email(request, home_inspection):
    """Send email to builder and owner"""

    send_email_to = [home_inspection.home.project.builder.email]
    pdf_file = generate_inspection_report_pdf(request, home_inspection)
    if home_inspection.owner_visibility:
        send_email_to.append(home_inspection.home.owner_email)
    subject = f"{home_inspection.inspection.name} Report - {home_inspection.home.street_no} {home_inspection.home.address} - {home_inspection.inspection.builder.get_full_name()} - {date.today().strftime('%m/%d/%Y')}"
    email = EmailMessage(
        subject,
        "Please find the inspection report attached.",
        EMAIL_HOST_USER,
        send_email_to,
    )

    email.attach("inspection_report.pdf", pdf_file.getvalue(), "application/pdf")

    return email.send()


def get_notification_users(user):
    """populate users to which the notification will be sent"""

    builder_user = None
    notification_users = None
    if user.user_type == "builder":
        notification_users = User.objects.filter(employee__builder__user=user)
    elif user.user_type == "trade":
        # Get all builders associated with the trade
        builders = user.trade.builder.all()
        # Get all employees for all builders
        notification_users = User.objects.filter(employee__builder__in=builders)
    elif user.user_type == "employee":
        builder_user = user.employee.builder.user
        notification_users = User.objects.filter(employee__builder__user=builder_user)

    return notification_users


def bulk_create_deficiency_update_logs(changes, instance, actor):
    """used upon deficiency update"""

    logs_to_create = [
        DeficiencyUpdateLog(
            deficiency=instance,
            actor_name=actor.get_full_name() if actor else "System",
            description=change,
        )
        for change in changes
    ]
    DeficiencyUpdateLog.objects.bulk_create(logs_to_create)


def bulk_create_deficiency_notifications(
    changes, instance, actor, notification_users, builder_user
):
    """used upon deficiency update"""

    for change in changes:
        notifications = [
            DeficiencyNotification(
                deficiency=instance,
                user=user,
                actor_name=actor.get_full_name() if actor else "System",
                description=change,
            )
            for user in notification_users
        ]

    DeficiencyNotification.objects.bulk_create(notifications)
    if builder_user:
        for change in changes:
            DeficiencyNotification.objects.create(
                deficiency=instance,
                user=builder_user,
                actor_name=actor.get_full_name() if actor else "System",
                description=change,
            )
    if actor.user_type == "builder":
        for change in changes:
            DeficiencyNotification.objects.create(
                deficiency=instance,
                user=instance.trade,
                actor_name=actor.get_full_name() if actor else "System",
                description=change,
            )


class DeficiencyUpdateLogsCreationThread(threading.Thread):

    def __init__(self, changes, instance, actor):
        threading.Thread.__init__(self)
        self.changes = changes
        self.instance = instance
        self.actor = actor

    def run(self):
        bulk_create_deficiency_update_logs(self.changes, self.instance, self.actor)


class DeficiencyNotificationsCreationThread(threading.Thread):

    def __init__(self, changes, instance, actor, notification_users, builder_user):
        threading.Thread.__init__(self)
        self.changes = changes
        self.instance = instance
        self.actor = actor
        self.notification_users = notification_users
        self.builder_user = builder_user

    def run(self):
        bulk_create_deficiency_notifications(
            self.changes,
            self.instance,
            self.actor,
            self.notification_users,
            self.builder_user,
        )
