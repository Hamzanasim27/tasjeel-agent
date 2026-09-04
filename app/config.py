import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    tasjeel_dashboard_url: str = os.getenv(
        "TASJEEL_DASHBOARD_URL",
        "https://tasjeel.cust.edu.pk/student/dashboard",
    )

    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    check_interval_minutes: int = int(
        os.getenv("CHECK_INTERVAL_MINUTES", "15")
    )

    headless: bool = (
        os.getenv("HEADLESS", "false").lower() == "true"
    )

    browser_profile_dir: str = os.getenv(
        "BROWSER_PROFILE_DIR",
        "./data/browser_profile",
    )

    email_sender: str = os.getenv("EMAIL_SENDER", "")
    email_app_password: str = os.getenv("EMAIL_APP_PASSWORD", "")
    email_recipient: str = os.getenv("EMAIL_RECIPIENT", "")


settings = Settings()