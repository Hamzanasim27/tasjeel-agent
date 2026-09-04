from app.scraper.browser import TasjeelBrowser
from app.scraper.tasjeel import (
    open_dashboard,
    is_logged_in,
    wait_for_login,
    get_course_links,
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

        # Always return to dashboard.
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
        print("OPENING COURSE")
        print("=" * 60)

        print(course["course_url"])

        page.goto(
            course["course_url"],
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(1500)

        print()
        print("=" * 60)
        print("COURSE PAGE")
        print("=" * 60)

        print("URL:", page.url)

        print()
        print("PAGE TEXT:")
        print("-" * 60)

        print(
            page.locator("body").inner_text()
        )

        print()
        print("=" * 60)
        print("TABLE INFORMATION")
        print("=" * 60)

        tables = page.locator("table").all()

        print("Tables found:", len(tables))

        for table_index, table in enumerate(tables):

            print()
            print(
                f"TABLE {table_index + 1}"
            )
            print("-" * 60)

            rows = table.locator("tr").all()

            for row_index, row in enumerate(rows):

                cells = row.locator(
                    "th, td"
                ).all()

                values = [
                    cell.inner_text().strip()
                    for cell in cells
                ]

                print(
                    f"Row {row_index}:",
                    values
                )

        input(
            "\nPress ENTER to close..."
        )

    finally:
        browser.stop()


if __name__ == "__main__":
    main()