from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
from typing import Any, Iterable
from uuid import uuid4

import pandas as pd
import streamlit as st


DEFAULT_BUCKET = "iars-weekly-itineraries"
DEFAULT_TABLE = "weekly_itineraries"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
}
VALID_STATUSES = {"pending", "approved", "returned"}


class WeeklyItineraryError(RuntimeError):
    """Base exception for Weekly Itinerary operations."""


class DuplicateWeeklyItineraryError(WeeklyItineraryError):
    """Raised when a user already has a non-returned itinerary for the week."""


@dataclass(frozen=True)
class WeeklyItineraryConfig:
    bucket: str = DEFAULT_BUCKET
    table: str = DEFAULT_TABLE
    max_image_bytes: int = MAX_IMAGE_BYTES


def _response_data(response: Any) -> list[dict[str, Any]]:
    if response is None:
        return []
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if not data:
        return []
    return [dict(row) for row in data]


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def _safe_segment(value: Any, fallback: str = "user") -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", _clean(value))
    text = re.sub(r"_+", "_", text).strip("._-")
    return text[:100] or fallback


def current_user_key(user: dict[str, Any]) -> str:
    """Return a stable private owner key for the signed-in IARS user."""
    if str(user.get("role", "")).strip().casefold() == "admin":
        return "admin"
    for field in ("id", "user_id", "sub", "username", "email"):
        value = _clean(user.get(field))
        if value:
            return value
    return "unknown-user"


def current_user_name(user: dict[str, Any]) -> str:
    return _clean(user.get("full_name") or user.get("username") or "IARS User")


def current_username(user: dict[str, Any]) -> str:
    return _clean(user.get("username") or user.get("email") or current_user_name(user))


def monday_for(value: date | None = None) -> date:
    value = value or date.today()
    return value - timedelta(days=value.weekday())


def friday_for(value: date | None = None) -> date:
    return monday_for(value) + timedelta(days=4)


def format_week(record: dict[str, Any]) -> str:
    start = _clean(record.get("week_start"))
    end = _clean(record.get("week_end"))
    try:
        start_date = date.fromisoformat(start[:10])
        end_date = date.fromisoformat(end[:10])
        if start_date.year == end_date.year:
            return f"{start_date.strftime('%B')} {start_date.day} – {end_date.day}, {end_date.year}"
        return (
            f"{start_date.strftime('%B')} {start_date.day}, {start_date.year} – "
            f"{end_date.strftime('%B')} {end_date.day}, {end_date.year}"
        )
    except Exception:
        return f"{start} to {end}".strip()


def _validate_week(week_start: date, week_end: date) -> None:
    if not isinstance(week_start, date) or not isinstance(week_end, date):
        raise WeeklyItineraryError("Week start and week end are required.")
    if week_end < week_start:
        raise WeeklyItineraryError("Week end cannot be earlier than week start.")
    if (week_end - week_start).days > 13:
        raise WeeklyItineraryError("The selected itinerary period is too long.")


def _validate_image(image_bytes: bytes, filename: str, mime_type: str, max_bytes: int) -> tuple[str, str]:
    if not image_bytes:
        raise WeeklyItineraryError("Select a JPG or PNG itinerary image before submitting.")
    if len(image_bytes) > max_bytes:
        raise WeeklyItineraryError(f"The itinerary image must not exceed {max_bytes // (1024 * 1024)} MB.")

    extension = Path(filename or "").suffix.casefold()
    normalized_mime = _clean(mime_type).casefold()
    allowed_extensions = ALLOWED_IMAGE_TYPES.get(normalized_mime, set())
    if extension not in {".jpg", ".jpeg", ".png"}:
        raise WeeklyItineraryError("Only JPG, JPEG and PNG files are allowed.")
    if allowed_extensions and extension not in allowed_extensions:
        raise WeeklyItineraryError("The file extension does not match the uploaded image type.")

    try:
        from PIL import Image

        with Image.open(BytesIO(image_bytes)) as image:
            detected = str(image.format or "").upper()
            image.verify()
        if detected not in {"JPEG", "PNG"}:
            raise WeeklyItineraryError("The uploaded file is not a valid JPG or PNG image.")
        normalized_mime = "image/jpeg" if detected == "JPEG" else "image/png"
        extension = ".jpg" if detected == "JPEG" else ".png"
    except WeeklyItineraryError:
        raise
    except Exception as exc:
        raise WeeklyItineraryError(f"Unable to validate the itinerary image: {exc}") from exc

    return normalized_mime, extension


