import base64
import json
from pathlib import Path

from playwright.sync_api import sync_playwright, BrowserContext

from app.config import settings


class TasjeelBrowser:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context: BrowserContext | None = None

    def _load_auth_state(self):
        """
        Load authentication state.

        Render:
            Uses TASJEEL_AUTH_STATE_B64 environment variable.

        Local:
            Uses data/auth_state.json.
        """

        if settings.tasjeel_auth_state_b64:

            try:
                decoded = base64.b64decode(
                    settings.tasjeel_auth_state_b64
                ).decode("utf-8")

                return json.loads(decoded)

            except Exception as exc:
                raise RuntimeError(
                    f"Invalid TASJEEL_AUTH_STATE_B64: {exc}"
                )

        # Local development fallback
        auth_file = Path("data/auth_state.json")

        if not auth_file.exists():
            raise RuntimeError(
                "Authentication state not found. "
                "Run: python login.py"
            )

        with open(
            auth_file,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    def start(self):

        auth_state = self._load_auth_state()

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=settings.headless
        )

        self.context = self.browser.new_context(
            storage_state=auth_state,
            viewport={
                "width": 1440,
                "height": 900,
            },
        )

        return self.context

    def stop(self):

        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None