import re
from urllib.parse import urljoin

from playwright.sync_api import Page

from app.config import settings


BASE_URL = "https://tasjeel.cust.edu.pk"


def clean_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text or ""
    ).strip()


def open_dashboard(page: Page):

    print("Opening Tasjeel...")

    page.goto(
        settings.tasjeel_dashboard_url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(2000)


def is_logged_in(page: Page) -> bool:

    url = page.url.lower()

    if "web/login" in url:
        return False

    if "/student/" in url:
        return True

    return False


def wait_for_login(page: Page):

    print()
    print("=" * 60)
    print("TASJEEL LOGIN")
    print("=" * 60)
    print()
    print("If Tasjeel asks you to log in:")
    print("1. Log in normally.")
    print("2. Complete Microsoft authentication if required.")
    print("3. Return to the Tasjeel dashboard.")
    print()
    print("Waiting for dashboard...")
    print()

    page.wait_for_url(
        re.compile(r".*/student/.*"),
        timeout=300000,
    )

    page.wait_for_timeout(2000)

    print("Login successful!")
    print("Current URL:", page.url)


def get_course_links(page: Page) -> list[dict]:

    print()
    print("Searching for courses...")

    courses = {}

    links = page.locator(
        'a[href*="/student/course/info/"]'
    ).all()

    for link in links:

        href = link.get_attribute("href")

        if not href:
            continue

        full_url = urljoin(
            BASE_URL,
            href
        )

        match = re.search(
            r"/student/course/info/([^/?#]+)",
            full_url
        )

        if not match:
            continue

        external_id = match.group(1)

        text = clean_text(
            link.inner_text()
        )

        if external_id not in courses:

            courses[external_id] = {
                "external_id": external_id,
                "course_name": text,
                "course_code": "",
                "course_url": full_url,
            }

    result = list(courses.values())

    print(
        f"Found {len(result)} course link(s)."
    )

    for course in result:
        print(
            f"  - {course['course_name']}"
            f" | {course['course_url']}"
        )

    return result


def get_current_page_text(page: Page) -> str:

    return clean_text(
        page.locator("body").inner_text()
    )


def extract_course_information(page: Page, course: dict) -> dict:
    page.goto(
        course["course_url"],
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(1000)

    body = clean_text(
        page.locator("body").inner_text()
    )

    # Look specifically for the course heading/code pattern.
    pattern = r"\b([A-Z][A-Z0-9 &/'-]{2,})\s*\(([A-Z]{2,}\d{2,}-[^)]*)\)"

    match = re.search(pattern, body)

    if match:
        course["course_name"] = clean_text(
            match.group(1)
        )
        course["course_code"] = clean_text(
            match.group(2)
        )

    return course

def get_announcement_items(page: Page, course: dict) -> list[dict]:
    """
    Scrape Announcement/News from a Tasjeel course page.
    """

    page.goto(
        course["course_url"],
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(1000)

    items = []

    tables = page.locator("table").all()

    if not tables:
        print("No announcement table found.")
        return items

    # Announcement table is currently the first/only table
    table = tables[0]

    rows = table.locator("tbody tr").all()

    for index, row in enumerate(rows):

        cells = row.locator("td").all()

        if not cells:
            continue

        values = [
            clean_text(cell.inner_text())
            for cell in cells
        ]

        # Tasjeel displays this when there are no announcements.
        if len(values) == 1 and "No Announcement" in values[0]:
            continue

        if len(values) < 4:
            continue

        # Expected structure:
        # Sr No. | Subject | Date | Description | Attachment

        subject = values[1]
        posted_date = values[2]
        description = values[3]

        attachment_url = None

        links = row.locator("a").all()

        for link in links:
            href = link.get_attribute("href")

            if href:
                attachment_url = urljoin(
                    BASE_URL,
                    href,
                )
                break

        items.append({
            "external_id": (
                f"{course['external_id']}"
                f"-announcement-{index}"
            ),
            "item_type": "announcement",
            "title": subject,
            "description": description,
            "posted_date": posted_date,
            "start_date": None,
            "due_date": None,
            "attachment_url": attachment_url,
            "source_url": course["course_url"],
        })

    return items

def get_material_items(page: Page, course: dict) -> list[dict]:
    """
    Scrape Course Material from Tasjeel.
    """

    material_url = (
        f"{BASE_URL}/student/course/material/"
        f"{course['external_id']}"
    )

    page.goto(
        material_url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(1000)

    items = []

    tables = page.locator("table").all()

    if not tables:
        print("No course material table found.")
        return items

    table = tables[0]

    rows = table.locator("tbody tr").all()

    for index, row in enumerate(rows):

        cells = row.locator("td").all()

        if not cells:
            continue

        values = [
            clean_text(cell.inner_text())
            for cell in cells
        ]

        if not any(values):
            continue

        # Skip "No Material" type rows if Tasjeel displays one.
        if len(values) == 1:
            if "No Material" in values[0]:
                continue

            if "No Course Material" in values[0]:
                continue

        if len(values) < 3:
            continue

        # Expected:
        # Sr No. | Course Material File | Description | Download

        title = values[1]
        description = values[2]

        attachment_url = None

        links = row.locator("a").all()

        for link in links:

            href = link.get_attribute("href")

            if href:
                attachment_url = urljoin(
                    BASE_URL,
                    href,
                )
                break

        items.append({
            "external_id": (
                f"{course['external_id']}"
                f"-material-{index}"
            ),
            "item_type": "material",
            "title": title,
            "description": description,
            "posted_date": None,
            "start_date": None,
            "due_date": None,
            "attachment_url": attachment_url,
            "source_url": material_url,
        })

    return items

def get_submission_items(page: Page, course: dict) -> list[dict]:
    """
    Scrape Submission/Tasks from Tasjeel.
    """

    submission_url = (
        f"{BASE_URL}/student/course/submission/"
        f"{course['external_id']}"
    )

    page.goto(
        submission_url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(1000)

    items = []

    tables = page.locator("table").all()

    if not tables:
        print("No submission table found.")
        return items

    table = tables[0]

    rows = table.locator("tbody tr").all()

    for index, row in enumerate(rows):

        cells = row.locator("td").all()

        if not cells:
            continue

        values = [
            clean_text(cell.inner_text())
            for cell in cells
        ]

        if not any(values):
            continue

        # Tasjeel may display a message when there are
        # no submissions/tasks.
        if len(values) == 1:

            no_submission_text = values[0].lower()

            if (
                "no submission" in no_submission_text
                or "no task" in no_submission_text
                or "no record" in no_submission_text
            ):
                continue

        # Expected structure:
        #
        # Sr No.
        # Name
        # Description
        # Start Date
        # Due Date
        # Attachment
        # Action

        if len(values) < 5:
            continue

        title = values[1]
        description = values[2]
        start_date = values[3]
        due_date = values[4]

        attachment_url = None

        links = row.locator("a").all()

        for link in links:

            href = link.get_attribute("href")

            if href:
                attachment_url = urljoin(
                    BASE_URL,
                    href,
                )
                break

        items.append({
            "external_id": (
                f"{course['external_id']}"
                f"-submission-{index}"
            ),
            "item_type": "submission",
            "title": title,
            "description": description,
            "posted_date": None,
            "start_date": start_date,
            "due_date": due_date,
            "attachment_url": attachment_url,
            "source_url": submission_url,
        })

    return items