def _storage_path(owner_key: str, week_start: date, filename: str, extension: str) -> str:
    user_segment = _safe_segment(owner_key)
    base_name = _safe_segment(Path(filename or "itinerary").stem, "itinerary")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{user_segment}/{week_start.isoformat()}/{timestamp}_{base_name}_{uuid4().hex[:8]}{extension}"


def list_user_itineraries(
    client: Any,
    user: dict[str, Any],
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
    *,
    limit: int = 250,
) -> list[dict[str, Any]]:
    owner_key = current_user_key(user)
    response = (
        client.table(config.table)
        .select("*")
        .eq("owner_key", owner_key)
        .order("week_start", desc=True)
        .order("submitted_at", desc=True)
        .limit(limit)
        .execute()
    )
    return _response_data(response)


def list_all_itineraries(
    client: Any,
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
    *,
    limit: int = 1500,
) -> list[dict[str, Any]]:
    response = (
        client.table(config.table)
        .select("*")
        .order("week_start", desc=True)
        .order("submitted_at", desc=True)
        .limit(limit)
        .execute()
    )
    return _response_data(response)


def find_itinerary_for_week(
    client: Any,
    user: dict[str, Any],
    week_start: date,
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
) -> dict[str, Any] | None:
    response = (
        client.table(config.table)
        .select("*")
        .eq("owner_key", current_user_key(user))
        .eq("week_start", week_start.isoformat())
        .order("revision_no", desc=True)
        .limit(1)
        .execute()
    )
    rows = _response_data(response)
    return rows[0] if rows else None


def submit_weekly_itinerary(
    client: Any,
    user: dict[str, Any],
    *,
    week_start: date,
    week_end: date,
    image_bytes: bytes,
    original_filename: str,
    mime_type: str,
    submitter_remarks: str = "",
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
) -> dict[str, Any]:
    """Create a submission or resubmit a record returned by the administrator."""
    _validate_week(week_start, week_end)
    normalized_mime, extension = _validate_image(
        image_bytes,
        original_filename,
        mime_type,
        config.max_image_bytes,
    )

    existing = find_itinerary_for_week(client, user, week_start, config)
    existing_status = _clean((existing or {}).get("status")).casefold()
    if existing and existing_status != "returned":
        label = existing_status.title() or "Existing"
        raise DuplicateWeeklyItineraryError(
            f"A {label} itinerary already exists for the week starting {week_start.isoformat()}."
        )

    owner_key = current_user_key(user)
    storage_path = _storage_path(owner_key, week_start, original_filename, extension)
    bucket = client.storage.from_(config.bucket)
    try:
        bucket.upload(
            path=storage_path,
            file=image_bytes,
            file_options={
                "content-type": normalized_mime,
                "cache-control": "3600",
                "upsert": "false",
            },
        )
    except Exception as exc:
        raise WeeklyItineraryError(f"Unable to upload the weekly itinerary image: {exc}") from exc

    now = datetime.now(timezone.utc).isoformat()
    base_payload = {
        "owner_key": owner_key,
        "auditor_name": current_user_name(user),
        "submitted_by_username": current_username(user),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "original_filename": Path(original_filename).name,
        "storage_bucket": config.bucket,
        "storage_path": storage_path,
        "mime_type": normalized_mime,
        "file_size": len(image_bytes),
        "sha256": sha256(image_bytes).hexdigest(),
        "status": "pending",
        "submitter_remarks": _clean(submitter_remarks),
        "admin_remarks": "",
        "approved_by": None,
        "approved_at": None,
        "updated_at": now,
    }

    try:
        payload = {
            **base_payload,
            "revision_no": int(existing.get("revision_no") or 1) + 1 if existing else 1,
            "submitted_at": now,
        }
        response = client.table(config.table).insert(payload).execute()
        rows = _response_data(response)
        record = dict(rows[0] if rows else payload)
    except Exception as exc:
        try:
            bucket.remove([storage_path])
        except Exception:
            pass
        raise WeeklyItineraryError(f"The image uploaded, but the itinerary record could not be saved: {exc}") from exc

    return record


