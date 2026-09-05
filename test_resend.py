from app.services.email_service import send_email


send_email(
    subject="Tasjeel Agent - Resend Test",
    body="""Hello Hamza,

This is a test email from the Tasjeel Student Agent.

The Render-compatible email system is working.

Tasjeel Agent
""",
)