import time

from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import settings
from app.scraper.browser import TasjeelBrowser
from app.scraper.tasjeel import (
    open_dashboard,
    is_logged_in,
    wait_for_login,
    get_course_links,
    extract_course_information,
)
from app.services.monitor import scan_course


def run_scan(browser):
    print()
    print("=" * 60)
    print("STARTING TASJEEL SCAN")
    print("=" * 60)

    context = browser.context

    if not context:
        print("Browser context is not available.")
        return

    page = context.pages[0] if context.pages else context.new_page()

    try:
        open_dashboard(page)

        if not is_logged_in(page):
            print("Tasjeel login required.")
            wait_for_login(page)

        page.goto(
            settings.tasjeel_dashboard_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(1500)

        print()
        print("Dashboard:", page.url)

        print()
        print("Searching for courses...")

        courses = get_course_links(page)

        if not courses:
            print("No course links were detected.")
            return

        print(f"Found {len(courses)} course link(s).")

        total_new = 0

        for course in courses:

            print()
            print(f"Reading course: {course['course_name']}")

            course = extract_course_information(
                page,
                course,
            )

            new_items = scan_course(
                page,
                course,
            )

            total_new += new_items

        print()
        print("=" * 60)
        print("SCAN COMPLETE")
        print("=" * 60)
        print(f"Courses scanned: {len(courses)}")
        print(f"New items detected: {total_new}")

    except Exception as e:
        print()
        print("=" * 60)
        print("SCAN ERROR")
        print("=" * 60)
        print(e)


def main():

    print("=" * 60)
    print("        TASJEEL STUDENT AGENT")
    print("=" * 60)

    browser = TasjeelBrowser()

    try:
        browser.start()

        # First scan immediately
        run_scan(browser)

        # Create scheduler
        scheduler = BlockingScheduler()

        scheduler.add_job(
            lambda: run_scan(browser),
            "interval",
            minutes=settings.check_interval_minutes,
            id="tasjeel_scan",
            replace_existing=True,
        )

        print()
        print("=" * 60)
        print("AUTOMATIC MONITORING ENABLED")
        print("=" * 60)
        print(
            f"Next scan interval: "
            f"{settings.check_interval_minutes} minutes"
        )
        print("That's every 4 hours.")
        print("Keep this program running.")
        print("Press Ctrl+C to stop.")
        print("=" * 60)

        scheduler.start()

    except KeyboardInterrupt:

        print()
        print("Tasjeel Agent stopped.")

    finally:

        browser.stop()


if __name__ == "__main__":
    main()