from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable



NOTIFICATION_TABLE = "iars_notifications"
NOTIFICATION_READ_TABLE = "iars_notification_reads"
MAX_NOTIFICATION_ROWS = 250


@dataclass(frozen=True)
class NotificationSetupStatus:
    ready: bool
    message: str = ""


def _clean(value: Any, max_len: int = 500) -> str:
    return " ".join(str(value or "").split()).strip()[:max_len]


def _response_rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if isinstance(data, list):
        return [dict(row) for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [dict(data)]
    return []


def notification_user_key(user: Any) -> str:
    """Return the same stable owner identity used by Weekly Itinerary."""
    if not isinstance(user, dict):
        return "unknown-user"
    if str(user.get("role", "")).strip().casefold() == "admin":
        return "admin"
    for field in ("id", "user_id", "sub", "username", "email"):
        value = _clean(user.get(field), 160)
        if value:
            return value.casefold() if field in {"username", "email"} else value
    return "unknown-user"


def notification_user_name(user: Any) -> str:
    if not isinstance(user, dict):
        return "IARS User"
    return _clean(user.get("full_name") or user.get("username") or "IARS User", 160)


def notification_user_aliases(user: Any) -> set[str]:
    """Identity aliases accepted by targeted notifications.

    Gantt assignments are stored by full name while Weekly Itinerary normally
    stores the account/user id.  Matching all stable aliases lets both sources
    arrive live without requiring a page refresh or a lookup table join.
    """
    if not isinstance(user, dict):
        return {"unknown-user"}
    aliases: set[str] = set()
    if str(user.get("role", "")).strip().casefold() == "admin":
        aliases.add("admin")
    for field in ("id", "user_id", "sub", "username", "email", "full_name"):
        value = _clean(user.get(field), 180).casefold()
        if value:
            aliases.add(value)
    aliases.add(notification_user_key(user).casefold())
    return aliases


def notification_setup_status(client: Any) -> NotificationSetupStatus:
    if client is None:
        return NotificationSetupStatus(False, "Supabase is not connected.")
    try:
        client.table(NOTIFICATION_TABLE).select("id").limit(1).execute()
        client.table(NOTIFICATION_READ_TABLE).select("notification_id,read_at,deleted_at").limit(1).execute()
        return NotificationSetupStatus(True, "")
    except Exception as exc:
        return NotificationSetupStatus(
            False,
            "Notification state is not ready. Run SUPABASE_NOTIFICATIONS_V4_5_51.sql in Supabase, then refresh IARS. "
            f"Details: {exc}",
        )


def _existing_event(client: Any, event_key: str) -> dict[str, Any] | None:
    if not event_key:
        return None
    try:
        rows = _response_rows(
            client.table(NOTIFICATION_TABLE)
            .select("*")
            .eq("event_key", event_key)
            .limit(1)
            .execute()
        )
        return rows[0] if rows else None
    except Exception:
        return None


def create_notification(
    client: Any,
    *,
    title: str,
    message: str,
    category: str,
    target_type: str = "all",
    recipient_key: str = "",
    action_page: str = "",
    source_type: str = "",
    source_id: str = "",
    event_key: str = "",
    created_by: str = "",
) -> dict[str, Any] | None:
    """Create an idempotent notification. Notification failure never blocks the source action."""
    if client is None:
        return None
    normalized_target = _clean(target_type, 20).casefold() or "all"
    if normalized_target not in {"all", "user"}:
        normalized_target = "all"
    recipient = _clean(recipient_key, 180)
    if normalized_target == "user" and not recipient:
        return None
    clean_event = _clean(event_key, 240)
    if clean_event:
        existing = _existing_event(client, clean_event)
        if existing:
            return existing
    payload = {
        "event_key": clean_event or None,
        "category": _clean(category, 60) or "Information",
        "title": _clean(title, 180) or "IARS Notification",
        "message": _clean(message, 1200),
        "target_type": normalized_target,
        "recipient_key": recipient if normalized_target == "user" else "",
        "action_page": _clean(action_page, 80),
        "source_type": _clean(source_type, 80),
        "source_id": _clean(source_id, 180),
        "created_by": _clean(created_by, 180),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        rows = _response_rows(client.table(NOTIFICATION_TABLE).insert(payload).execute())
        return rows[0] if rows else payload
    except Exception:
        # A concurrent duplicate event is harmless. Never break the originating workflow.
        if clean_event:
            return _existing_event(client, clean_event)
        return None


def notify_itinerary_status(
    client: Any,
    record: dict[str, Any],
    *,
    status: str,
    admin_name: str,
    remarks: str = "",
) -> dict[str, Any] | None:
    normalized = _clean(status, 30).casefold()
    if normalized not in {"approved", "returned"}:
        return None
    recipient = _clean(record.get("owner_key"), 180)
    if not recipient:
        recipient = _clean(record.get("submitted_by_username"), 180).casefold()
    if not recipient:
        return None
    week_start = _clean(record.get("week_start"), 30)
    week_end = _clean(record.get("week_end"), 30)
    revision = int(record.get("revision_no") or 1)
    record_id = _clean(record.get("id"), 180)
    if normalized == "approved":
        title = "Weekly Itinerary Approved"
        message = f"Your weekly itinerary for {week_start} to {week_end} was approved by {admin_name}."
        category = "Itinerary Approved"
    else:
        title = "Weekly Itinerary for Revision"
        message = f"Your weekly itinerary for {week_start} to {week_end} was returned for revision by {admin_name}."
        clean_remarks = _clean(remarks, 500)
        if clean_remarks:
            message += f" Remarks: {clean_remarks}"
        category = "Itinerary Revision"
    return create_notification(
        client,
        title=title,
        message=message,
        category=category,
        target_type="user",
        recipient_key=recipient,
        action_page="Weekly Itinerary",
        source_type="weekly_itinerary",
        source_id=record_id,
        event_key=(
            f"itinerary:{record_id}:{_clean(record.get('updated_at'), 80)}:{normalized}"
            if _clean(record.get("updated_at"), 80)
            else f"itinerary:{record_id}:rev{revision}:{normalized}"
        ),
        created_by=admin_name,
    )


def notify_gantt_schedule(
    client: Any,
    record: dict[str, Any],
    *,
    stage: str,
    custodian: str,
    audit_task: str,
    actor: str,
) -> dict[str, Any] | None:
    """Notify the assigned auditor immediately when Admin saves a Gantt month.

    ``source_id`` is the actual schedule-row id, which is also the deep-link key
    used by Yearly Audit Gantt.  The recipient is the assigned auditor full name;
    ``notification_user_aliases`` resolves that safely against the signed-in user.
    """
    recipient = _clean(record.get("auditor_full_name"), 180)
    if not recipient:
        return None
    record_id = _clean(record.get("id"), 180)
    master_id = _clean(record.get("master_id"), 180)
    year = _clean(record.get("schedule_year"), 10)
    month = _clean(record.get("schedule_month"), 2)
    updated_at = _clean(record.get("updated_at"), 80)
    clean_stage = _clean(stage, 80) or "Scheduled"
    clean_custodian = _clean(custodian, 180) or "Custodian"
    clean_task = _clean(audit_task, 240) or "Audit task"
    month_label = month
    try:
        from calendar import month_name
        month_label = month_name[int(month)] or month
    except Exception:
        pass
    message = (
        f"Your {month_label} {year} audit schedule for {clean_custodian} — "
        f"{clean_task} was updated to {clean_stage} by {actor}."
    )
    source_id = record_id or f"{master_id}:{year}:{month}"
    event_token = updated_at or datetime.now(timezone.utc).isoformat()
    return create_notification(
        client,
        title="Audit Schedule Updated",
        message=message,
        category="Yearly Audit Gantt",
        target_type="user",
        recipient_key=recipient,
        action_page="Yearly Audit Gantt",
        source_type="gantt_schedule",
        source_id=source_id,
        event_key=f"gantt:{source_id}:{event_token}",
        created_by=actor,
    )


def notify_new_policy(
    client: Any,
    record: dict[str, Any],
    *,
    uploaded_by: str,
) -> dict[str, Any] | None:
    record_id = _clean(record.get("id"), 180)
    title_value = _clean(record.get("title") or record.get("original_filename"), 180)
    category_value = _clean(record.get("category"), 80) or "Policy / Memorandum"
    folder_value = _clean(record.get("folder_name"), 160)
    message = f"A new {category_value} was added: {title_value}."
    if folder_value:
        message += f" Folder: {folder_value}."
    return create_notification(
        client,
        title="New Policy / Memorandum",
        message=message,
        category="Policy / Memorandum",
        target_type="all",
        action_page="Policies & Memoranda",
        source_type="document_library",
        source_id=record_id,
        event_key=f"policy:{record_id}" if record_id else f"policy:{title_value}:{folder_value}",
        created_by=uploaded_by,
    )


def create_announcement(
    client: Any,
    *,
    title: str,
    message: str,
    created_by: str,
    recipient_key: str = "",
) -> dict[str, Any] | None:
    recipient = _clean(recipient_key, 180)
    return create_notification(
        client,
        title=title,
        message=message,
        category="Information",
        target_type="user" if recipient else "all",
        recipient_key=recipient,
        action_page="Dashboard",
        source_type="announcement",
        source_id="",
        event_key="",
        created_by=created_by,
    )


def list_user_notifications(client: Any, user: dict[str, Any], *, limit: int = 80) -> list[dict[str, Any]]:
    if client is None:
        return []
    user_key = notification_user_key(user)
    try:
        rows = _response_rows(
            client.table(NOTIFICATION_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .limit(MAX_NOTIFICATION_ROWS)
            .execute()
        )
    except Exception:
        return []
    aliases = notification_user_aliases(user)
    eligible = [
        row for row in rows
        if _clean(row.get("target_type"), 20).casefold() == "all"
        or (
            _clean(row.get("target_type"), 20).casefold() == "user"
            and _clean(row.get("recipient_key"), 180).casefold() in aliases
        )
    ]
    ids = [_clean(row.get("id"), 180) for row in eligible if _clean(row.get("id"), 180)]
    read_ids: set[str] = set()
    deleted_ids: set[str] = set()
    if ids:
        try:
            read_rows = _response_rows(
                client.table(NOTIFICATION_READ_TABLE)
                .select("notification_id,read_at,deleted_at")
                .eq("user_key", user_key)
                .in_("notification_id", ids)
                .execute()
            )
            read_ids = {
                _clean(row.get("notification_id"), 180)
                for row in read_rows if row.get("read_at")
            }
            deleted_ids = {
                _clean(row.get("notification_id"), 180)
                for row in read_rows if row.get("deleted_at")
            }
        except Exception:
            read_ids = set()
            deleted_ids = set()
    visible = [row for row in eligible if _clean(row.get("id"), 180) not in deleted_ids]
    visible = visible[: max(1, int(limit))]
    return [{**row, "is_read": _clean(row.get("id"), 180) in read_ids} for row in visible]


def unread_notification_count(notifications: Iterable[dict[str, Any]]) -> int:
    return sum(1 for row in notifications if not bool(row.get("is_read")))


def mark_notification_read(client: Any, notification_id: str, user: dict[str, Any]) -> None:
    notification_id = _clean(notification_id, 180)
    if not notification_id:
        return
    payload = {
        "notification_id": notification_id,
        "user_key": notification_user_key(user),
        "read_at": datetime.now(timezone.utc).isoformat(),
    }
    client.table(NOTIFICATION_READ_TABLE).upsert(
        payload,
        on_conflict="notification_id,user_key",
    ).execute()


def dismiss_notification(client: Any, notification_id: str, user: dict[str, Any]) -> None:
    """Delete a notification from one user's inbox without deleting broadcasts globally."""
    notification_id = _clean(notification_id, 180)
    if not notification_id:
        return
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "notification_id": notification_id,
        "user_key": notification_user_key(user),
        "read_at": now,
        "deleted_at": now,
    }
    client.table(NOTIFICATION_READ_TABLE).upsert(
        payload,
        on_conflict="notification_id,user_key",
    ).execute()


def mark_all_notifications_read(client: Any, notifications: Iterable[dict[str, Any]], user: dict[str, Any]) -> int:
    user_key = notification_user_key(user)
    now = datetime.now(timezone.utc).isoformat()
    payloads = [
        {"notification_id": _clean(row.get("id"), 180), "user_key": user_key, "read_at": now}
        for row in notifications
        if _clean(row.get("id"), 180) and not bool(row.get("is_read"))
    ]
    if not payloads:
        return 0
    client.table(NOTIFICATION_READ_TABLE).upsert(
        payloads,
        on_conflict="notification_id,user_key",
    ).execute()
    return len(payloads)


def list_active_notification_users(client: Any, users_table: str, admin_user: dict[str, Any]) -> list[dict[str, str]]:
    users: list[dict[str, str]] = [
        {
            "key": "admin",
            "name": notification_user_name(admin_user),
            "username": _clean(admin_user.get("username"), 80),
        }
    ]
    try:
        rows = _response_rows(
            client.table(users_table)
            .select("id,username,full_name,status")
            .eq("status", "Active")
            .order("full_name")
            .execute()
        )
    except Exception:
        rows = []
    for row in rows:
        key = _clean(row.get("id"), 180) or _clean(row.get("username"), 180).casefold()
        if not key:
            continue
        users.append(
            {
                "key": key,
                "name": _clean(row.get("full_name") or row.get("username"), 160),
                "username": _clean(row.get("username"), 80),
            }
        )
    deduped: dict[str, dict[str, str]] = {}
    for row in users:
        deduped[row["key"]] = row
    return list(deduped.values())