def download_itinerary_image(
    client: Any,
    record: dict[str, Any],
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
) -> bytes:
    storage_path = _clean(record.get("storage_path"))
    if not storage_path:
        raise WeeklyItineraryError("The selected itinerary has no storage path.")
    bucket_name = _clean(record.get("storage_bucket")) or config.bucket
    try:
        data = client.storage.from_(bucket_name).download(storage_path)
    except Exception as exc:
        raise WeeklyItineraryError(f"Unable to download the weekly itinerary image: {exc}") from exc
    if isinstance(data, bytes):
        return data
    if hasattr(data, "read"):
        return data.read()
    try:
        return bytes(data)
    except Exception as exc:
        raise WeeklyItineraryError("Supabase returned an unsupported image response.") from exc


def update_itinerary_status(
    client: Any,
    record: dict[str, Any],
    admin_user: dict[str, Any],
    *,
    status: str,
    remarks: str = "",
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
) -> dict[str, Any]:
    normalized_status = _clean(status).casefold()
    if normalized_status not in {"approved", "returned"}:
        raise WeeklyItineraryError("Status must be Approved or Returned.")
    record_id = record.get("id")
    if not record_id:
        raise WeeklyItineraryError("The selected itinerary record is incomplete.")

    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "status": normalized_status,
        "admin_remarks": _clean(remarks),
        "approved_by": current_user_name(admin_user) if normalized_status == "approved" else None,
        "approved_at": now if normalized_status == "approved" else None,
        "updated_at": now,
    }
    response = client.table(config.table).update(payload).eq("id", record_id).execute()
    rows = _response_data(response)
    return dict(rows[0] if rows else {**record, **payload})


def _status_label(status: Any) -> str:
    normalized = _clean(status).casefold()
    return {
        "pending": "Pending Approval",
        "approved": "Approved",
        "returned": "Returned for Revision",
    }.get(normalized, normalized.title() or "Unknown")


def _status_icon(status: Any) -> str:
    normalized = _clean(status).casefold()
    return {"pending": "🟡", "approved": "🟢", "returned": "🔴"}.get(normalized, "⚪")


def _record_label(record: dict[str, Any], index: int = 1, *, include_auditor: bool = False) -> str:
    auditor = f"{_clean(record.get('auditor_name'))} | " if include_auditor else ""
    return (
        f"{auditor}{format_week(record)} | {_status_label(record.get('status'))} | "
        f"Rev. {int(record.get('revision_no') or 1)} | {index}"
    )


def _itinerary_image_width(
    image_bytes: bytes,
    *,
    max_width: int,
    max_height: int,
) -> int:
    """Return a readable width that keeps the image inside the viewport."""
    try:
        from PIL import Image

        with Image.open(BytesIO(image_bytes)) as image:
            source_width, source_height = image.size
        if source_width <= 0 or source_height <= 0:
            return max_width
        scale = min(max_width / source_width, max_height / source_height)
        # A small upscale is useful for screenshot-style itineraries, but avoid
        # excessive enlargement that would make text blurry.
        scale = min(scale, 1.35)
        return max(260, min(max_width, int(round(source_width * scale))))
    except Exception:
        return max_width


def _dialog_decorator(title: str):
    if hasattr(st, "dialog"):
        return st.dialog(title, width="medium")
    return lambda function: function


@_dialog_decorator("Weekly Itinerary Preview")
def render_itinerary_preview_dialog(
    client: Any,
    record: dict[str, Any],
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
) -> None:
    st.markdown(f"### {_clean(record.get('auditor_name')) or 'Auditor'}")
    st.caption(
        f"Week Covered: {format_week(record)} · "
        f"{_status_icon(record.get('status'))} {_status_label(record.get('status'))}"
    )
    submitter_remarks = _clean(record.get("submitter_remarks"))
    admin_remarks = _clean(record.get("admin_remarks"))
    if submitter_remarks:
        st.info(f"Auditor remarks: {submitter_remarks}")
    if admin_remarks:
        st.warning(f"Administrator remarks: {admin_remarks}")

    try:
        image_bytes = download_itinerary_image(client, record, config)
    except Exception as exc:
        st.error(str(exc))
        return

    popup_width = _itinerary_image_width(
        image_bytes,
        max_width=650,
        max_height=460,
    )
    st.image(
        image_bytes,
        caption=_clean(record.get("original_filename")) or "Weekly itinerary",
        width=popup_width,
    )
    st.download_button(
        "Download Original Image",
        data=image_bytes,
        file_name=_clean(record.get("original_filename")) or "weekly_itinerary.png",
        mime=_clean(record.get("mime_type")) or "image/png",
        use_container_width=True,
        key=f"weekly_itinerary_dialog_download_{record.get('id')}",
    )


