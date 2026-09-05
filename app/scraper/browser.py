from pathlib import Path

from playwright.sync_api import sync_playwright, BrowserContext

from app.config import settings


class TasjeelBrowser:

    def __init__(self):
        self.playwright = None
        self.context: BrowserContext | None = None

    def start(self):

        profile = Path(settings.browser_profile_dir)
        profile.mkdir(parents=True, exist_ok=True)

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile),
            headless=settings.headless,
            viewport={"width": 1440, "height": 900},
        )

        return self.context

    def stop(self):

        if self.context:
            self.context.close()
            self.context = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None