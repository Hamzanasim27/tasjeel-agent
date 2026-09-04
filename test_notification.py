from app.services.monitor import process_items


test_course = {
    "external_id": "TEST-COURSE",
    "course_name": "Test Course",
    "course_code": "TEST101",
    "course_url": "https://tasjeel.cust.edu.pk/student/dashboard",
}

test_item = {
    "external_id": "TEST-ITEM-001",
    "item_type": "announcement",
    "title": "Test Tasjeel Announcement",
    "description": "This is a test notification from the Tasjeel Agent.",
    "posted_date": "04-09-2026",
    "start_date": None,
    "due_date": None,
    "attachment_url": None,
    "source_url": "https://tasjeel.cust.edu.pk/student/dashboard",
}


process_items(test_course, [test_item])