def _render_setup_notice() -> None:
    st.warning("Weekly Itinerary storage is not ready yet.")
    st.markdown(
        "Run `SUPABASE_WEEKLY_ITINERARY_SETUP.sql` in the same Supabase project used by IARS, "
        "then reboot the Streamlit application."
    )


def _filter_records(
    records: Iterable[dict[str, Any]],
    *,
    status: str = "All",
    auditor: str = "All",
    search: str = "",
) -> list[dict[str, Any]]:
    status_filter = _clean(status).casefold()
    auditor_filter = _clean(auditor).casefold()
    search_filter = _clean(search).casefold()
    filtered: list[dict[str, Any]] = []
    for record in records:
        if status_filter not in {"", "all"} and _clean(record.get("status")).casefold() != status_filter:
            continue
        if auditor_filter not in {"", "all"} and _clean(record.get("auditor_name")).casefold() != auditor_filter:
            continue
        haystack = " ".join(
            [
                _clean(record.get("auditor_name")),
                _clean(record.get("submitted_by_username")),
                _clean(record.get("week_start")),
                _clean(record.get("week_end")),
                _clean(record.get("original_filename")),
                _clean(record.get("submitter_remarks")),
                _clean(record.get("admin_remarks")),
            ]
        ).casefold()
        if search_filter and search_filter not in haystack:
            continue
        filtered.append(record)
    return filtered


