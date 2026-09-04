from app.services.email_service import send_email


send_email(
    subject="Tasjeel Agent Test",
    body="""Hello!

This is a test email from the Tasjeel Student Agent.

If you received this email, the email notification system is working correctly.

Tasjeel Agent
""",
)