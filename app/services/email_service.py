import resend

from app.config import settings


def send_email(
    subject: str,
    body: str,
):
    if not settings.resend_api_key:
        raise RuntimeError(
            "RESEND_API_KEY is missing from environment variables."
        )

    if not settings.email_recipient:
        raise RuntimeError(
            "EMAIL_RECIPIENT is missing from environment variables."
        )

    if not settings.email_from:
        raise RuntimeError(
            "EMAIL_FROM is missing from environment variables."
        )

    resend.api_key = settings.resend_api_key

    params = {
        "from": settings.email_from,
        "to": [settings.email_recipient],
        "subject": subject,
        "text": body,
    }

    response = resend.Emails.send(params)

    print(
        f"  EMAIL SENT VIA RESEND: {subject}"
    )

    return response