def render_weekly_itinerary_page(
    *,
    client: Any,
    current_user: dict[str, Any],
    admin: bool,
    ready: bool,
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
) -> None:
    if not ready or client is None:
        _render_setup_notice()
        return

    user_tab_label = "My Weekly Itineraries"
    if admin:
        my_tab, admin_tab = st.tabs([user_tab_label, "All Auditor Submissions"])
    else:
        my_tab = st.container()
        admin_tab = None

    with my_tab:
        with st.container(border=True):
            st.markdown("### Upload Weekly Itinerary")
            st.caption(
                "Upload one JPG, JPEG or PNG image for the selected week. Only you and the IARS administrator can view it."
            )
            default_start = monday_for()
            default_end = friday_for()
            date_left, date_right = st.columns(2)
            with date_left:
                week_start = st.date_input(
                    "Week Start",
                    value=default_start,
                    key="weekly_itinerary_week_start_v4_4_73",
                )
            with date_right:
                week_end = st.date_input(
                    "Week End",
                    value=default_end,
                    key="weekly_itinerary_week_end_v4_4_73",
                )
            itinerary_image = st.file_uploader(
                "Weekly itinerary image",
                type=["jpg", "jpeg", "png"],
                key="weekly_itinerary_upload_v4_4_73",
                help="Maximum size: 10 MB.",
            )
            submitter_remarks = st.text_area(
                "Remarks (optional)",
                key="weekly_itinerary_submitter_remarks_v4_4_73",
                placeholder="Example: Field itinerary for July 20–24, 2026",
            )
            if st.button(
                "Submit for Approval",
                type="primary",
                use_container_width=True,
                key="weekly_itinerary_submit_v4_4_73",
            ):
                if itinerary_image is None:
                    st.error("Select a JPG or PNG itinerary image before submitting.")
                else:
                    try:
                        record = submit_weekly_itinerary(
                            client,
                            current_user,
                            week_start=week_start,
                            week_end=week_end,
                            image_bytes=itinerary_image.getvalue(),
                            original_filename=itinerary_image.name,
                            mime_type=itinerary_image.type,
                            submitter_remarks=submitter_remarks,
                            config=config,
                        )
                        st.success(
                            f"Weekly itinerary for {format_week(record)} was submitted for administrator approval."
                        )
                        st.session_state.pop("weekly_itinerary_my_records_v4_4_73", None)
                        st.rerun()
                    except DuplicateWeeklyItineraryError as exc:
                        st.warning(str(exc))
                    except Exception as exc:
                        st.error(str(exc))

        st.divider()
        st.markdown("### My Submission History")
        try:
            my_records = list_user_itineraries(client, current_user, config)
        except Exception as exc:
            st.error(
                "Unable to load Weekly Itineraries. Run the setup SQL if this is the first deployment. "
                f"Details: {exc}"
            )
            my_records = []

        if not my_records:
            st.info("No weekly itinerary has been uploaded yet.")
        else:
            rows = [
                {
                    "Week Covered": format_week(record),
                    "Status": _status_label(record.get("status")),
                    "Revision": int(record.get("revision_no") or 1),
                    "Submitted": _clean(record.get("submitted_at"))[:16].replace("T", " "),
                    "Administrator Remarks": _clean(record.get("admin_remarks")),
                }
                for record in my_records
            ]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            labels = [_record_label(record, index) for index, record in enumerate(my_records, start=1)]
            selected_label = st.selectbox(
                "Select itinerary",
                labels,
                key="weekly_itinerary_my_select_v4_4_73",
            )
            selected_record = my_records[labels.index(selected_label)]
            if st.button(
                "View Itinerary",
                use_container_width=True,
                key=f"weekly_itinerary_my_view_{selected_record.get('id')}",
            ):
                render_itinerary_preview_dialog(client, selected_record, config)

    if admin_tab is not None:
        with admin_tab:
            try:
                all_records = list_all_itineraries(client, config)
            except Exception as exc:
                st.error(
                    "Unable to load all Weekly Itinerary records. Run the setup SQL if required. "
                    f"Details: {exc}"
                )
                all_records = []

            pending_count = sum(_clean(record.get("status")).casefold() == "pending" for record in all_records)
            approved_count = sum(_clean(record.get("status")).casefold() == "approved" for record in all_records)
            returned_count = sum(_clean(record.get("status")).casefold() == "returned" for record in all_records)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Uploads", len(all_records))
            m2.metric("Pending Approval", pending_count)
            m3.metric("Approved", approved_count)
            m4.metric("Returned", returned_count)

            auditors = sorted(
                {_clean(record.get("auditor_name")) for record in all_records if _clean(record.get("auditor_name"))},
                key=str.casefold,
            )
            filter_1, filter_2, filter_3 = st.columns([1, 1.3, 2])
            with filter_1:
                status_filter = st.selectbox(
                    "Status",
                    ["All", "pending", "approved", "returned"],
                    format_func=lambda value: "All" if value == "All" else _status_label(value),
                    key="weekly_itinerary_admin_status_v4_4_73",
                )
            with filter_2:
                auditor_filter = st.selectbox(
                    "Auditor",
                    ["All"] + auditors,
                    key="weekly_itinerary_admin_auditor_v4_4_73",
                )
            with filter_3:
                search = st.text_input(
                    "Search",
                    placeholder="Week, filename, auditor or remarks",
                    key="weekly_itinerary_admin_search_v4_4_73",
                )

            filtered = _filter_records(
                all_records,
                status=status_filter,
                auditor=auditor_filter,
                search=search,
            )
            if not filtered:
                st.info("No Weekly Itinerary records match the current filters.")
            else:
                admin_rows = [
                    {
                        "Auditor": _clean(record.get("auditor_name")),
                        "Week Covered": format_week(record),
                        "Status": _status_label(record.get("status")),
                        "Revision": int(record.get("revision_no") or 1),
                        "Submitted": _clean(record.get("submitted_at"))[:16].replace("T", " "),
                        "Approved By": _clean(record.get("approved_by")),
                    }
                    for record in filtered
                ]
                st.dataframe(pd.DataFrame(admin_rows), use_container_width=True, hide_index=True)
                labels = [
                    _record_label(record, index, include_auditor=True)
                    for index, record in enumerate(filtered, start=1)
                ]
                selected_label = st.selectbox(
                    "Select auditor itinerary",
                    labels,
                    key="weekly_itinerary_admin_select_v4_4_73",
                )
                selected_record = filtered[labels.index(selected_label)]

                action_left, action_right = st.columns([1, 2])
                with action_left:
                    if st.button(
                        "Open Image",
                        use_container_width=True,
                        key=f"weekly_itinerary_admin_view_{selected_record.get('id')}",
                    ):
                        render_itinerary_preview_dialog(client, selected_record, config)
                with action_right:
                    st.caption(
                        f"{_status_icon(selected_record.get('status'))} "
                        f"Current status: {_status_label(selected_record.get('status'))}"
                    )

                admin_remarks = st.text_area(
                    "Approval / Return Remarks",
                    value=_clean(selected_record.get("admin_remarks")),
                    key=f"weekly_itinerary_admin_remarks_{selected_record.get('id')}",
                    placeholder="Required when returning the itinerary for revision.",
                )
                approve_col, return_col = st.columns(2)
                with approve_col:
                    if st.button(
                        "Approve Itinerary",
                        type="primary",
                        use_container_width=True,
                        key=f"weekly_itinerary_approve_{selected_record.get('id')}",
                    ):
                        try:
                            update_itinerary_status(
                                client,
                                selected_record,
                                current_user,
                                status="approved",
                                remarks=admin_remarks,
                                config=config,
                            )
                            st.success("Weekly itinerary approved. It will now appear on the auditor's Dashboard.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                with return_col:
                    if st.button(
                        "Return for Revision",
                        use_container_width=True,
                        key=f"weekly_itinerary_return_{selected_record.get('id')}",
                    ):
                        if not _clean(admin_remarks):
                            st.error("Enter a reason before returning the itinerary for revision.")
                        else:
                            try:
                                update_itinerary_status(
                                    client,
                                    selected_record,
                                    current_user,
                                    status="returned",
                                    remarks=admin_remarks,
                                    config=config,
                                )
                                st.warning("Weekly itinerary returned to the auditor for revision.")
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))


