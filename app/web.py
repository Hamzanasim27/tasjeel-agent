from fastapi import FastAPI, Header, HTTPException
from fastapi.background import BackgroundTasks

from app.config import settings
from app.scraper.browser import TasjeelBrowser
from app.scraper.tasjeel import (
    open_dashboard,
    is_logged_in,
    get_course_links,
    extract_course_information,
)
from app.services.monitor import scan_course


app = FastAPI(title="Tasjeel Student Agent")


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Tasjeel Student Agent",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


def run_tasjeel_scan():
    """
    Actual long-running Tasjeel scan.
    This runs after /trigger returns.
    """

    browser = TasjeelBrowser()

    try:
        print("=" * 60)
        print("STARTING TASJEEL BACKGROUND SCAN")
        print("=" * 60)

        context = browser.start()

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        open_dashboard(page)

        if not is_logged_in(page):
            print("Tasjeel authentication expired.")

            return

        page.goto(
            settings.tasjeel_dashboard_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(1500)

        courses = get_course_links(page)

        if not courses:
            print("No courses found.")
            return

        print(
            f"Found {len(courses)} course(s)."
        )

        total_new = 0

        for course in courses:

            print(
                f"Reading course: "
                f"{course['course_name']}"
            )

            course = extract_course_information(
                page,
                course,
            )

            total_new += scan_course(
                page,
                course,
            )

        print("=" * 60)
        print("BACKGROUND SCAN COMPLETE")
        print(f"Courses scanned: {len(courses)}")
        print(f"New items: {total_new}")
        print("=" * 60)

    except Exception as exc:

        print("=" * 60)
        print("BACKGROUND SCAN ERROR")
        print(exc)
        print("=" * 60)

    finally:

        browser.stop()

        print("Browser closed.")


@app.get("/check")
def check_tasjeel(
    x_cron_secret: str = Header(default="")
):

    if not settings.check_token:
        raise HTTPException(
            status_code=500,
            detail="CHECK_TOKEN is not configured",
        )

    if x_cron_secret != settings.check_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    # Perform scan immediately.
    # This route is useful for manual testing.
    run_tasjeel_scan()

    return {
        "status": "success",
        "message": "Scan completed",
    }


@app.get("/trigger")
def trigger_tasjeel(
    background_tasks: BackgroundTasks,
    x_cron_secret: str = Header(default="")
):

    if not settings.check_token:
        raise HTTPException(
            status_code=500,
            detail="CHECK_TOKEN is not configured",
        )

    if x_cron_secret != settings.check_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    background_tasks.add_task(
        run_tasjeel_scan
    )

    return {
        "status": "accepted",
        "message": "Tasjeel scan started",
    }