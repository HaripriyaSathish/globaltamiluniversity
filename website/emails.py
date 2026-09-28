"""
Email notifications for form submissions.

A failed email never loses a submission: the record is saved first and
email errors are only logged.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def _send(subject, body, recipients, reply_to=None):
    recipients = [r for r in recipients if r]
    if not recipients:
        return
    try:
        EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, recipients,
                     reply_to=[reply_to] if reply_to else None).send()
    except Exception:
        logger.exception("Could not send email %r to %s", subject, recipients)


def notify_new_application(application, section, site):
    admin_body = (
        f"New application received on the website.\n\n"
        f"Name: {application.full_name}\n"
        f"Email: {application.email}\n"
        f"Phone: {application.phone}\n"
        f"Program: {application.program_name}\n"
        f"Highest qualification: {application.qualification}\n"
        f"Year of passing: {application.year_of_passing}\n\n"
        f"Goals:\n{application.goals or '-'}\n"
    )
    _send(f"New application: {application.full_name} – {application.program_name}",
          admin_body, [settings.ENQUIRY_RECEIVER_EMAIL], reply_to=application.email)

    if section.send_confirmation_email:
        _send(
            f"We received your application – {site.university_name.title()}",
            f"Dear {application.full_name},\n\n"
            f"Thank you for applying to {application.program_name} at {site.university_name.title()}.\n"
            f"{section.success_message}\n\n"
            f"Regards,\nAdmissions Team\n{site.university_name.title()}\n{site.phone}  |  {site.email}\n",
            [application.email],
        )


def notify_new_contact_message(msg, section, site):
    admin_body = (
        f"New contact message from the website.\n\n"
        f"Name: {msg.name}\n"
        f"Email: {msg.email}\n"
        f"Phone: {msg.phone or '-'}\n"
        f"Subject: {msg.subject_name}\n\n"
        f"Message:\n{msg.message}\n"
    )
    _send(f"New enquiry: {msg.subject_name} – {msg.name}",
          admin_body, [settings.ENQUIRY_RECEIVER_EMAIL], reply_to=msg.email)

    if section.send_confirmation_email:
        _send(
            f"Thank you for contacting {site.university_name.title()}",
            f"Dear {msg.name},\n\n{section.success_message}\n\n"
            f"Your message:\n{msg.message}\n\n"
            f"Regards,\n{site.university_name.title()}\n{site.phone}  |  {site.email}\n",
            [msg.email],
        )