def render_dashboard_weekly_itinerary(
    *,
    client: Any,
    current_user: dict[str, Any],
    admin: bool,
    ready: bool,
    config: WeeklyItineraryConfig = WeeklyItineraryConfig(),
    navigation_label: str = "🗓️ Weekly Itinerary",
) -> None:
    """Render the auditor's latest approved itinerary or the admin pending summary."""
    with st.container(border=True):
        st.markdown("### 🗓️ Weekly Itinerary")
        if not ready or client is None:
            st.caption("Weekly Itinerary storage requires setup.")
            return

        try:
            if admin:
                records = list_all_itineraries(client, config, limit=500)
                pending = [record for record in records if _clean(record.get("status")).casefold() == "pending"]
                st.metric("Pending Approval", len(pending))
                st.caption("Review all auditor submissions in the Weekly Itinerary module.")
                if st.button(
                    "Open Weekly Itinerary Module",
                    use_container_width=True,
                    key="dashboard_open_weekly_itinerary_admin_v4_4_73",
                ):
                    st.session_state["main_navigation"] = navigation_label
                    st.rerun()
                return

            records = list_user_itineraries(client, current_user, config, limit=100)
        except Exception as exc:
            st.caption(f"Weekly Itinerary could not be loaded: {exc}")
            return

        approved = [record for record in records if _clean(record.get("status")).casefold() == "approved"]
        latest = records[0] if records else None
        approved_record = approved[0] if approved else None

        if approved_record:
            st.success(f"Approved · {format_week(approved_record)}")
            try:
                image_bytes = download_itinerary_image(client, approved_record, config)
                dashboard_width = _itinerary_image_width(
                    image_bytes,
                    max_width=900,
                    max_height=620,
                )
                # The approved itinerary is intentionally shown immediately on
                # the Dashboard. No extra View button is required.
                st.image(
                    image_bytes,
                    caption=_clean(approved_record.get("original_filename")) or "Approved weekly itinerary",
                    width=dashboard_width,
                )
                st.download_button(
                    "Download Approved Itinerary",
                    data=image_bytes,
                    file_name=_clean(approved_record.get("original_filename")) or "weekly_itinerary.png",
                    mime=_clean(approved_record.get("mime_type")) or "image/png",
                    use_container_width=True,
                    key=f"dashboard_download_weekly_itinerary_{approved_record.get('id')}",
                )
            except Exception as exc:
                st.warning(str(exc))
            return

        if latest:
            status = _clean(latest.get("status")).casefold()
            if status == "pending":
                st.info(f"Your itinerary for {format_week(latest)} is awaiting administrator approval.")
            elif status == "returned":
                st.warning(
                    f"Your itinerary for {format_week(latest)} was returned for revision. "
                    f"{_clean(latest.get('admin_remarks'))}"
                )
        else:
            st.caption("No weekly itinerary has been submitted yet.")

        if st.button(
            "Open Weekly Itinerary Module",
            use_container_width=True,
            key="dashboard_open_weekly_itinerary_user_v4_4_73",
        ):
            st.session_state["main_navigation"] = navigation_label
            st.rerun()
