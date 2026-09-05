import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Tasjeel
    tasjeel_dashboard_url: str = os.getenv(
        "TASJEEL_DASHBOARD_URL",
        "https://tasjeel.cust.edu.pk/student/dashboard",
    )

    # Supabase
    supabase_url: str = os.getenv(
        "SUPABASE_URL",
        "",
    )

    supabase_key: str = os.getenv(
        "SUPABASE_KEY",
        "",
    )

    # Scheduler
    check_interval_minutes: int = int(
        os.getenv(
            "CHECK_INTERVAL_MINUTES",
            "240",
        )
    )

    # Playwright
    headless: bool = (
        os.getenv(
            "HEADLESS",
            "false",
        ).lower()
        == "true"
    )

    browser_profile_dir: str = os.getenv(
        "BROWSER_PROFILE_DIR",
        "./data/browser_profile",
    )

    # Tasjeel authentication
    tasjeel_auth_state_b64: str = os.getenv(
        "TASJEEL_AUTH_STATE_B64",
        "",
    )

    # Cron security
    check_token: str = os.getenv(
        "CHECK_TOKEN",
        "",
    )

    # Resend
    resend_api_key: str = os.getenv(
        "RESEND_API_KEY",
        "",
    )

    email_from: str = os.getenv(
        "EMAIL_FROM",
        "onboarding@resend.dev",
    )

    email_recipient: str = os.getenv(
        "EMAIL_RECIPIENT",
        "",
    )

    # Old Gmail settings kept temporarily
    # They are no longer used by Resend.
    email_sender: str = os.getenv(
        "EMAIL_SENDER",
        "",
    )

    email_app_password: str = os.getenv(
        "EMAIL_APP_PASSWORD",
        "",
    )


settings = Settings()