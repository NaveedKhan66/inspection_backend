from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from inspections.models import HomeInspectionReview
from inspection_backend.settings import EMAIL_HOST_USER
from django.shortcuts import get_object_or_404


def get_inspection_data(home_inspection):
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
    address_list = [home.street_no, home.city, home.postal_code, home.address]
    home_address = " ".join([a for a in address_list if a])
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
    pdf_file = generate_inspection_report_pdf(request, home_inspection)
    owner_email = home_inspection.home.owner_email
    email = EmailMessage(
        "Inspection Report",
        "Please find the inspection report attached.",
        EMAIL_HOST_USER,
        [owner_email],
    )

    email.attach("inspection_report.pdf", pdf_file.getvalue(), "application/pdf")

    return email.send()
