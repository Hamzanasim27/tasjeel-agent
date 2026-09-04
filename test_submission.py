from app.scraper.browser import TasjeelBrowser

from app.scraper.tasjeel import (
    open_dashboard,
    is_logged_in,
    wait_for_login,
    get_course_links,
    get_submission_items,
)


def main():

    browser = TasjeelBrowser()

    try:

        context = browser.start()

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        open_dashboard(page)

        if not is_logged_in(page):
            wait_for_login(page)

        page.goto(
            "https://tasjeel.cust.edu.pk/student/dashboard",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(1500)

        courses = get_course_links(page)

        if not courses:

            print("No courses found.")
            return

        course = courses[0]

        print()
        print("=" * 60)
        print("SUBMISSIONS / TASKS")
        print("=" * 60)

        print(
            "Course:",
            course["course_name"]
        )

        print()

        items = get_submission_items(
            page,
            course,
        )

        print(
            f"Found {len(items)} submission/task(s)."
        )

        print()

        for item in items:

            print("-" * 60)

            print(
                "Title:",
                item["title"]
            )

            print(
                "Description:",
                item["description"]
            )

            print(
                "Start Date:",
                item["start_date"]
            )

            print(
                "Due Date:",
                item["due_date"]
            )

            print(
                "Attachment:",
                item["attachment_url"]
            )

            print(
                "Source:",
                item["source_url"]
            )

        print()
        print("=" * 60)

        input(
            "Press ENTER to close..."
        )

    finally:

        browser.stop()


if __name__ == "__main__":
    main()