from django.conf import settings
from mailersend import emails


ONBOARDING_TEMPLATE = "0r83ql3qv6x4zw1j"
ONBOARDING_SUBJECT = "Welcome to tellme"
VERIFICATION_TEMPLATE = "3z0vklopmopg7qrx"
VERIFICATION_SUBJECT = "tellme - Verify your Email"


def send_email_with_link(target_name: str, target_email: str, link: str, method: str, template: str, subject: str):
    mailer = emails.NewEmail(settings.MAILER_API_KEY)

    mail_body = {}
    mail_from = {"name": "TellMe GmbH", "email": "noreply@tell-me.ch"}
    recipients = [{"name": target_name, "email": target_email}]

    personalization = [
        {
            "email": target_email,
            "data": {
                "link": link,
                "first_name": target_name,
                "account_name": "tellme",
                "support_email": "support@tell-me.ch",
                "method": method
            }
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_template(template, mail_body)
    mailer.set_personalization(personalization, mail_body)

    mailer.send(mail_body)
