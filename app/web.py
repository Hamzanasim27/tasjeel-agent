from fastapi import FastAPI, Header, HTTPException

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

    browser = TasjeelBrowser()

    try:
        print("=" * 60)
        print("STARTING TASJEEL CHECK")
        print("=" * 60)

        context = browser.start()

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        open_dashboard(page)

        if not is_logged_in(page):
            return {
                "status": "login_required",
                "message": "Tasjeel/Microsoft login session is not available",
                "url": page.url,
            }

        page.goto(
            settings.tasjeel_dashboard_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(1500)

        print("Dashboard:", page.url)

        courses = get_course_links(page)

        if not courses:
            return {
                "status": "success",
                "courses_scanned": 0,
                "new_items": 0,
            }

        print(f"Found {len(courses)} course(s).")

        total_new = 0

        for course in courses:

            print(
                f"Reading course: {course['course_name']}"
            )

            course = extract_course_information(
                page,
                course,
            )

            total_new += scan_course(
                page,
                course,
            )

        return {
            "status": "success",
            "courses_scanned": len(courses),
            "new_items": total_new,
        }

    except Exception as e:

        print("SCAN ERROR:", e)

        return {
            "status": "error",
            "message": str(e),
        }

    finally:
        browser.stop()
        print("Browser closed.")