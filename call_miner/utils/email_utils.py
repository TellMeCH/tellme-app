from django.conf import settings
from mailersend import emails


def send_email_with_link(target_name: str, target_email: str, link: str):
    mailer = emails.NewEmail(settings.MAILER_API_KEY)

    mail_body = {}
    mail_from = {
        "name": "TellMe GmbH",
        "email": "noreply@tell-me.ch",
    }
    recipients = [{"name": target_name, "email": target_email}]

    reply_to = {
        "name": "Support",
        "email": "support@tell-me.ch",
    }

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Welcome to TellMe", mail_body)
    mailer.set_html_content(f"This is your link: {link}", mail_body)
    mailer.set_reply_to(reply_to, mail_body)

    mailer.send(mail_body)