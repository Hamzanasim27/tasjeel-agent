from supabase import create_client, Client

from app.config import settings


_client = None


def get_client() -> Client:
    global _client

    if _client is None:

        if not settings.supabase_url:
            raise RuntimeError(
                "SUPABASE_URL is missing from .env"
            )

        if not settings.supabase_key:
            raise RuntimeError(
                "SUPABASE_KEY is missing from .env"
            )

        _client = create_client(
            settings.supabase_url,
            settings.supabase_key,
        )

    return _client


def get_or_create_course(course: dict) -> dict:

    client = get_client()

    result = (
        client
        .table("courses")
        .upsert(
            course,
            on_conflict="external_id"
        )
        .execute()
    )

    if not result.data:
        raise RuntimeError(
            f"Could not save course: {course}"
        )

    return result.data[0]


def item_exists(content_hash: str) -> bool:

    client = get_client()

    result = (
        client
        .table("tasjeel_items")
        .select("id")
        .eq("content_hash", content_hash)
        .limit(1)
        .execute()
    )

    return bool(result.data)


def save_item(item: dict) -> dict:

    client = get_client()

    result = (
        client
        .table("tasjeel_items")
        .insert(item)
        .execute()
    )

    if not result.data:
        raise RuntimeError(
            f"Could not save item: {item}"
        )

    return result.data[0]


def mark_notified(item_id: int):

    client = get_client()

    (
        client
        .table("tasjeel_items")
        .update({
            "notified": True
        })
        .eq("id", item_id)
        .execute()
    )