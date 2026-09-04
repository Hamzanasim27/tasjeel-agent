import hashlib
import json

from app.database.supabase import (
    get_or_create_course,
    item_exists,
    save_item,
    mark_notified,
)

from app.scraper.tasjeel import (
    get_announcement_items,
    get_material_items,
    get_submission_items,
)

from app.services.email_service import send_email


def generate_content_hash(item: dict) -> str:
    content = {
        "item_type": item.get("item_type"),
        "title": item.get("title"),
        "description": item.get("description"),
        "posted_date": item.get("posted_date"),
        "start_date": item.get("start_date"),
        "due_date": item.get("due_date"),
        "attachment_url": item.get("attachment_url"),
        "source_url": item.get("source_url"),
    }

    normalized = json.dumps(
        content,
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def build_email(item: dict, course: dict):
    item_type = item.get("item_type", "").replace("_", " ").title()

    subject = f"🔔 New Tasjeel {item_type}: {item.get('title', 'Update')}"

    body = f"""
New Tasjeel Update
==================

Course:
{course.get('course_name', 'Unknown Course')}

Course Code:
{course.get('course_code', 'N/A')}

Type:
{item_type}

Title:
{item.get('title', 'N/A')}

Description:
{item.get('description') or 'No description provided.'}
"""

    if item.get("posted_date"):
        body += f"""
Posted Date:
{item['posted_date']}
"""

    if item.get("start_date"):
        body += f"""
Start Date:
{item['start_date']}
"""

    if item.get("due_date"):
        body += f"""
Due Date:
{item['due_date']}
"""

    if item.get("attachment_url"):
        body += f"""
Attachment:
{item['attachment_url']}
"""

    body += f"""
Tasjeel Page:
{item.get('source_url', course.get('course_url', ''))}

==================
Tasjeel Student Agent
"""

    return subject, body


def process_items(course: dict, items: list[dict]) -> int:
    if not items:
        return 0

    saved_count = 0

    saved_course = get_or_create_course(course)
    course_id = saved_course["id"]

    for item in items:

        content_hash = generate_content_hash(item)

        if item_exists(content_hash):
            print(
                f"  EXISTING: "
                f"{item['item_type']} - {item['title']}"
            )
            continue

        database_item = {
            "course_id": course_id,
            "external_id": item.get("external_id"),
            "item_type": item.get("item_type"),
            "title": item.get("title"),
            "description": item.get("description"),
            "posted_date": item.get("posted_date"),
            "start_date": item.get("start_date"),
            "due_date": item.get("due_date"),
            "attachment_url": item.get("attachment_url"),
            "source_url": item.get("source_url"),
            "content_hash": content_hash,
            "notified": False,
        }

        saved = save_item(database_item)

        print(
            f"  NEW: "
            f"{saved['item_type']} - {saved['title']}"
        )

        # Send notification email
        try:
            subject, body = build_email(item, course)

            send_email(
                subject=subject,
                body=body,
            )

            mark_notified(saved["id"])

            print("  NOTIFICATION: Sent successfully")

        except Exception as e:
            print(f"  EMAIL ERROR: {e}")

        saved_count += 1

    return saved_count


def scan_course(page, course: dict) -> int:

    print()
    print("=" * 60)
    print(f"Scanning: {course['course_name']}")
    print("=" * 60)

    total_new = 0

    print()
    print("Checking Announcement/News...")

    announcements = get_announcement_items(
        page,
        course,
    )

    print(
        f"Found {len(announcements)} announcement(s)."
    )

    total_new += process_items(
        course,
        announcements,
    )

    print()
    print("Checking Course Material...")

    materials = get_material_items(
        page,
        course,
    )

    print(
        f"Found {len(materials)} material item(s)."
    )

    total_new += process_items(
        course,
        materials,
    )

    print()
    print("Checking Submission...")

    submissions = get_submission_items(
        page,
        course,
    )

    print(
        f"Found {len(submissions)} submission/task(s)."
    )

    total_new += process_items(
        course,
        submissions,
    )

    return total_new