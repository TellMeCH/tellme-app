from django.conf import settings
from mailersend import emails


def send_email_with_link(target_name: str, target_email: str, link: str, method: str):
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
    mailer.set_subject("Welcome to tellme", mail_body)
    mailer.set_template("0r83ql3qv6x4zw1j", mail_body)
    mailer.set_personalization(personalization, mail_body)

    mailer.send(mail_body)
