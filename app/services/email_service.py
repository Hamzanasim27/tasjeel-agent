import smtplib
from email.message import EmailMessage

from app.config import settings


def send_email(
    subject: str,
    body: str,
):
    sender = settings.email_sender
    app_password = settings.email_app_password
    recipient = settings.email_recipient

    if not sender:
        raise RuntimeError("EMAIL_SENDER is missing from .env")

    if not app_password:
        raise RuntimeError("EMAIL_APP_PASSWORD is missing from .env")

    if not recipient:
        raise RuntimeError("EMAIL_RECIPIENT is missing from .env")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(message)

    print(f"  EMAIL SENT: {subject}")