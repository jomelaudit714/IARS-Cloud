from __future__ import annotations

from calendar import month_name, monthrange
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Iterator
from urllib.parse import urlencode
import html
import re

import pandas as pd
import streamlit as st


GANTT_MASTER_TABLE = "iars_gantt_master"
GANTT_SCHEDULE_TABLE = "iars_gantt_schedule"
GANTT_HOLIDAY_TABLE = "iars_gantt_holiday"

GANTT_STATUSES = ["Planned", "In Progress", "Done", "Overdue"]
REPORT_STAGES = ["Overdue: IRS", "For FRS", "Overdue: FRS", "FRS"]
# The database continues to store "Planned" for backward compatibility, but the UI displays it as "Scheduled".
DISPLAY_STATUSES = ["Scheduled", "In Progress", "Overdue", "Done"] + REPORT_STAGES
MONTHS = list(range(1, 13))
PHILIPPINE_TIMEZONE = timezone(timedelta(hours=8))
REPORT_WORKING_DAYS = 5
GANTT_EDIT_QUERY_PARAM = "iars_gantt_edit"  # legacy URL key; no longer used for month clicks
GANTT_PENDING_EDIT_KEY = "iars_gantt_pending_edit_v4530"
GANTT_GRID_KEY = "iars_gantt_native_grid_v4532"
GANTT_GRID_MAP_SUFFIX = "__selection_map"
GANTT_COMPONENT_KEY = "iars_gantt_pointer_grid_v4544"
_GANTT_GRID_COMPONENT: Any | None = None

HOLIDAY_COVERAGES = ["National", "Province of Rizal", "San Mateo, Rizal"]
HOLIDAY_TYPES = [
    "Regular",
    "Special Non-Working",
    "Local Special Non-Working",
    "Special Working",
]
NON_WORKING_HOLIDAY_TYPES = {
    "regular",
    "special non working",
    "local special non working",
}

NICKNAME_OVERRIDES = {
    "patricia anne del rosario": "Anne",
    "sarina amuraw": "Sab",
    "cris canonoy": "Cris",
    "jomel santiago": "Jomel",
    "noel buena": "Noel",
    "trece generato jr.": "Trece",
    "trece generato jr": "Trece",
    "antonio p. bides": "Antonio",
    "antonio p bides": "Antonio",
    "jed laserna": "Jed",
    "joshua christopher catis": "Joshua",
}


class GanttError(RuntimeError):
    pass


@dataclass(frozen=True)
class GanttSetupStatus:
    ready: bool
    message: str = ""


@dataclass(frozen=True)
class ReportStageInfo:
    stage: str
    deadline: date | None = None
    overdue: bool = False


def _response_rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def _name_key(value: Any) -> str:
    text = _clean_text(value).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _user_name(user: Any) -> str:
    if not isinstance(user, dict):
        return "IARS User"
    return _clean_text(user.get("full_name") or user.get("username") or "IARS User")


def nickname_for(full_name: Any) -> str:
    name = _clean_text(full_name)
    if not name:
        return "—"
    override = NICKNAME_OVERRIDES.get(_name_key(name))
    if override:
        return override
    return name.split()[0][:14]


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = _clean_text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _date_text(value: Any) -> str:
    parsed = _parse_date(value)
    return parsed.isoformat() if parsed else ""


def _display_date(value: Any) -> str:
    parsed = _parse_date(value)
    return parsed.strftime("%b %d, %Y") if parsed else "—"


def _box_date(value: Any) -> str:
    """Compact date used inside monthly Gantt boxes: MM/DD/YY."""
    parsed = _parse_date(value)
    return parsed.strftime("%m/%d/%y") if parsed else "—"


def _display_stage(stage: Any) -> str:
    """Use Scheduled in the UI without changing the legacy database value Planned."""
    clean_stage = _clean_text(stage) or "Planned"
    return "Scheduled" if clean_stage == "Planned" else clean_stage


def _today_pht() -> date:
    return datetime.now(PHILIPPINE_TIMEZONE).date()


def month_end_date(year: int, month: int) -> date:
    return date(int(year), int(month), monthrange(int(year), int(month))[1])


def effective_status(entry: dict[str, Any], *, today: date | None = None) -> str:
    status = _clean_text(entry.get("status")) or "Planned"
    if status == "Done":
        return "Done"
    planned = _parse_date(entry.get("planned_date"))
    check_date = today or _today_pht()
    if planned and planned < check_date:
        return "Overdue"
    return status if status in GANTT_STATUSES else "Planned"


def _holiday_type_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _clean_text(value).casefold()).strip()


def active_non_working_holiday_dates(rows: Iterable[dict[str, Any]]) -> set[date]:
    dates: set[date] = set()
    for row in rows:
        active = row.get("active", True)
        if isinstance(active, str):
            active = _clean_text(active).casefold() not in {"no", "n", "false", "0", "inactive"}
        if not bool(active):
            continue
        if _holiday_type_key(row.get("holiday_type")) not in NON_WORKING_HOLIDAY_TYPES:
            continue
        holiday_date = _parse_date(row.get("holiday_date"))
        if holiday_date:
            dates.add(holiday_date)
    return dates


def add_working_days(
    start_date: date,
    working_days: int = REPORT_WORKING_DAYS,
    *,
    holidays: Iterable[date] = (),
) -> date:
    """Return the deadline after N working days, excluding start date.

    Saturday, Sunday, active regular/special non-working national holidays,
    Province of Rizal holidays, and San Mateo, Rizal holidays are excluded.
    """
    if working_days < 0:
        raise ValueError("working_days must not be negative")
    holiday_set = set(holidays)
    cursor = start_date
    counted = 0
    while counted < working_days:
        cursor += timedelta(days=1)
        if cursor.weekday() >= 5 or cursor in holiday_set:
            continue
        counted += 1
    return cursor


def report_stage_info(
    entry: dict[str, Any],
    holiday_rows: Iterable[dict[str, Any]] = (),
    *,
    today: date | None = None,
) -> ReportStageInfo:
    """Return the visible workflow stage and its automatic working-day deadline.

    There is intentionally no separate ``For IRS`` or ``IRS`` display stage.
    A completed audit stays ``Done`` while its five-working-day initial-report
    period is running, then becomes ``Overdue: IRS`` if no initial report was
    submitted. After the initial report is recorded, the stage becomes
    ``For FRS`` and later ``Overdue: FRS`` when applicable.
    """
    check_date = today or _today_pht()
    audit_status = effective_status(entry, today=check_date)
    if audit_status != "Done":
        return ReportStageInfo(audit_status, _parse_date(entry.get("planned_date")), audit_status == "Overdue")

    holiday_dates = active_non_working_holiday_dates(holiday_rows)
    audit_date = _parse_date(entry.get("accomplished_date"))
    initial_date = _parse_date(entry.get("initial_report_submitted_at"))
    final_date = _parse_date(entry.get("final_report_submitted_at"))

    if final_date:
        return ReportStageInfo("FRS", final_date, False)
    if initial_date:
        deadline = add_working_days(initial_date, REPORT_WORKING_DAYS, holidays=holiday_dates)
        overdue = check_date > deadline
        return ReportStageInfo("Overdue: FRS" if overdue else "For FRS", deadline, overdue)
    if not audit_date:
        return ReportStageInfo("Done", None, False)
    deadline = add_working_days(audit_date, REPORT_WORKING_DAYS, holidays=holiday_dates)
    overdue = check_date > deadline
    return ReportStageInfo("Overdue: IRS" if overdue else "Done", deadline, overdue)


def gantt_setup_status(client: Any) -> GanttSetupStatus:
    if client is None:
        return GanttSetupStatus(False, "Supabase is not connected.")
    try:
        client.table(GANTT_MASTER_TABLE).select("id").limit(1).execute()
        client.table(GANTT_SCHEDULE_TABLE).select("id").limit(1).execute()
        client.table(GANTT_HOLIDAY_TABLE).select("id").limit(1).execute()
        return GanttSetupStatus(True, "")
    except Exception as exc:
        return GanttSetupStatus(
            False,
            "Yearly Audit Gantt V4.5.20 tables/columns are not ready. Run "
            "SUPABASE_GANTT_V4_5_20_WORKFLOW_MIGRATION.sql, then refresh IARS. "
            f"Details: {exc}",
        )


def list_master_records(client: Any, *, active_only: bool = False) -> list[dict[str, Any]]:
    query = client.table(GANTT_MASTER_TABLE).select("*")
    if active_only:
        query = query.eq("active", True)
    return _response_rows(query.order("company_department").order("custodian").execute())


def list_schedule_entries(
    client: Any,
    schedule_year: int,
    *,
    auditor_full_name: str | None = None,
) -> list[dict[str, Any]]:
    query = client.table(GANTT_SCHEDULE_TABLE).select("*").eq("schedule_year", int(schedule_year))
    if auditor_full_name:
        query = query.ilike("auditor_full_name", _clean_text(auditor_full_name))
    return _response_rows(query.order("schedule_month").execute())


def list_holidays(client: Any, year: int | None = None, *, active_only: bool = True) -> list[dict[str, Any]]:
    query = client.table(GANTT_HOLIDAY_TABLE).select("*")
    if active_only:
        query = query.eq("active", True)
    rows = _response_rows(query.order("holiday_date").execute())
    if year is None:
        return rows
    return [row for row in rows if (_parse_date(row.get("holiday_date")) or date.min).year == int(year)]


def _master_payload(row: dict[str, Any], actor: str) -> dict[str, Any]:
    company = _clean_text(row.get("company_department") or row.get("Company") or row.get("Company / Department"))
    custodian = _clean_text(row.get("custodian") or row.get("Custodian"))
    task = _clean_text(row.get("audit_task") or row.get("Audit Task"))
    accountability = _clean_text(row.get("accountability") or row.get("Accountability"))
    active_raw = row.get("active", row.get("Active", True))
    if isinstance(active_raw, str):
        active = active_raw.strip().casefold() not in {"no", "n", "false", "0", "inactive"}
    else:
        active = bool(active_raw)
    if not company or not custodian or not task:
        raise GanttError("Company, Custodian, and Audit Task are required.")
    return {
        "company_department": company,
        "custodian": custodian,
        "audit_task": task,
        "accountability": accountability,
        "active": active,
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def upsert_master_records(client: Any, rows: Iterable[dict[str, Any]], actor: str) -> int:
    payloads = []
    for row in rows:
        payload = _master_payload(dict(row), actor)
        payload["created_by"] = actor
        payloads.append(payload)
    if not payloads:
        raise GanttError("No valid master-data rows were provided.")
    response = client.table(GANTT_MASTER_TABLE).upsert(
        payloads,
        on_conflict="company_department,custodian,audit_task,accountability",
    ).execute()
    returned = _response_rows(response)
    return len(returned) if returned else len(payloads)


def update_master_record(client: Any, record_id: str, row: dict[str, Any], actor: str) -> None:
    client.table(GANTT_MASTER_TABLE).update(_master_payload(row, actor)).eq("id", record_id).execute()


def set_master_active(client: Any, record_id: str, active: bool, actor: str) -> None:
    client.table(GANTT_MASTER_TABLE).update({
        "active": bool(active),
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", record_id).execute()


def _unique_record_ids(record_ids: Iterable[Any]) -> list[str]:
    """Return cleaned, de-duplicated master-record IDs in original order."""
    seen: set[str] = set()
    cleaned: list[str] = []
    for value in record_ids:
        record_id = _clean_text(value)
        if record_id and record_id not in seen:
            seen.add(record_id)
            cleaned.append(record_id)
    return cleaned


def delete_master_records(client: Any, record_ids: Iterable[Any]) -> int:
    """Permanently delete selected master records and their linked schedules.

    Monthly schedules are deleted explicitly before the master rows. The
    database foreign key also uses ON DELETE CASCADE, but the explicit delete
    keeps this action compatible with older deployments that may not yet have
    the cascade constraint. Holiday-calendar records are never affected.
    """
    ids = _unique_record_ids(record_ids)
    if not ids:
        raise GanttError("Select at least one Gantt Master Data record to delete.")

    chunk_size = 100
    for start in range(0, len(ids), chunk_size):
        chunk = ids[start:start + chunk_size]
        client.table(GANTT_SCHEDULE_TABLE).delete().in_("master_id", chunk).execute()
        client.table(GANTT_MASTER_TABLE).delete().in_("id", chunk).execute()
    return len(ids)


def delete_all_master_records(client: Any) -> int:
    """Delete the whole custodian master list and all linked schedules."""
    records = list_master_records(client, active_only=False)
    ids = [row.get("id") for row in records]
    if not _unique_record_ids(ids):
        return 0
    return delete_master_records(client, ids)


def _holiday_payload(row: dict[str, Any], actor: str) -> dict[str, Any]:
    holiday_date = _parse_date(row.get("holiday_date") or row.get("Holiday Date"))
    holiday_name = _clean_text(row.get("holiday_name") or row.get("Holiday Name"))
    coverage = _clean_text(row.get("coverage") or row.get("Coverage"))
    holiday_type = _clean_text(row.get("holiday_type") or row.get("Holiday Type"))
    source_reference = _clean_text(row.get("source_reference") or row.get("Source Reference"))
    active_raw = row.get("active", row.get("Active", True))
    active = (
        active_raw.strip().casefold() not in {"no", "n", "false", "0", "inactive"}
        if isinstance(active_raw, str)
        else bool(active_raw)
    )
    if not holiday_date or not holiday_name:
        raise GanttError("Holiday Date and Holiday Name are required.")
    if coverage not in HOLIDAY_COVERAGES:
        raise GanttError("Coverage must be National, Province of Rizal, or San Mateo, Rizal.")
    if holiday_type not in HOLIDAY_TYPES:
        raise GanttError("Select a valid Holiday Type.")
    return {
        "holiday_date": holiday_date.isoformat(),
        "holiday_name": holiday_name,
        "coverage": coverage,
        "holiday_type": holiday_type,
        "source_reference": source_reference,
        "active": active,
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def upsert_holiday_records(client: Any, rows: Iterable[dict[str, Any]], actor: str) -> int:
    payloads = []
    for row in rows:
        payload = _holiday_payload(dict(row), actor)
        payload["created_by"] = actor
        payloads.append(payload)
    if not payloads:
        raise GanttError("No valid holiday rows were provided.")
    response = client.table(GANTT_HOLIDAY_TABLE).upsert(
        payloads,
        on_conflict="holiday_date,coverage",
    ).execute()
    returned = _response_rows(response)
    return len(returned) if returned else len(payloads)


def update_holiday_record(client: Any, record_id: str, row: dict[str, Any], actor: str) -> None:
    client.table(GANTT_HOLIDAY_TABLE).update(_holiday_payload(row, actor)).eq("id", record_id).execute()


def set_holiday_active(client: Any, record_id: str, active: bool, actor: str) -> None:
    client.table(GANTT_HOLIDAY_TABLE).update({
        "active": bool(active),
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", record_id).execute()


def upsert_schedule_entry(
    client: Any,
    *,
    master_id: str,
    schedule_year: int,
    schedule_month: int,
    auditor_full_name: str,
    status: str = "Planned",
    planned_date: date | None = None,
    accomplished_date: date | None = None,
    remarks: str = "",
    actor: str,
) -> None:
    auditor = _clean_text(auditor_full_name)
    clean_status = _clean_text(status) or "Planned"
    if not master_id:
        raise GanttError("Select a custodian and audit task.")
    if int(schedule_month) not in MONTHS:
        raise GanttError("Select a valid month.")
    if not auditor:
        raise GanttError("Assigned auditor is required.")
    if clean_status not in GANTT_STATUSES:
        raise GanttError("Select a valid status.")
    due_date = planned_date or month_end_date(schedule_year, schedule_month)
    if clean_status == "Done" and not accomplished_date:
        raise GanttError("Date of Audit is required when status is Done.")
    payload = {
        "master_id": master_id,
        "schedule_year": int(schedule_year),
        "schedule_month": int(schedule_month),
        "auditor_full_name": auditor,
        "auditor_nickname": nickname_for(auditor),
        "status": clean_status,
        "planned_date": due_date.isoformat(),
        "accomplished_date": accomplished_date.isoformat() if accomplished_date else None,
        "remarks": _clean_text(remarks),
        "created_by": actor,
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    client.table(GANTT_SCHEDULE_TABLE).upsert(
        payload,
        on_conflict="master_id,schedule_year,schedule_month",
    ).execute()


def admin_save_schedule_entry(
    client: Any,
    *,
    entry: dict[str, Any] | None,
    master_id: str,
    schedule_year: int,
    schedule_month: int,
    auditor_full_name: str,
    status: str,
    accomplished_date: date | None,
    initial_report_submitted_at: date | None = None,
    final_report_submitted_at: date | None = None,
    remarks: str,
    actor: str,
    holiday_rows: Iterable[dict[str, Any]] = (),
) -> None:
    """Create or edit any monthly schedule from the Admin/Supervisor dialog.

    The Admin/Supervisor may select every visible workflow status.  Report
    stages are saved using the existing audit, IRS and FRS date columns, so no
    additional Supabase migration is required.
    """
    selected_status = _clean_text(status) or "Scheduled"
    if selected_status not in DISPLAY_STATUSES:
        raise GanttError("Select a valid audit or report status.")

    auditor = _clean_text(auditor_full_name)
    if not auditor:
        raise GanttError("Assigned auditor is required.")

    today = _today_pht()
    holiday_dates = active_non_working_holiday_dates(holiday_rows)
    for label, value in (
        ("Date of Audit", accomplished_date),
        ("IRS Submission Date", initial_report_submitted_at),
        ("FRS Submission Date", final_report_submitted_at),
    ):
        if value and value > today:
            raise GanttError(f"{label} cannot be later than today's Philippine date.")

    database_status = {
        "Scheduled": "Planned",
        "In Progress": "In Progress",
        "Overdue": "Overdue",
    }.get(selected_status, "Done")

    needs_audit_date = selected_status in {
        "Done", "Overdue: IRS", "For FRS", "Overdue: FRS", "FRS"
    }
    needs_irs_date = selected_status in {"For FRS", "Overdue: FRS", "FRS"}
    needs_frs_date = selected_status == "FRS"

    if needs_audit_date and not accomplished_date:
        raise GanttError("Date of Audit is required for the selected status.")
    if needs_irs_date and not initial_report_submitted_at:
        raise GanttError("IRS Submission Date is required for the selected status.")
    if needs_frs_date and not final_report_submitted_at:
        raise GanttError("FRS Submission Date is required when status is FRS.")

    if accomplished_date and initial_report_submitted_at and initial_report_submitted_at < accomplished_date:
        raise GanttError("IRS Submission Date cannot be earlier than the Date of Audit.")
    if initial_report_submitted_at and final_report_submitted_at and final_report_submitted_at < initial_report_submitted_at:
        raise GanttError("FRS Submission Date cannot be earlier than the IRS Submission Date.")

    if selected_status == "Overdue" and month_end_date(schedule_year, schedule_month) >= today:
        raise GanttError("Overdue can be selected only when the month's due date has already passed.")

    if accomplished_date:
        irs_deadline = add_working_days(
            accomplished_date,
            REPORT_WORKING_DAYS,
            holidays=holiday_dates,
        )
        if selected_status == "Done" and today > irs_deadline:
            raise GanttError(
                "This Date of Audit is already beyond the five-working-day IRS period. "
                "Choose Overdue: IRS, For FRS, Overdue: FRS, or FRS."
            )
        if selected_status == "Overdue: IRS" and today <= irs_deadline:
            raise GanttError(
                f"Overdue: IRS begins after {_display_date(irs_deadline)}. "
                "Choose Done until the five-working-day period has passed."
            )

    if initial_report_submitted_at:
        frs_deadline = add_working_days(
            initial_report_submitted_at,
            REPORT_WORKING_DAYS,
            holidays=holiday_dates,
        )
        if selected_status == "For FRS" and today > frs_deadline:
            raise GanttError(
                "This IRS Submission Date is already beyond the five-working-day FRS period. "
                "Choose Overdue: FRS or FRS."
            )
        if selected_status == "Overdue: FRS" and today <= frs_deadline:
            raise GanttError(
                f"Overdue: FRS begins after {_display_date(frs_deadline)}. "
                "Choose For FRS until the five-working-day period has passed."
            )

    if not needs_audit_date:
        accomplished_date = None
    if not needs_irs_date:
        initial_report_submitted_at = None
    if not needs_frs_date:
        final_report_submitted_at = None

    due_date = month_end_date(schedule_year, schedule_month)
    payload: dict[str, Any] = {
        "master_id": master_id,
        "schedule_year": int(schedule_year),
        "schedule_month": int(schedule_month),
        "auditor_full_name": auditor,
        "auditor_nickname": nickname_for(auditor),
        "status": database_status,
        "planned_date": due_date.isoformat(),
        "accomplished_date": accomplished_date.isoformat() if accomplished_date else None,
        "initial_report_submitted_at": (
            initial_report_submitted_at.isoformat() if initial_report_submitted_at else None
        ),
        "final_report_submitted_at": (
            final_report_submitted_at.isoformat() if final_report_submitted_at else None
        ),
        "remarks": _clean_text(remarks),
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Supabase defines both report-reference columns as NOT NULL with an
    # empty-string default.  Sending an explicit Python None bypasses that
    # database default and causes the insert/update to fail.  Always send a
    # string while preserving an existing reference when the corresponding
    # report stage is still present.
    payload["initial_report_reference"] = (
        _clean_text((entry or {}).get("initial_report_reference"))
        if initial_report_submitted_at is not None
        else ""
    )
    payload["final_report_reference"] = (
        _clean_text((entry or {}).get("final_report_reference"))
        if final_report_submitted_at is not None
        else ""
    )

    entry_id = _clean_text((entry or {}).get("id"))
    if entry_id:
        client.table(GANTT_SCHEDULE_TABLE).update(payload).eq("id", entry_id).execute()
        return

    payload["created_by"] = actor
    client.table(GANTT_SCHEDULE_TABLE).upsert(
        payload,
        on_conflict="master_id,schedule_year,schedule_month",
    ).execute()


def mark_audit_in_progress(
    client: Any,
    *,
    entry_id: str,
    assigned_auditor: str,
    current_user_name: str,
    remarks: str = "",
) -> None:
    if _name_key(assigned_auditor) != _name_key(current_user_name):
        raise GanttError("You can only update audit schedules assigned to your account.")
    client.table(GANTT_SCHEDULE_TABLE).update({
        "status": "In Progress",
        "remarks": _clean_text(remarks),
        "updated_by": current_user_name,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", entry_id).execute()


def update_auditor_accomplishment(
    client: Any,
    *,
    entry_id: str,
    assigned_auditor: str,
    current_user_name: str,
    status: str,
    accomplished_date: date | None,
    remarks: str,
) -> None:
    if _name_key(assigned_auditor) != _name_key(current_user_name):
        raise GanttError("You can only update audit schedules assigned to your account.")
    clean_status = _clean_text(status)
    if clean_status != "Done":
        raise GanttError("The auditor action is to mark the audit as Done.")
    if not accomplished_date:
        raise GanttError("Date of Audit is required when status is Done.")
    if accomplished_date > _today_pht():
        raise GanttError("Date of Audit cannot be later than today's Philippine date.")
    client.table(GANTT_SCHEDULE_TABLE).update({
        "status": "Done",
        "accomplished_date": accomplished_date.isoformat(),
        "remarks": _clean_text(remarks),
        "updated_by": current_user_name,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", entry_id).execute()


def submit_initial_report(
    client: Any,
    *,
    entry_id: str,
    assigned_auditor: str,
    current_user_name: str,
    reference: str = "",
    submitted_date: date | None = None,
) -> None:
    if _name_key(assigned_auditor) != _name_key(current_user_name):
        raise GanttError("You can only submit the initial report for an audit assigned to your account.")
    actual_date = submitted_date or _today_pht()
    client.table(GANTT_SCHEDULE_TABLE).update({
        "initial_report_submitted_at": actual_date.isoformat(),
        "initial_report_reference": _clean_text(reference),
        "updated_by": current_user_name,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", entry_id).execute()


def submit_final_report(
    client: Any,
    *,
    entry_id: str,
    actor: str,
    reference: str = "",
    submitted_date: date | None = None,
) -> None:
    actual_date = submitted_date or _today_pht()
    client.table(GANTT_SCHEDULE_TABLE).update({
        "final_report_submitted_at": actual_date.isoformat(),
        "final_report_reference": _clean_text(reference),
        "updated_by": actor,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", entry_id).execute()


def delete_schedule_entry(client: Any, entry_id: str) -> None:
    client.table(GANTT_SCHEDULE_TABLE).delete().eq("id", entry_id).execute()


def parse_master_upload(file_bytes: bytes) -> pd.DataFrame:
    try:
        xls = pd.ExcelFile(BytesIO(file_bytes))
    except Exception as exc:
        raise GanttError(f"Unable to read the Excel file: {exc}") from exc
    sheet_name = "Gantt Master Data" if "Gantt Master Data" in xls.sheet_names else xls.sheet_names[0]
    raw = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name).dropna(how="all").copy()
    normalized = {str(column).strip().casefold(): column for column in raw.columns}
    aliases = {
        "company_department": ["company / department", "company/department", "company", "department"],
        "custodian": ["custodian", "name of custodian"],
        "audit_task": ["audit task", "type of fund", "task"],
        "accountability": ["accountability", "accountable amount"],
        "active": ["active", "status"],
    }
    selected: dict[str, str] = {}
    for target, options in aliases.items():
        for option in options:
            if option in normalized:
                selected[target] = normalized[option]
                break
    required = ["company_department", "custodian", "audit_task", "accountability"]
    missing = [name for name in required if name not in selected]
    if missing:
        friendly = {
            "company_department": "Company",
            "custodian": "Custodian",
            "audit_task": "Audit Task",
            "accountability": "Accountability",
        }
        raise GanttError("Missing required column(s): " + ", ".join(friendly[name] for name in missing))

    output = pd.DataFrame({target: raw[selected[target]] for target in required})
    output["active"] = raw[selected["active"]] if "active" in selected else True
    output = output.dropna(how="all", subset=["company_department", "custodian", "audit_task"])
    for target in required:
        output[target] = output[target].map(_clean_text)
    if output[["company_department", "custodian", "audit_task"]].eq("").any(axis=None):
        raise GanttError("Every row must contain Company, Custodian, and Audit Task.")
    output["active"] = output["active"].map(
        lambda value: _clean_text(value).casefold() not in {"no", "n", "false", "0", "inactive"}
        if isinstance(value, str)
        else bool(value)
    )
    duplicates = output.duplicated(
        subset=["company_department", "custodian", "audit_task", "accountability"],
        keep=False,
    )
    if duplicates.any():
        raise GanttError(
            "Exact duplicate master-data rows were found. Company, Custodian, "
            "Audit Task, and Accountability must not all be identical."
        )
    return output.reset_index(drop=True)


def parse_holiday_upload(file_bytes: bytes) -> pd.DataFrame:
    try:
        xls = pd.ExcelFile(BytesIO(file_bytes))
    except Exception as exc:
        raise GanttError(f"Unable to read the holiday Excel file: {exc}") from exc
    sheet_name = "Holiday Calendar" if "Holiday Calendar" in xls.sheet_names else xls.sheet_names[0]
    raw = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name).dropna(how="all").copy()
    normalized = {str(column).strip().casefold(): column for column in raw.columns}
    aliases = {
        "holiday_date": ["holiday date", "date"],
        "holiday_name": ["holiday name", "holiday"],
        "coverage": ["coverage", "location"],
        "holiday_type": ["holiday type", "type"],
        "source_reference": ["source reference", "source", "proclamation / source"],
        "active": ["active", "status"],
    }
    selected: dict[str, str] = {}
    for target, options in aliases.items():
        for option in options:
            if option in normalized:
                selected[target] = normalized[option]
                break
    required = ["holiday_date", "holiday_name", "coverage", "holiday_type"]
    missing = [name for name in required if name not in selected]
    if missing:
        friendly = {
            "holiday_date": "Holiday Date",
            "holiday_name": "Holiday Name",
            "coverage": "Coverage",
            "holiday_type": "Holiday Type",
        }
        raise GanttError("Missing required column(s): " + ", ".join(friendly[name] for name in missing))

    output = pd.DataFrame()
    output["holiday_date"] = pd.to_datetime(raw[selected["holiday_date"]], errors="coerce").dt.date
    output["holiday_name"] = raw[selected["holiday_name"]].map(_clean_text)
    output["coverage"] = raw[selected["coverage"]].map(_clean_text)
    output["holiday_type"] = raw[selected["holiday_type"]].map(_clean_text)
    output["source_reference"] = (
        raw[selected["source_reference"]].map(_clean_text) if "source_reference" in selected else ""
    )
    output["active"] = raw[selected["active"]] if "active" in selected else True
    output = output.dropna(how="all", subset=["holiday_date", "holiday_name"])
    if output["holiday_date"].isna().any() or output["holiday_name"].eq("").any():
        raise GanttError("Every holiday row must contain a valid Holiday Date and Holiday Name.")
    invalid_coverage = sorted(set(output.loc[~output["coverage"].isin(HOLIDAY_COVERAGES), "coverage"]))
    if invalid_coverage:
        raise GanttError("Invalid Coverage value(s): " + ", ".join(invalid_coverage))
    invalid_types = sorted(set(output.loc[~output["holiday_type"].isin(HOLIDAY_TYPES), "holiday_type"]))
    if invalid_types:
        raise GanttError("Invalid Holiday Type value(s): " + ", ".join(invalid_types))
    output["active"] = output["active"].map(
        lambda value: _clean_text(value).casefold() not in {"no", "n", "false", "0", "inactive"}
        if isinstance(value, str)
        else bool(value)
    )
    if output.duplicated(subset=["holiday_date", "coverage"], keep=False).any():
        raise GanttError("Duplicate Holiday Date + Coverage rows were found.")
    return output.reset_index(drop=True)


def _format_accountability(value: Any) -> str:
    if value is None or (isinstance(value, str) and not value.strip()):
        return "—"
    text = "0" if value == 0 else _clean_text(value)
    if not text:
        return "—"
    try:
        number = float(text.replace(",", "").replace("₱", ""))
        return f"₱{number:,.2f}"
    except ValueError:
        return text


def done_frequency_by_master(
    masters: list[dict[str, Any]],
    entries: list[dict[str, Any]],
) -> dict[str, int]:
    valid_master_ids = {str(master.get("id") or "") for master in masters if master.get("id")}
    counts: dict[str, int] = {}
    for entry in entries:
        if effective_status(entry) != "Done":
            continue
        master_id = str(entry.get("master_id") or "")
        if master_id in valid_master_ids:
            counts[master_id] = counts.get(master_id, 0) + 1
    return counts


def _entry_lookup(entries: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (str(entry.get("master_id") or ""), int(entry.get("schedule_month") or 0)): entry
        for entry in entries
        if entry.get("master_id") and int(entry.get("schedule_month") or 0) in MONTHS
    }


def _stage_slug(stage: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", stage.casefold()).strip("-") or "empty"


def _month_box_label(entry: dict[str, Any] | None, holiday_rows: list[dict[str, Any]]) -> tuple[str, str]:
    """Return the exact user-facing month-cell lines for the current workflow stage.

    V4.5.43 locks the date label to the date itself and no longer reuses one
    generic Due line for every report stage.  The source dates are left intact;
    only their display labels change.
    """
    if not entry:
        return "＋ Schedule", "empty"

    info = report_stage_info(entry, holiday_rows)
    # Keep the workflow/database stage as FRS, but use a clearer user-facing
    # label inside the completed-report month box.  Do not change the status
    # dropdown or database value.
    display_stage = "Report Submitted" if info.stage == "FRS" else _display_stage(info.stage)
    style_stage = _display_stage(info.stage)
    nickname = _clean_text(entry.get("auditor_nickname")) or nickname_for(entry.get("auditor_full_name"))
    audit_date = _box_date(entry.get("accomplished_date"))

    if info.stage in {"Planned", "In Progress", "Overdue"}:
        lines = [
            display_stage,
            nickname,
            f"Due:\u00A0{_box_date(entry.get('planned_date'))}",
        ]
    elif info.stage == "Done":
        lines = [
            display_stage,
            nickname,
            f"Audit Date:\u00A0{audit_date}",
        ]
    elif info.stage == "Overdue: IRS":
        lines = [
            display_stage,
            nickname,
            f"Audit Date:\u00A0{audit_date}",
            f"Due:\u00A0{_box_date(info.deadline)}",
        ]
    elif info.stage == "For FRS":
        lines = [
            display_stage,
            nickname,
            f"Audit Date:\u00A0{audit_date}",
            f"Due:\u00A0{_box_date(info.deadline)}",
        ]
    elif info.stage == "Overdue: FRS":
        # The approved V4.5.43 display specification intentionally keeps this
        # overdue box to three lines: stage, audit date, and FRS due date.
        lines = [
            display_stage,
            f"Audit Date:\u00A0{audit_date}",
            f"Due:\u00A0{_box_date(info.deadline)}",
        ]
    else:  # FRS / completed final report
        # ``report_stage_info`` returns the actual FRS submission date as its
        # deadline for this terminal stage.  Use it as a defensive fallback in
        # case a partially shaped row omits final_report_submitted_at.  The
        # shorter "Submitted" label also keeps the actual date visible inside
        # compact month cells instead of clipping it after the label.
        submission_date = _box_date(entry.get("final_report_submitted_at") or info.deadline)
        lines = [
            display_stage,
            nickname,
            f"Audit Date:\u00A0{audit_date}",
            f"Submitted:\u00A0{submission_date}",
        ]

    # Styling still follows the real workflow stage so Report Submitted keeps
    # the approved green FRS palette.
    return "\n".join(line for line in lines if line), _stage_slug(style_stage)


def _query_params_as_dict() -> dict[str, Any]:
    """Return current query parameters without assuming one Streamlit version."""
    try:
        query_params = getattr(st, "query_params")
        output: dict[str, Any] = {}
        for key in query_params:
            try:
                values = query_params.get_all(key)
            except Exception:
                values = query_params[key]
            if isinstance(values, (list, tuple)):
                output[str(key)] = [str(value) for value in values]
            else:
                output[str(key)] = str(values)
        return output
    except Exception:
        try:
            values = st.experimental_get_query_params()
            return dict(values or {})
        except Exception:
            return {}


def _query_param_value(name: str) -> str:
    value = _query_params_as_dict().get(name, "")
    if isinstance(value, (list, tuple)):
        return _clean_text(value[-1] if value else "")
    return _clean_text(value)


def _gantt_edit_href(master_id: str, year: int, month: int) -> str:
    params = _query_params_as_dict()
    params[GANTT_EDIT_QUERY_PARAM] = f"{master_id}|{int(year)}|{int(month)}"
    pairs: list[tuple[str, str]] = []
    for key, value in params.items():
        if isinstance(value, (list, tuple)):
            pairs.extend((str(key), str(item)) for item in value)
        else:
            pairs.append((str(key), str(value)))
    return "?" + urlencode(pairs)


def _selected_gantt_edit() -> tuple[str, int, int] | None:
    raw = _query_param_value(GANTT_EDIT_QUERY_PARAM)
    if not raw:
        return None
    parts = raw.split("|")
    if len(parts) != 3:
        return None
    try:
        master_id = _clean_text(parts[0])
        year = int(parts[1])
        month = int(parts[2])
    except (TypeError, ValueError):
        return None
    if not master_id or month not in MONTHS:
        return None
    return master_id, year, month


def _clear_gantt_edit_query() -> None:
    try:
        query_params = getattr(st, "query_params")
        if GANTT_EDIT_QUERY_PARAM in query_params:
            del query_params[GANTT_EDIT_QUERY_PARAM]
        return
    except Exception:
        pass
    try:
        params = _query_params_as_dict()
        params.pop(GANTT_EDIT_QUERY_PARAM, None)
        st.experimental_set_query_params(**params)
    except Exception:
        pass


def _render_gantt_css() -> None:
    st.markdown(
        """
        <style>
        .iars-gantt-title {margin-top:0!important;padding-top:0!important;}
        .iars-gantt-title h2 {font-size:1.72rem!important;font-weight:800!important;margin:0 0 .2rem!important;color:#0B2B55!important;}
        .iars-gantt-title p {color:#667085!important;margin:0 0 .45rem!important;}
        .iars-gantt-alert {border:1px solid #991B1B;background:#B91C1C;color:#fff;border-radius:14px;padding:1rem 1.1rem;margin:.5rem 0 1rem;}
        .iars-gantt-alert strong {font-size:1.02rem;display:block;margin-bottom:.18rem;}
        .iars-gantt-alert ul {margin:.45rem 0 0 1.1rem;padding:0;}
        .iars-gantt-notice {border:1px solid #D6A129;background:#FFF8E6;color:#594200;border-radius:14px;padding:1rem 1.1rem;margin:.5rem 0 1rem;}
        .iars-gantt-notice strong {display:block;margin-bottom:.18rem;}
        .iars-gantt-dashboard-panel-title{margin:0 0 .18rem;color:#0B2B55;font-size:1.18rem;font-weight:850;}
        .iars-gantt-dashboard-panel-subtitle{margin:0 0 .72rem;color:#667085;font-size:.78rem;line-height:1.35;}
        .iars-gantt-dashboard-list{display:flex;flex-direction:column;gap:.48rem;}
        .iars-gantt-dashboard-item{border:1px solid #D9E2EE;border-radius:10px;padding:.62rem .72rem;background:#FFF;}
        .iars-gantt-dashboard-item.overdue{border-color:#F0A3A3;background:#FFF5F5;}
        .iars-gantt-dashboard-item .title{font-size:.80rem;font-weight:800;color:#102A4E;line-height:1.25;}
        .iars-gantt-dashboard-item .meta{font-size:.70rem;color:#667085;line-height:1.35;margin-top:.16rem;}
        .iars-gantt-dashboard-item .stage{display:inline-block;margin-top:.28rem;font-size:.68rem;font-weight:800;color:#8B1E1E;}

        /* V4.5.42: constrain only the Gantt month editor to the visible
           browser height and give the popup its own vertical scrollbar. */
        div[data-testid="stDialog"]:has(.iars-gantt-month-editor-marker) div[role="dialog"] {
            max-height:calc(100vh - 24px)!important;
            overflow-y:auto!important;
            overflow-x:hidden!important;
            overscroll-behavior:contain!important;
            scrollbar-gutter:stable!important;
        }
        div[data-testid="stDialog"]:has(.iars-gantt-month-editor-marker) div[role="dialog"]::-webkit-scrollbar {width:10px;}
        div[data-testid="stDialog"]:has(.iars-gantt-month-editor-marker) div[role="dialog"]::-webkit-scrollbar-thumb {background:#B7C3D4;border-radius:999px;border:2px solid transparent;background-clip:padding-box;}

        /* V4.5.29: one native-DOM table. The scroll viewport owns both the
           header and rows, so the complete Company-to-December header remains
           frozen without an iframe or cross-frame click navigation. */
        .iars-gantt-native-shell {border:1px solid #D9E2EE;border-radius:14px;overflow:hidden;background:#FFFFFF;box-shadow:0 1px 2px rgba(16,24,40,.04);}
        .iars-gantt-native-scroll {width:100%;max-height:560px;overflow:auto;position:relative;overscroll-behavior:contain;scrollbar-gutter:stable;background:#FFFFFF;}
        .iars-gantt-native-table {border-collapse:separate;border-spacing:0;table-layout:fixed;width:1900px;min-width:1900px;margin:0!important;font-size:.72rem;color:#23324A;}
        .iars-gantt-native-table th,.iars-gantt-native-table td {box-sizing:border-box;width:92px;min-width:92px;max-width:92px;border-right:1px solid #D9E2EE;border-bottom:1px solid #D9E2EE;padding:.32rem .34rem;overflow:hidden;vertical-align:middle;}
        .iars-gantt-native-table th:nth-child(n+6),.iars-gantt-native-table td:nth-child(n+6){width:120px;min-width:120px;max-width:120px;padding-left:.20rem;padding-right:.20rem;}
        .iars-gantt-native-table thead th {position:sticky;top:0;z-index:100;height:54px;background:#EAF0F8;color:#0B2B55;text-align:center!important;font-weight:800;line-height:1.12;word-break:normal;overflow-wrap:anywhere;box-shadow:0 2px 0 #C8D4E3;}
        .iars-gantt-native-table thead th:nth-child(4) {font-size:.58rem!important;letter-spacing:-.035em;white-space:nowrap;overflow:visible;}
        .iars-gantt-native-table tbody td {height:118px;background:#FFFFFF;word-break:break-word;line-height:1.16;}
        .iars-gantt-native-table tbody tr:hover td {background:#F8FAFC;}
        .iars-gantt-native-table th:nth-child(1),.iars-gantt-native-table td:nth-child(1){position:sticky;left:0;}
        .iars-gantt-native-table th:nth-child(2),.iars-gantt-native-table td:nth-child(2){position:sticky;left:92px;}
        .iars-gantt-native-table th:nth-child(3),.iars-gantt-native-table td:nth-child(3){position:sticky;left:184px;}
        .iars-gantt-native-table th:nth-child(4),.iars-gantt-native-table td:nth-child(4){position:sticky;left:276px;}
        .iars-gantt-native-table th:nth-child(5),.iars-gantt-native-table td:nth-child(5){position:sticky;left:368px;box-shadow:2px 0 0 #C8D4E3;}
        .iars-gantt-native-table thead th:nth-child(-n+5){z-index:130;background:#EAF0F8;}
        .iars-gantt-native-table tbody td:nth-child(-n+5){z-index:40;background:#FFFFFF;}
        .iars-gantt-native-table tbody tr:hover td:nth-child(-n+5){background:#F8FAFC;}
        .iars-gantt-native-table .iars-static-cell {text-align:left;font-weight:600;font-size:.66rem;}
        .iars-gantt-native-table .iars-accountability {text-align:center;font-weight:800;white-space:nowrap;font-size:.64rem;letter-spacing:-.02em;}
        .iars-gantt-native-table .iars-frequency {text-align:center;font-weight:800;white-space:nowrap;font-size:.68rem;}
        .iars-gantt-month-box {display:flex;min-height:104px;width:100%;box-sizing:border-box;flex-direction:column;align-items:center;justify-content:center;gap:.08rem;border:1px solid #CBD5E1;border-radius:9px;padding:.24rem .12rem;text-align:center;text-decoration:none!important;font-weight:750;line-height:1.08;transition:transform .06s ease,border-color .06s ease,box-shadow .06s ease,filter .06s ease;cursor:pointer;touch-action:manipulation;}
        .iars-gantt-month-box:hover {transform:translateY(-1px);box-shadow:0 2px 7px rgba(15,23,42,.12);filter:brightness(.99);}
        .iars-gantt-month-box:active {transform:translateY(0) scale(.985);box-shadow:none;}
        .iars-gantt-month-box:focus-visible {outline:3px solid rgba(23,92,211,.25);outline-offset:1px;}
        .iars-gantt-month-stage {font-size:.70rem;font-weight:850;}
        .iars-gantt-month-auditor {font-size:.69rem;font-weight:800;}
        .iars-gantt-month-date {font-size:.60rem;font-weight:700;white-space:nowrap;letter-spacing:-.035em;}
        .iars-gantt-month-box.scheduled {background:#EAF2FF;color:#1E3A8A;border-color:#3B82F6;}
        .iars-gantt-month-box.in-progress {background:#FFF4E5;color:#7C2D12;border-color:#F59E0B;}
        .iars-gantt-month-box.done {background:#DCFCE7;color:#14532D;border-color:#22C55E;}
        .iars-gantt-month-box.for-frs {background:#ECFEFF;color:#164E63;border-color:#0891B2;}
        .iars-gantt-month-box.frs {background:#D1FAE5;color:#064E3B;border-color:#047857;}
        .iars-gantt-month-box.overdue,.iars-gantt-month-box.overdue-irs,.iars-gantt-month-box.overdue-frs {background:#B91C1C;color:#FFFFFF;border-color:#991B1B;}
        .iars-gantt-month-box.empty {background:#FAFBFC;color:#667085;border-color:#CBD5E1;}
        .iars-gantt-month-na {display:flex;align-items:center;justify-content:center;min-height:68px;color:#98A2B3;font-weight:700;}
        .iars-gantt-legend {display:flex;flex-wrap:wrap;gap:.42rem;margin:.2rem 0 .55rem;}
        .iars-gantt-chip {display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:.28rem .62rem;font-size:.74rem;font-weight:800;border:1px solid transparent;}
        .iars-gantt-chip.scheduled {background:#EAF2FF;color:#1E3A8A;border-color:#3B82F6;}
        .iars-gantt-chip.in-progress {background:#FFF4E5;color:#7C2D12;border-color:#F59E0B;}
        .iars-gantt-chip.done {background:#DCFCE7;color:#14532D;border-color:#22C55E;}
        .iars-gantt-chip.for-frs {background:#ECFEFF;color:#164E63;border-color:#0891B2;}
        .iars-gantt-chip.frs {background:#D1FAE5;color:#064E3B;border-color:#047857;}
        .iars-gantt-chip.overdue {background:#B91C1C;color:#FFFFFF;border-color:#991B1B;}
        </style>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def _safe_container(*, key: str | None = None, border: bool = False) -> Iterator[Any]:
    try:
        ctx = st.container(key=key, border=border)
    except TypeError:
        ctx = st.container()
    with ctx:
        yield ctx


@contextmanager
def _safe_popover(label: str, *, key: str) -> Iterator[Any]:
    try:
        ctx = st.popover(label, width="stretch", key=key, on_change="rerun")
    except TypeError:
        try:
            ctx = st.popover(label, use_container_width=True)
        except TypeError:
            ctx = st.popover(label)
    with ctx:
        yield ctx


def _empty_grid_selection() -> dict[str, dict[str, list[Any]]]:
    return {"selection": {"rows": [], "columns": [], "cells": []}}


def _reset_gantt_grid_selection() -> None:
    """Clear the selected grid cell without changing the browser URL or page."""
    try:
        st.session_state[GANTT_GRID_KEY] = _empty_grid_selection()
    except Exception:
        pass


def _dismiss_month_editor() -> None:
    st.session_state.pop(GANTT_PENDING_EDIT_KEY, None)
    _reset_gantt_grid_selection()


def _finish_month_editor() -> None:
    st.session_state.pop(GANTT_PENDING_EDIT_KEY, None)
    _reset_gantt_grid_selection()
    st.rerun()


def _open_month_editor_dialog(
    client: Any,
    *,
    master: dict[str, Any],
    entry: dict[str, Any] | None,
    year: int,
    month: int,
    holiday_rows: list[dict[str, Any]],
    admin: bool,
    current_user_name: str,
    auditor_options: list[str],
) -> None:
    dialog_factory = getattr(st, "dialog", None)
    title = f"{month_name[month]} Audit Schedule"
    if callable(dialog_factory):
        try:
            decorator = dialog_factory(
                title,
                width="small",
                on_dismiss=_dismiss_month_editor,
            )
        except TypeError:
            decorator = dialog_factory(title)

        @decorator
        def _dialog() -> None:
            st.markdown('<div class="iars-gantt-month-editor-marker"></div>', unsafe_allow_html=True)
            _render_month_editor(
                client,
                master=master,
                entry=entry,
                year=year,
                month=month,
                holiday_rows=holiday_rows,
                admin=admin,
                current_user_name=current_user_name,
                auditor_options=auditor_options,
            )

        _dialog()
        return

    # Compatibility fallback for older/test Streamlit environments.
    with _safe_container(border=True):
        st.markdown(f"### {title}")
        _render_month_editor(
            client,
            master=master,
            entry=entry,
            year=year,
            month=month,
            holiday_rows=holiday_rows,
            admin=admin,
            current_user_name=current_user_name,
            auditor_options=auditor_options,
        )


def _render_month_editor(
    client: Any,
    *,
    master: dict[str, Any],
    entry: dict[str, Any] | None,
    year: int,
    month: int,
    holiday_rows: list[dict[str, Any]],
    admin: bool,
    current_user_name: str,
    auditor_options: list[str],
) -> None:
    master_id = str(master.get("id") or "")
    unique = re.sub(r"[^a-zA-Z0-9]", "", master_id)[-16:] + f"_{year}_{month}"
    due_date = month_end_date(year, month)
    today = _today_pht()
    st.markdown(
        f"**{html.escape(_clean_text(master.get('custodian')))}**  \n"
        f"{html.escape(_clean_text(master.get('audit_task')))} · {_format_accountability(master.get('accountability'))}"
    )

    # Admin/Supervisor can create or edit every monthly record, including
    # historical audit and report stages from previous months.
    if admin:
        options = list(dict.fromkeys(
            [name for name in auditor_options if _clean_text(name)]
            + ([_clean_text((entry or {}).get("auditor_full_name"))] if entry else [])
        ))
        options = [name for name in options if name]
        if not options:
            st.error("No auditor account is available for assignment.")
            return

        assigned = _clean_text((entry or {}).get("auditor_full_name"))
        selected_index = options.index(assigned) if assigned in options else 0
        current_stage = _display_stage(report_stage_info(entry or {}, holiday_rows).stage) if entry else "Scheduled"
        status_options = list(DISPLAY_STATUSES)
        status_index = status_options.index(current_stage) if current_stage in status_options else 0
        existing_audit_date = _parse_date((entry or {}).get("accomplished_date")) or today
        existing_irs_date = _parse_date((entry or {}).get("initial_report_submitted_at")) or today
        existing_frs_date = _parse_date((entry or {}).get("final_report_submitted_at")) or today

        auditor = st.selectbox(
            "Auditor",
            options,
            index=selected_index,
            format_func=lambda name: f"{name} — {nickname_for(name)}",
            key=f"gantt_admin_auditor_{unique}",
        )
        selected_status = st.selectbox(
            "Status",
            status_options,
            index=status_index,
            key=f"gantt_admin_status_{unique}",
        )
        st.caption(f"Monthly due date: {_box_date(due_date)}")

        audit_date: date | None = None
        initial_date: date | None = None
        final_date: date | None = None
        if selected_status in {"Done", "Overdue: IRS", "For FRS", "Overdue: FRS", "FRS"}:
            audit_date = st.date_input(
                "Date of Audit",
                value=min(existing_audit_date, today),
                max_value=today,
                key=f"gantt_admin_audit_date_{unique}",
            )
        if selected_status in {"For FRS", "Overdue: FRS", "FRS"}:
            initial_default = max(audit_date or existing_audit_date, min(existing_irs_date, today))
            initial_date = st.date_input(
                "IRS Submission Date",
                value=initial_default,
                min_value=audit_date if audit_date else None,
                max_value=today,
                key=f"gantt_admin_irs_date_{unique}",
            )
        if selected_status == "FRS":
            final_default = max(initial_date or existing_irs_date, min(existing_frs_date, today))
            final_date = st.date_input(
                "FRS Submission Date",
                value=final_default,
                min_value=initial_date if initial_date else None,
                max_value=today,
                key=f"gantt_admin_frs_date_{unique}",
            )

        if selected_status in {"Done", "Overdue: IRS", "For FRS", "Overdue: FRS", "FRS"}:
            st.caption("Dates default to today and may be edited backward. Future dates are blocked.")
        remarks = st.text_area(
            "Audit Remarks / Reference",
            value=_clean_text((entry or {}).get("remarks")),
            key=f"gantt_admin_remarks_{unique}",
        )
        save_label = "Create Monthly Record" if entry is None else "Save Monthly Changes"
        if st.button(save_label, type="primary", key=f"gantt_admin_save_{unique}", use_container_width=True):
            try:
                admin_save_schedule_entry(
                    client,
                    entry=entry,
                    master_id=master_id,
                    schedule_year=year,
                    schedule_month=month,
                    auditor_full_name=auditor,
                    status=selected_status,
                    accomplished_date=audit_date,
                    initial_report_submitted_at=initial_date,
                    final_report_submitted_at=final_date,
                    remarks=remarks,
                    actor=current_user_name,
                    holiday_rows=holiday_rows,
                )
                st.success(f"Monthly record saved as {selected_status}.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))

        if entry is None:
            return
        if st.button("Delete Monthly Assignment", key=f"gantt_delete_{unique}", use_container_width=True):
            try:
                delete_schedule_entry(client, str(entry.get("id") or ""))
                st.success("Monthly assignment deleted.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))
        return

    # Auditor workflow.
    if entry is None:
        st.caption("No audit assignment for your account.")
        return

    stage = report_stage_info(entry, holiday_rows)
    assigned = _clean_text(entry.get("auditor_full_name"))
    st.caption(f"Assigned auditor: {assigned} — {nickname_for(assigned)}")
    if _name_key(assigned) != _name_key(current_user_name):
        st.info("This audit is assigned to another auditor.")
        return

    if effective_status(entry) != "Done":
        if _clean_text(entry.get("status")) != "In Progress":
            if st.button("Start Audit — In Progress", key=f"gantt_start_{unique}", use_container_width=True):
                try:
                    mark_audit_in_progress(
                        client,
                        entry_id=str(entry.get("id") or ""),
                        assigned_auditor=assigned,
                        current_user_name=current_user_name,
                        remarks=_clean_text(entry.get("remarks")),
                    )
                    st.success("Audit marked In Progress.")
                    _finish_month_editor()
                except Exception as exc:
                    st.error(str(exc))
        with st.form(f"gantt_done_{unique}"):
            audit_date = st.date_input(
                "Date of Audit",
                value=today,
                max_value=today,
                key=f"gantt_audit_date_{unique}",
            )
            remarks = st.text_area(
                "Audit Remarks / Reference",
                value=_clean_text(entry.get("remarks")),
                key=f"gantt_done_remarks_{unique}",
            )
            mark_done = st.form_submit_button("Done — Audit Completed", type="primary", use_container_width=True)
        if mark_done:
            try:
                update_auditor_accomplishment(
                    client,
                    entry_id=str(entry.get("id") or ""),
                    assigned_auditor=assigned,
                    current_user_name=current_user_name,
                    status="Done",
                    accomplished_date=audit_date,
                    remarks=remarks,
                )
                st.success("Audit marked Done. The five-working-day initial-report period has started.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))
        return

    existing_audit_date = _parse_date(entry.get("accomplished_date")) or today
    with st.form(f"gantt_edit_done_date_{unique}"):
        edited_audit_date = st.date_input(
            "Date of Audit",
            value=min(existing_audit_date, today),
            max_value=today,
            key=f"gantt_edit_done_date_value_{unique}",
        )
        remarks = st.text_area(
            "Audit Remarks / Reference",
            value=_clean_text(entry.get("remarks")),
            key=f"gantt_edit_done_remarks_{unique}",
        )
        update_date = st.form_submit_button("Update Date of Audit", use_container_width=True)
    if update_date:
        try:
            update_auditor_accomplishment(
                client,
                entry_id=str(entry.get("id") or ""),
                assigned_auditor=assigned,
                current_user_name=current_user_name,
                status="Done",
                accomplished_date=edited_audit_date,
                remarks=remarks,
            )
            st.success("Date of Audit updated.")
            _finish_month_editor()
        except Exception as exc:
            st.error(str(exc))

    if stage.stage in {"Done", "Overdue: IRS"}:
        st.write(f"**Initial report deadline:** {_display_date(stage.deadline)}")
        if stage.overdue:
            st.error("Overdue: IRS — submit the initial report now.")
        with st.form(f"gantt_initial_report_{unique}"):
            reference = st.text_input(
                "Initial Report Reference / Remarks",
                value=_clean_text(entry.get("initial_report_reference")),
                key=f"gantt_initial_ref_{unique}",
            )
            submit_initial = st.form_submit_button(
                "Submit Initial Report",
                type="primary",
                use_container_width=True,
            )
        if submit_initial:
            try:
                submit_initial_report(
                    client,
                    entry_id=str(entry.get("id") or ""),
                    assigned_auditor=assigned,
                    current_user_name=current_user_name,
                    reference=reference,
                )
                st.success("Initial report submitted. The five-working-day FRS period has started.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))
        return

    st.write(f"**Initial report submitted:** {_display_date(entry.get('initial_report_submitted_at'))}")
    if stage.stage in {"For FRS", "Overdue: FRS"}:
        st.write(f"**FRS deadline:** {_display_date(stage.deadline)}")
        if stage.overdue:
            st.error("Overdue: FRS — waiting for the Admin/Supervisor to submit the final report.")
        else:
            st.info("Initial report submitted. Waiting for the Admin/Supervisor to complete the FRS.")
        return

    if stage.stage == "FRS":
        st.success(f"FRS submitted on {_display_date(entry.get('final_report_submitted_at'))}.")
        if _clean_text(entry.get("final_report_reference")):
            st.caption(_clean_text(entry.get("final_report_reference")))


def _filter_masters(
    masters: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    holiday_rows: list[dict[str, Any]],
    *,
    admin: bool,
    current_user_name: str,
    custodian_filter: str,
    auditor_filter: str,
    status_filter: str,
    month_filter: int | None,
    sort_by: str,
    sort_desc: bool,
) -> list[dict[str, Any]]:
    lookup = _entry_lookup(entries)
    current_key = _name_key(current_user_name)
    filtered: list[dict[str, Any]] = []
    for master in masters:
        master_id = str(master.get("id") or "")
        month_entries = [lookup.get((master_id, month)) for month in MONTHS]
        visible_entries = [entry for entry in month_entries if entry]
        if not admin:
            visible_entries = [
                entry for entry in visible_entries
                if _name_key(entry.get("auditor_full_name")) == current_key
            ]
            if not visible_entries:
                continue
        if custodian_filter != "All" and _clean_text(master.get("custodian")) != custodian_filter:
            continue
        if admin and auditor_filter != "All" and not any(
            _name_key(entry.get("auditor_full_name")) == _name_key(auditor_filter)
            for entry in visible_entries
        ):
            continue
        if status_filter != "All" and not any(
            _display_stage(report_stage_info(entry, holiday_rows).stage) == status_filter
            for entry in visible_entries
        ):
            continue
        if month_filter and not any(
            int(entry.get("schedule_month") or 0) == month_filter for entry in visible_entries
        ):
            continue
        filtered.append(master)

    def first_entry(master: dict[str, Any]) -> dict[str, Any] | None:
        master_id = str(master.get("id") or "")
        candidates = [lookup.get((master_id, month)) for month in MONTHS]
        candidates = [entry for entry in candidates if entry]
        if not admin:
            candidates = [entry for entry in candidates if _name_key(entry.get("auditor_full_name")) == current_key]
        return candidates[0] if candidates else None

    def sort_value(master: dict[str, Any]):
        first = first_entry(master) or {}
        if sort_by == "Auditor":
            return _clean_text(first.get("auditor_full_name")).casefold()
        if sort_by == "Status":
            rank = {
                "Overdue": 0,
                "Overdue: IRS": 1,
                "Overdue: FRS": 2,
                "For FRS": 3,
                "Scheduled": 4,
                "In Progress": 5,
                "Done": 6,
                "FRS": 7,
            }
            return rank.get(_display_stage(report_stage_info(first, holiday_rows).stage), 9)
        if sort_by == "Month":
            return int(first.get("schedule_month") or 99)
        return _clean_text(master.get("custodian")).casefold()

    filtered.sort(key=sort_value, reverse=sort_desc)
    return filtered


def _month_cell_html(
    *,
    master_id: str,
    year: int,
    month: int,
    entry: dict[str, Any] | None,
    holiday_rows: list[dict[str, Any]],
    clickable: bool,
) -> str:
    if entry is None and not clickable:
        return '<div class="iars-gantt-month-na">—</div>'

    label, slug = _month_box_label(entry, holiday_rows)
    lines = label.splitlines()
    content_parts: list[str] = []
    for line_index, line in enumerate(lines):
        safe = html.escape(line)
        if line_index == 0:
            css_class = "iars-gantt-month-stage"
        elif line_index == 1 and ":" not in line:
            css_class = "iars-gantt-month-auditor"
        else:
            css_class = "iars-gantt-month-date"
        content_parts.append(f'<span class="{css_class}">{safe}</span>')
    content = "".join(content_parts)
    if not clickable:
        return f'<div class="iars-gantt-month-box {html.escape(slug)}">{content}</div>'
    href = html.escape(_gantt_edit_href(master_id, year, month), quote=True)
    return (
        f'<a class="iars-gantt-month-box {html.escape(slug)}" '
        f'href="{href}" aria-label="Edit {html.escape(month_name[month])} audit schedule">{content}</a>'
    )


def _gantt_body_viewport_height(row_count: int) -> int:
    return min(560, max(190, 20 + int(row_count) * 82))


def _build_gantt_table_html(
    filtered: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    holiday_rows: list[dict[str, Any]],
    *,
    year: int,
    admin: bool,
    current_user_name: str,
    done_counts: dict[str, int],
) -> str:
    """Build one native-DOM table with a frozen header and clickable links.

    Because the HTML is inserted directly into Streamlit's main document,
    month-box links are not blocked by an iframe sandbox and respond immediately.
    """
    lookup = _entry_lookup(entries)
    headers = [
        "Company",
        "Custodian",
        "Audit Task",
        "Accountability",
        "Frequency",
        *[month_name[month] for month in MONTHS],
    ]
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body_rows: list[str] = []
    current_key = _name_key(current_user_name)

    for master in filtered:
        master_id = str(master.get("id") or "")
        static_cells = [
            ("iars-static-cell", _clean_text(master.get("company_department"))),
            ("iars-static-cell", _clean_text(master.get("custodian"))),
            ("iars-static-cell", _clean_text(master.get("audit_task"))),
            ("iars-accountability", _format_accountability(master.get("accountability"))),
            ("iars-frequency", f"{done_counts.get(master_id, 0)}×"),
        ]
        cells = [
            f'<td class="{css_class}" title="{html.escape(value, quote=True)}">{html.escape(value)}</td>'
            for css_class, value in static_cells
        ]
        for month in MONTHS:
            entry = lookup.get((master_id, month))
            assigned_to_current = bool(entry) and _name_key(entry.get("auditor_full_name")) == current_key
            visible_entry = entry if (admin or assigned_to_current) else None
            clickable = admin or assigned_to_current
            cells.append(
                "<td>"
                + _month_cell_html(
                    master_id=master_id,
                    year=year,
                    month=month,
                    entry=visible_entry,
                    holiday_rows=holiday_rows,
                    clickable=clickable,
                )
                + "</td>"
            )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        '<div class="iars-gantt-native-shell">'
        '<div class="iars-gantt-native-scroll" role="region" aria-label="Yearly Audit Gantt">'
        '<table class="iars-gantt-native-table">'
        f'<thead><tr>{header_html}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        '</table></div></div>'
    )


def _grid_map_key(grid_key: str) -> str:
    return f"{grid_key}{GANTT_GRID_MAP_SUFFIX}"


def _grid_selection_callback(grid_key: str = GANTT_GRID_KEY) -> None:
    """Translate one native dataframe cell selection into an editor request.

    This callback runs before the app rerenders. It keeps ``main_navigation``
    unchanged, so selecting a month never performs a browser navigation and
    can never send the user back to Dashboard.
    """
    try:
        state = st.session_state.get(grid_key, {})
        selection = state.get("selection", {}) if hasattr(state, "get") else {}
        cells = selection.get("cells", []) if hasattr(selection, "get") else []
        mapping = st.session_state.get(_grid_map_key(grid_key), {})
        if cells and isinstance(mapping, dict):
            row_index, column_name = cells[-1]
            month_by_column = mapping.get("month_by_column", {})
            master_ids = mapping.get("master_ids", [])
            clickable_cells = set(mapping.get("clickable_cells", []))
            cell_token = f"{int(row_index)}|{str(column_name)}"
            month = month_by_column.get(str(column_name))
            if (
                month in MONTHS
                and 0 <= int(row_index) < len(master_ids)
                and cell_token in clickable_cells
            ):
                st.session_state[GANTT_PENDING_EDIT_KEY] = {
                    "master_id": str(master_ids[int(row_index)]),
                    "year": int(mapping.get("year") or _today_pht().year),
                    "month": int(month),
                }
        # Clearing in the callback is supported because the widget has not yet
        # been recreated on the new run. This makes every click immediately
        # available, including two consecutive clicks on the same month cell.
        st.session_state[grid_key] = _empty_grid_selection()
    except Exception:
        # A selection must never break the Gantt page. The next click can retry.
        try:
            st.session_state[grid_key] = _empty_grid_selection()
        except Exception:
            pass


def _gantt_cell_palette(slug: str) -> str:
    palettes = {
        "scheduled": "background-color:#EAF2FF;color:#1E3A8A;font-weight:700;border:1px solid #3B82F6;",
        "in-progress": "background-color:#FFF4E5;color:#7C2D12;font-weight:700;border:1px solid #F59E0B;",
        "done": "background-color:#DCFCE7;color:#14532D;font-weight:700;border:1px solid #22C55E;",
        "for-frs": "background-color:#ECFEFF;color:#164E63;font-weight:700;border:1px solid #0891B2;",
        "frs": "background-color:#D1FAE5;color:#064E3B;font-weight:700;border:1px solid #047857;",
        "overdue": "background-color:#B91C1C;color:#FFFFFF;font-weight:800;border:1px solid #991B1B;",
        "overdue-irs": "background-color:#B91C1C;color:#FFFFFF;font-weight:800;border:1px solid #991B1B;",
        "overdue-frs": "background-color:#B91C1C;color:#FFFFFF;font-weight:800;border:1px solid #991B1B;",
        "empty": "background-color:#FAFBFC;color:#667085;font-weight:650;border:1px solid #CBD5E1;",
        "na": "background-color:#FFFFFF;color:#98A2B3;",
    }
    layout = "white-space:pre-line;line-height:1.16;word-break:normal;overflow-wrap:normal;"
    return palettes.get(slug, palettes["empty"]) + layout



def _gantt_component_click_callback() -> None:
    """Open a month editor only for a real pointer click from the V2 grid.

    Keyboard arrow navigation is intentionally kept entirely in the browser and
    never calls Streamlit, so moving the focus rectangle cannot open a dialog or
    rerun the page.
    """
    try:
        state = st.session_state.get(GANTT_COMPONENT_KEY)
        clicked = getattr(state, "cell_click", None)
        if clicked is None and hasattr(state, "get"):
            clicked = state.get("cell_click")
        if not isinstance(clicked, dict):
            return
        master_id = _clean_text(clicked.get("master_id"))
        year = int(clicked.get("year"))
        month = int(clicked.get("month"))
        if not master_id or month not in MONTHS:
            return
        st.session_state[GANTT_PENDING_EDIT_KEY] = {
            "master_id": master_id,
            "year": year,
            "month": month,
        }
    except Exception:
        return


def _get_gantt_grid_component() -> Any | None:
    """Return the V2 interactive Gantt grid when supported by Streamlit."""
    global _GANTT_GRID_COMPONENT
    if _GANTT_GRID_COMPONENT is not None:
        return _GANTT_GRID_COMPONENT

    components = getattr(st, "components", None)
    v2 = getattr(components, "v2", None)
    register = getattr(v2, "component", None)
    if not callable(register):
        return None

    component_html = '<div class="iars-gantt-v2-root"></div>'
    component_css = r'''
.iars-gantt-v2-root{width:100%;font-family:var(--st-font);color:#23324A;}
.iars-gantt-v2-shell{border:1px solid #D9E2EE;border-radius:14px;overflow:hidden;background:#FFF;box-shadow:0 1px 2px rgba(16,24,40,.04);}
.iars-gantt-v2-scroll{width:100%;height:100%;overflow:auto;position:relative;overscroll-behavior:contain;scrollbar-gutter:stable;background:#FFF;outline:none;}
.iars-gantt-v2-table{border-collapse:separate;border-spacing:0;table-layout:fixed;width:1900px;min-width:1900px;margin:0;font-size:.72rem;color:#23324A;}
.iars-gantt-v2-table th,.iars-gantt-v2-table td{box-sizing:border-box;width:92px;min-width:92px;max-width:92px;border-right:1px solid #D9E2EE;border-bottom:1px solid #D9E2EE;padding:.30rem .30rem;overflow:hidden;vertical-align:middle;background:#FFF;}
.iars-gantt-v2-table th:nth-child(n+6),.iars-gantt-v2-table td:nth-child(n+6){width:120px;min-width:120px;max-width:120px;padding-left:.20rem;padding-right:.20rem;}
.iars-gantt-v2-table thead th{position:sticky;top:0;z-index:100;height:54px;background:#EAF0F8;color:#0B2B55;text-align:center;font-weight:800;line-height:1.12;overflow-wrap:anywhere;box-shadow:0 2px 0 #C8D4E3;}
.iars-gantt-v2-table tbody td{height:108px;line-height:1.15;}
.iars-gantt-v2-table tbody tr:hover td{background:#F8FAFC;}
.iars-gantt-v2-table th:nth-child(1),.iars-gantt-v2-table td:nth-child(1){position:sticky;left:0;}
.iars-gantt-v2-table th:nth-child(2),.iars-gantt-v2-table td:nth-child(2){position:sticky;left:92px;}
.iars-gantt-v2-table th:nth-child(3),.iars-gantt-v2-table td:nth-child(3){position:sticky;left:184px;}
.iars-gantt-v2-table th:nth-child(4),.iars-gantt-v2-table td:nth-child(4){position:sticky;left:276px;}
.iars-gantt-v2-table th:nth-child(5),.iars-gantt-v2-table td:nth-child(5){position:sticky;left:368px;box-shadow:2px 0 0 #C8D4E3;}
.iars-gantt-v2-table thead th:nth-child(-n+5){z-index:130;background:#EAF0F8;}
.iars-gantt-v2-table tbody td:nth-child(-n+5){z-index:40;background:#FFF;}
.iars-gantt-v2-table tbody tr:hover td:nth-child(-n+5){background:#F8FAFC;}
.iars-gantt-v2-cell{position:relative;text-align:center;outline:none;}
.iars-gantt-v2-cell:focus-visible{box-shadow:inset 0 0 0 2px #D39A16,inset 0 0 0 4px rgba(211,154,22,.18);}
.iars-gantt-v2-static{font-weight:600;font-size:.66rem;text-align:left;white-space:normal;overflow-wrap:anywhere;}
.iars-gantt-v2-accountability{font-weight:800;font-size:.64rem;text-align:center;white-space:nowrap;}
.iars-gantt-v2-frequency{font-weight:800;font-size:.68rem;text-align:center;white-space:nowrap;}
.iars-gantt-v2-month-box{display:flex;min-height:104px;width:100%;box-sizing:border-box;flex-direction:column;align-items:center;justify-content:center;gap:.08rem;border:1px solid #CBD5E1;border-radius:9px;padding:.24rem .12rem;text-align:center;font-weight:750;line-height:1.08;cursor:pointer;user-select:none;transition:border-color .06s ease,box-shadow .06s ease,filter .06s ease;}
.iars-gantt-v2-month-box:hover{box-shadow:0 2px 7px rgba(15,23,42,.12);filter:brightness(.99);}
.iars-gantt-v2-month-box:active{transform:scale(.988);box-shadow:none;}
.iars-gantt-v2-month-line{display:block;width:100%;white-space:nowrap;overflow:hidden;text-overflow:clip;}
.iars-gantt-v2-month-line.stage{font-size:.67rem;font-weight:850;}
.iars-gantt-v2-month-line.auditor{font-size:.66rem;font-weight:800;}
.iars-gantt-v2-month-line.date{font-size:.60rem;font-weight:700;letter-spacing:-.035em;}
.iars-gantt-v2-month-box.scheduled{background:#EAF2FF;color:#1E3A8A;border-color:#3B82F6;}
.iars-gantt-v2-month-box.in-progress{background:#FFF4E5;color:#7C2D12;border-color:#F59E0B;}
.iars-gantt-v2-month-box.done{background:#DCFCE7;color:#14532D;border-color:#22C55E;}
.iars-gantt-v2-month-box.for-frs{background:#ECFEFF;color:#164E63;border-color:#0891B2;}
.iars-gantt-v2-month-box.frs{background:#D1FAE5;color:#064E3B;border-color:#047857;}
.iars-gantt-v2-month-box.overdue,.iars-gantt-v2-month-box.overdue-irs,.iars-gantt-v2-month-box.overdue-frs{background:#B91C1C;color:#FFF;border-color:#991B1B;}
.iars-gantt-v2-month-box.empty{background:#FAFBFC;color:#667085;border-color:#CBD5E1;}
.iars-gantt-v2-month-na{display:flex;align-items:center;justify-content:center;min-height:94px;color:#98A2B3;font-weight:700;}
'''
    component_js = r'''
export default function(component) {
  const { data, setTriggerValue, parentElement } = component;
  const root = parentElement.querySelector('.iars-gantt-v2-root');
  if (!root) return;

  const payload = data || {};
  const storageKey = String(payload.storage_key || 'iars-gantt-grid-v4544');
  const rows = Array.isArray(payload.rows) ? payload.rows : [];
  const columns = Array.isArray(payload.columns) ? payload.columns : [];
  const viewportHeight = Number(payload.viewport_height || 560);

  root.replaceChildren();
  const shell = document.createElement('div');
  shell.className = 'iars-gantt-v2-shell';
  const scroll = document.createElement('div');
  scroll.className = 'iars-gantt-v2-scroll';
  scroll.style.height = `${viewportHeight}px`;
  scroll.setAttribute('role', 'region');
  scroll.setAttribute('aria-label', 'Yearly Audit Gantt');

  const table = document.createElement('table');
  table.className = 'iars-gantt-v2-table';
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  columns.forEach((column) => {
    const th = document.createElement('th');
    th.textContent = String(column.label || column.name || '');
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  const cellMatrix = [];

  function focusCell(rowIndex, colIndex) {
    if (rowIndex < 0 || rowIndex >= cellMatrix.length) return;
    const row = cellMatrix[rowIndex] || [];
    if (colIndex < 0 || colIndex >= row.length) return;
    const target = row[colIndex];
    if (!target) return;
    target.focus({ preventScroll: true });
    target.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }

  rows.forEach((rowData, rowIndex) => {
    const tr = document.createElement('tr');
    const rowCells = [];
    const cells = Array.isArray(rowData.cells) ? rowData.cells : [];
    cells.forEach((cellData, colIndex) => {
      const td = document.createElement('td');
      td.className = 'iars-gantt-v2-cell';
      td.tabIndex = 0;
      td.dataset.row = String(rowIndex);
      td.dataset.col = String(colIndex);
      td.addEventListener('pointerdown', (event) => {
        if (Number(event.button ?? 0) === 0) td.focus({ preventScroll: true });
      });
      td.addEventListener('keydown', (event) => {
        let nextRow = rowIndex;
        let nextCol = colIndex;
        if (event.key === 'ArrowLeft') nextCol -= 1;
        else if (event.key === 'ArrowRight') nextCol += 1;
        else if (event.key === 'ArrowUp') nextRow -= 1;
        else if (event.key === 'ArrowDown') nextRow += 1;
        else if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          return;
        } else {
          return;
        }
        event.preventDefault();
        focusCell(nextRow, nextCol);
      });

      const kind = String(cellData.kind || 'static');
      if (kind === 'month') {
        if (cellData.visible === false) {
          const na = document.createElement('div');
          na.className = 'iars-gantt-v2-month-na';
          na.textContent = '—';
          td.appendChild(na);
        } else {
          const box = document.createElement('div');
          box.className = `iars-gantt-v2-month-box ${String(cellData.slug || 'empty')}`;
          box.setAttribute('role', 'presentation');
          const lines = Array.isArray(cellData.lines) ? cellData.lines : [];
          lines.forEach((value, lineIndex) => {
            const span = document.createElement('span');
            span.className = 'iars-gantt-v2-month-line ' + (lineIndex === 0 ? 'stage' : (lineIndex === 1 && lines.length >= 3 && !String(value).includes(':') ? 'auditor' : 'date'));
            span.textContent = String(value || '');
            box.appendChild(span);
          });

          let pointerArmed = false;
          box.addEventListener('pointerdown', (event) => {
            if (Number(event.button ?? 0) === 0) pointerArmed = true;
          });
          box.addEventListener('pointercancel', () => { pointerArmed = false; });
          box.addEventListener('click', (event) => {
            const genuinePointer = pointerArmed || Number(event.detail || 0) > 0;
            pointerArmed = false;
            td.focus({ preventScroll: true });
            if (!genuinePointer || !cellData.clickable) return;
            event.preventDefault();
            setTriggerValue('cell_click', {
              master_id: String(rowData.master_id || ''),
              year: Number(cellData.year || 0),
              month: Number(cellData.month || 0),
            });
          });
          td.appendChild(box);
        }
      } else {
        const div = document.createElement('div');
        div.className = kind === 'accountability'
          ? 'iars-gantt-v2-accountability'
          : (kind === 'frequency' ? 'iars-gantt-v2-frequency' : 'iars-gantt-v2-static');
        div.textContent = String(cellData.text || '');
        td.appendChild(div);
      }
      rowCells.push(td);
      tr.appendChild(td);
    });
    cellMatrix.push(rowCells);
    tbody.appendChild(tr);
  });

  table.appendChild(tbody);
  scroll.appendChild(table);
  shell.appendChild(scroll);
  root.appendChild(shell);

  window.__iarsGanttScrollState = window.__iarsGanttScrollState || {};
  let saved = window.__iarsGanttScrollState[storageKey] || null;
  if (!saved) {
    try {
      saved = JSON.parse(window.sessionStorage.getItem(storageKey) || 'null');
    } catch (_) {
      saved = null;
    }
  }
  if (saved && Number.isFinite(saved.left) && Number.isFinite(saved.top)) {
    requestAnimationFrame(() => {
      scroll.scrollLeft = saved.left;
      scroll.scrollTop = saved.top;
    });
  }
  let saveFrame = null;
  scroll.addEventListener('scroll', () => {
    if (saveFrame) cancelAnimationFrame(saveFrame);
    saveFrame = requestAnimationFrame(() => {
      const position = { left: scroll.scrollLeft, top: scroll.scrollTop };
      window.__iarsGanttScrollState[storageKey] = position;
      try {
        window.sessionStorage.setItem(storageKey, JSON.stringify(position));
      } catch (_) {}
    });
  }, { passive: true });

  return () => {
    if (saveFrame) cancelAnimationFrame(saveFrame);
  };
}
'''
    try:
        _GANTT_GRID_COMPONENT = register(
            "iars_gantt_pointer_grid_v4544",
            html=component_html,
            css=component_css,
            js=component_js,
            isolate_styles=True,
        )
    except Exception:
        return None
    return _GANTT_GRID_COMPONENT


def _build_gantt_component_payload(
    filtered: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    holiday_rows: list[dict[str, Any]],
    *,
    year: int,
    admin: bool,
    current_user_name: str,
    done_counts: dict[str, int],
) -> dict[str, Any]:
    """Build structured data for the click-only Gantt component."""
    lookup = _entry_lookup(entries)
    current_key = _name_key(current_user_name)
    columns = [
        {"name": "Company", "label": "Company"},
        {"name": "Custodian", "label": "Custodian"},
        {"name": "Audit Task", "label": "Audit Task"},
        {"name": "Accountability", "label": "Accountability"},
        {"name": "Frequency", "label": "Frequency"},
        *[{"name": month_name[month], "label": month_name[month]} for month in MONTHS],
    ]
    payload_rows: list[dict[str, Any]] = []
    for master in filtered:
        master_id = str(master.get("id") or "")
        cells: list[dict[str, Any]] = [
            {"kind": "static", "text": _clean_text(master.get("company_department"))},
            {"kind": "static", "text": _clean_text(master.get("custodian"))},
            {"kind": "static", "text": _clean_text(master.get("audit_task"))},
            {"kind": "accountability", "text": _format_accountability(master.get("accountability"))},
            {"kind": "frequency", "text": f"{done_counts.get(master_id, 0)}×"},
        ]
        for month in MONTHS:
            entry = lookup.get((master_id, month))
            assigned_to_current = bool(entry) and _name_key(entry.get("auditor_full_name")) == current_key
            visible_entry = entry if (admin or assigned_to_current) else None
            clickable = bool(admin or assigned_to_current)
            if visible_entry is None and not clickable:
                cells.append({
                    "kind": "month",
                    "visible": False,
                    "clickable": False,
                    "year": int(year),
                    "month": int(month),
                    "lines": [],
                    "slug": "na",
                })
                continue
            label, slug = _month_box_label(visible_entry, holiday_rows)
            cells.append({
                "kind": "month",
                "visible": True,
                "clickable": clickable,
                "year": int(year),
                "month": int(month),
                "lines": label.splitlines(),
                "slug": slug,
            })
        payload_rows.append({"master_id": master_id, "cells": cells})

    return {
        "columns": columns,
        "rows": payload_rows,
        "viewport_height": min(560, max(240, 58 + len(filtered) * 108)),
        "storage_key": f"iars-gantt-v4544-{int(year)}",
    }

def _build_native_gantt_dataframe(
    filtered: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    holiday_rows: list[dict[str, Any]],
    *,
    year: int,
    admin: bool,
    current_user_name: str,
    done_counts: dict[str, int],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Build the native Streamlit grid, styling matrix and click map."""
    lookup = _entry_lookup(entries)
    current_key = _name_key(current_user_name)
    rows: list[dict[str, str]] = []
    style_rows: list[dict[str, str]] = []
    master_ids: list[str] = []
    clickable_cells: list[str] = []
    month_by_column = {month_name[month]: month for month in MONTHS}

    for row_index, master in enumerate(filtered):
        master_id = str(master.get("id") or "")
        master_ids.append(master_id)
        row: dict[str, str] = {
            "Company": _clean_text(master.get("company_department")),
            "Custodian": _clean_text(master.get("custodian")),
            "Audit Task": _clean_text(master.get("audit_task")),
            "Accountability": _format_accountability(master.get("accountability")),
            "Frequency": f"{done_counts.get(master_id, 0)}×",
        }
        style_row = {column: "" for column in row}

        for month in MONTHS:
            column = month_name[month]
            entry = lookup.get((master_id, month))
            assigned_to_current = bool(entry) and _name_key(entry.get("auditor_full_name")) == current_key
            visible_entry = entry if (admin or assigned_to_current) else None
            clickable = bool(admin or assigned_to_current)
            if visible_entry is None and not clickable:
                row[column] = "—"
                slug = "na"
            else:
                label, slug = _month_box_label(visible_entry, holiday_rows)
                row[column] = label
            style_row[column] = _gantt_cell_palette(slug)
            if clickable:
                clickable_cells.append(f"{row_index}|{column}")
        rows.append(row)
        style_rows.append(style_row)

    data = pd.DataFrame(rows)
    style_matrix = pd.DataFrame(style_rows, columns=data.columns, index=data.index)
    mapping = {
        "year": int(year),
        "master_ids": master_ids,
        "month_by_column": month_by_column,
        "clickable_cells": clickable_cells,
    }
    return data, style_matrix, mapping


def _native_gantt_column_config() -> dict[str, Any]:
    config: dict[str, Any] = {
        "Company": st.column_config.TextColumn(
            "Company", width=112, pinned=True, alignment="center"
        ),
        "Custodian": st.column_config.TextColumn(
            "Custodian", width=108, pinned=True, alignment="center"
        ),
        "Audit Task": st.column_config.TextColumn(
            "Audit Task", width=104, pinned=True, alignment="center"
        ),
        "Accountability": st.column_config.TextColumn(
            "Accountability", width=100, pinned=True, alignment="center"
        ),
        "Frequency": st.column_config.TextColumn(
            "Frequency", width=82, pinned=True, alignment="center"
        ),
    }
    for month in MONTHS:
        config[month_name[month]] = st.column_config.TextColumn(
            month_name[month], width=112, alignment="center"
        )
    return config


def _pending_gantt_edit() -> tuple[str, int, int] | None:
    pending = st.session_state.get(GANTT_PENDING_EDIT_KEY)
    if not isinstance(pending, dict):
        return None
    try:
        master_id = _clean_text(pending.get("master_id"))
        year = int(pending.get("year"))
        month = int(pending.get("month"))
    except (TypeError, ValueError):
        return None
    if not master_id or month not in MONTHS:
        return None
    return master_id, year, month


def _render_matrix(
    client: Any,
    masters: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    holiday_rows: list[dict[str, Any]],
    *,
    year: int,
    admin: bool,
    current_user_name: str,
    auditor_options: list[str],
    custodian_filter: str,
    auditor_filter: str,
    status_filter: str,
    month_filter: int | None,
    sort_by: str,
    sort_desc: bool,
) -> list[dict[str, Any]]:
    filtered = _filter_masters(
        masters,
        entries,
        holiday_rows,
        admin=admin,
        current_user_name=current_user_name,
        custodian_filter=custodian_filter,
        auditor_filter=auditor_filter,
        status_filter=status_filter,
        month_filter=month_filter,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )
    if not filtered:
        st.info("No schedule matched the selected filters.")
        return []

    lookup = _entry_lookup(entries)
    done_counts = done_frequency_by_master(masters, entries)

    # V4.5.44: use a Components V2 grid so keyboard navigation remains a
    # browser-only action.  A Python rerun/editor request is emitted only by a
    # genuine pointer click on a colored month box.
    component = _get_gantt_grid_component()
    component_rendered = False
    if component is not None:
        payload = _build_gantt_component_payload(
            filtered,
            entries,
            holiday_rows,
            year=year,
            admin=admin,
            current_user_name=current_user_name,
            done_counts=done_counts,
        )
        try:
            component(
                data=payload,
                key=GANTT_COMPONENT_KEY,
                on_cell_click_change=_gantt_component_click_callback,
                width="stretch",
                height=int(payload["viewport_height"]) + 2,
            )
            component_rendered = True
        except Exception:
            component_rendered = False

    if not component_rendered:
        # Compatibility fallback for test/older Streamlit environments.  The
        # production requirements pin Streamlit 1.58, where V2 is available.
        data, style_matrix, selection_map = _build_native_gantt_dataframe(
            filtered,
            entries,
            holiday_rows,
            year=year,
            admin=admin,
            current_user_name=current_user_name,
            done_counts=done_counts,
        )
        st.session_state[_grid_map_key(GANTT_GRID_KEY)] = selection_map

        def _apply_grid_styles(_: pd.DataFrame) -> pd.DataFrame:
            return style_matrix

        styled = data.style.apply(_apply_grid_styles, axis=None)
        table_height = min(650, max(240, 58 + len(filtered) * 108))
        st.dataframe(
            styled,
            width="stretch",
            height=table_height,
            hide_index=True,
            column_config=_native_gantt_column_config(),
            key=GANTT_GRID_KEY,
            on_select=_grid_selection_callback,
            selection_mode="single-cell",
            row_height=108,
        )

    selected = _pending_gantt_edit()
    if selected:
        selected_master_id, selected_year, selected_month = selected
        master = next(
            (row for row in masters if str(row.get("id") or "") == selected_master_id),
            None,
        )
        if selected_year != year or master is None:
            _dismiss_month_editor()
        else:
            entry = lookup.get((selected_master_id, selected_month))
            assigned_to_current = bool(entry) and _name_key(entry.get("auditor_full_name")) == _name_key(current_user_name)
            if admin or assigned_to_current:
                _open_month_editor_dialog(
                    client,
                    master=master,
                    entry=entry,
                    year=year,
                    month=selected_month,
                    holiday_rows=holiday_rows,
                    admin=admin,
                    current_user_name=current_user_name,
                    auditor_options=auditor_options,
                )
            else:
                _dismiss_month_editor()
                st.warning("You can open only the monthly audit schedules assigned to your account.")

    st.caption(
        f"Showing all {len(filtered)} matching custodian record(s). Click the colored January–December schedule box to edit it. "
        "Arrow keys only move the focus inside the Gantt and do not open the schedule editor."
    )
    return filtered

def _load_gantt_data(client: Any, year: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        list_master_records(client, active_only=False),
        list_schedule_entries(client, year),
        list_holidays(client, year, active_only=True),
    )


def _alert_line(entry: dict[str, Any], masters: dict[str, dict[str, Any]], info: ReportStageInfo) -> str:
    master = masters.get(str(entry.get("master_id")), {})
    return (
        f"<li><strong>{html.escape(_clean_text(master.get('custodian')) or 'Custodian')}</strong> — "
        f"{html.escape(_clean_text(master.get('audit_task')) or 'Audit task')} · "
        f"{html.escape(info.stage)} · deadline {html.escape(_date_text(info.deadline) or '—')}</li>"
    )


def render_gantt_dashboard_alert(client: Any, current_user: dict[str, Any], *, admin: bool) -> None:
    _render_gantt_css()
    setup = gantt_setup_status(client)
    if not setup.ready:
        return
    current_name = _user_name(current_user)
    year = _today_pht().year
    try:
        entries = list_schedule_entries(client, year)
        holidays = list_holidays(client, year)
        masters = {str(row.get("id")): row for row in list_master_records(client, active_only=False)}
    except Exception:
        return
    if not admin:
        entries = [entry for entry in entries if _name_key(entry.get("auditor_full_name")) == _name_key(current_name)]

    infos = [(entry, report_stage_info(entry, holidays)) for entry in entries]
    if admin:
        red_stages = {"Overdue", "Overdue: FRS"}
        notice_stage = "For FRS"
        red_title = "⚠ Overdue audit / FRS notification"
    else:
        red_stages = {"Overdue", "Overdue: IRS"}
        notice_stage = "Done"
        red_title = "⚠ Overdue audit / initial-report notification"

    overdue = [(entry, info) for entry, info in infos if info.stage in red_stages]
    notices = [(entry, info) for entry, info in infos if info.stage == notice_stage]
    if overdue:
        lines = "".join(_alert_line(entry, masters, info) for entry, info in overdue[:5])
        st.markdown(
            f'<div class="iars-gantt-alert"><strong>{red_title}</strong>'
            f'<span>{len(overdue)} item(s) require immediate action.</span><ul>{lines}</ul>'
            '<div style="margin-top:.55rem;font-size:.78rem;opacity:.9;">Open Yearly Audit Gantt and click the month box to update it.</div></div>',
            unsafe_allow_html=True,
        )
    if notices:
        label = "final report" if admin else "initial report"
        st.markdown(
            f'<div class="iars-gantt-notice"><strong>📄 {len(notices)} {label} submission(s) pending</strong>'
            f'<span>The five-working-day period is running. Weekends and active non-working holidays are excluded.</span></div>',
            unsafe_allow_html=True,
        )


def render_gantt_dashboard_panel(client: Any, current_user: dict[str, Any], *, admin: bool) -> None:
    """Dashboard replacement for Recent Archive Activity.

    Administrators see overdue audit/report items. Auditors see the audit
    schedules assigned to them for the current Philippine month.
    """
    _render_gantt_css()
    with st.container(border=True):
        today = _today_pht()
        if admin:
            st.markdown('<div class="iars-gantt-dashboard-panel-title">Overdue Audit / FRS Notifications</div>', unsafe_allow_html=True)
            st.markdown('<div class="iars-gantt-dashboard-panel-subtitle">Audit and report deadlines that need administrator attention.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="iars-gantt-dashboard-panel-title">{html.escape(month_name[today.month])} Audit Schedule</div>', unsafe_allow_html=True)
            st.markdown('<div class="iars-gantt-dashboard-panel-subtitle">Monthly audit schedules assigned to your account.</div>', unsafe_allow_html=True)

        setup = gantt_setup_status(client)
        if not setup.ready:
            st.info("Audit schedule information is not available yet.")
            return
        try:
            entries = list_schedule_entries(client, today.year)
            holidays = list_holidays(client, today.year)
            masters = {str(row.get("id") or ""): row for row in list_master_records(client, active_only=False)}
        except Exception as exc:
            st.warning(f"Audit schedule information could not be loaded: {exc}")
            return

        current_name = _user_name(current_user)
        rows: list[tuple[dict[str, Any], ReportStageInfo]] = []
        for entry in entries:
            info = report_stage_info(entry, holidays, today=today)
            if admin:
                if info.stage in {"Overdue", "Overdue: FRS"}:
                    rows.append((entry, info))
            else:
                if (
                    int(entry.get("schedule_month") or 0) == today.month
                    and _name_key(entry.get("auditor_full_name")) == _name_key(current_name)
                ):
                    rows.append((entry, info))

        rows.sort(key=lambda pair: (pair[1].deadline or date.max, _clean_text(pair[0].get("auditor_full_name"))))
        if not rows:
            if admin:
                st.success("No overdue audit or report items at this time.")
            else:
                st.info(f"No audit schedule is assigned to you for {month_name[today.month]} {today.year}.")
            return

        cards: list[str] = []
        for entry, info in rows[:10]:
            master = masters.get(str(entry.get("master_id") or ""), {})
            custodian = _clean_text(master.get("custodian")) or "Custodian"
            task = _clean_text(master.get("audit_task")) or "Audit task"
            auditor = nickname_for(entry.get("auditor_full_name"))
            stage = _display_stage(info.stage)
            if stage == "FRS":
                date_meta = f"Submission Date: {_box_date(entry.get('final_report_submitted_at'))}"
            elif info.deadline:
                date_meta = f"Due: {_box_date(info.deadline)}"
            else:
                date_meta = f"Due: {_box_date(entry.get('planned_date'))}"
            overdue_class = " overdue" if info.overdue or stage.startswith("Overdue") else ""
            auditor_meta = f" · {html.escape(auditor)}" if admin else ""
            cards.append(
                f'<div class="iars-gantt-dashboard-item{overdue_class}">'
                f'<div class="title">{html.escape(custodian)} — {html.escape(task)}</div>'
                f'<div class="meta">{html.escape(date_meta)}{auditor_meta}</div>'
                f'<span class="stage">{html.escape(stage)}</span>'
                '</div>'
            )
        st.markdown('<div class="iars-gantt-dashboard-list">' + ''.join(cards) + '</div>', unsafe_allow_html=True)


def render_yearly_gantt_page(
    client: Any,
    current_user: dict[str, Any],
    *,
    admin: bool,
    auditor_options: list[str],
) -> None:
    _render_gantt_css()
    current_name = _user_name(current_user)
    st.markdown(
        '<div class="iars-gantt-title"><h2>Yearly Audit Gantt Schedule</h2>'
        '<p>Plan, update and monitor every monthly audit and report-submission stage.</p></div>',
        unsafe_allow_html=True,
    )
    setup = gantt_setup_status(client)
    if not setup.ready:
        if admin:
            st.warning(setup.message)
            st.code("SUPABASE_GANTT_V4_5_20_WORKFLOW_MIGRATION.sql", language=None)
        else:
            st.info("The Yearly Audit Gantt module is not yet available. Please contact the administrator.")
        return

    default_year = _today_pht().year
    years = list(range(default_year - 1, default_year + 4))
    year = int(st.selectbox("Schedule Year", years, index=1, key="iars_gantt_year_v4520"))
    try:
        masters, entries, holidays = _load_gantt_data(client, year)
    except Exception as exc:
        st.error(f"Unable to load the Yearly Audit Gantt: {exc}")
        return

    visible_entries = entries if admin else [
        entry for entry in entries if _name_key(entry.get("auditor_full_name")) == _name_key(current_name)
    ]
    stages = [report_stage_info(entry, holidays).stage for entry in visible_entries]
    metric_cols = st.columns(5)
    metric_cols[0].metric("Assigned" if not admin else "Scheduled", len(visible_entries))
    metric_cols[1].metric("Done", sum(effective_status(entry) == "Done" for entry in visible_entries))
    metric_cols[2].metric("For FRS", sum(stage == "For FRS" for stage in stages))
    metric_cols[3].metric("FRS", sum(stage == "FRS" for stage in stages))
    metric_cols[4].metric("Overdue", sum(stage in {"Overdue", "Overdue: IRS", "Overdue: FRS"} for stage in stages))


    custodian_options = ["All"] + sorted(
        {_clean_text(row.get("custodian")) for row in masters if _clean_text(row.get("custodian"))},
        key=str.casefold,
    )
    filter_cols = st.columns(5 if admin else 4)
    custodian_filter = filter_cols[0].selectbox("Custodian", custodian_options, key="iars_gantt_filter_custodian_v4520")
    offset = 1
    auditor_filter = "All"
    if admin:
        auditor_filter = filter_cols[1].selectbox(
            "Auditor",
            ["All"] + list(auditor_options),
            key="iars_gantt_filter_auditor_v4520",
        )
        offset = 2
    status_filter = filter_cols[offset].selectbox(
        "Status",
        ["All"] + DISPLAY_STATUSES,
        key="iars_gantt_filter_status_v4520",
    )
    month_label = filter_cols[offset + 1].selectbox(
        "Month",
        ["All"] + [month_name[m] for m in MONTHS],
        key="iars_gantt_filter_month_v4520",
    )
    sort_by = filter_cols[offset + 2].selectbox(
        "Sort by",
        ["Custodian", "Auditor", "Status", "Month"],
        key="iars_gantt_sort_by_v4520",
    )
    sort_desc = st.toggle("Descending order", value=False, key="iars_gantt_sort_desc_v4520")
    month_filter = None if month_label == "All" else list(month_name).index(month_label)
    st.caption("Month filter affects custodian rows only. All January–December columns remain visible for every matching row.")
    st.markdown(
        '<div class="iars-gantt-legend" aria-label="Gantt status color legend">'
        '<span class="iars-gantt-chip scheduled">Scheduled</span>'
        '<span class="iars-gantt-chip in-progress">In Progress</span>'
        '<span class="iars-gantt-chip done">Done</span>'
                '<span class="iars-gantt-chip for-frs">For FRS</span>'
        '<span class="iars-gantt-chip frs">FRS</span>'
        '<span class="iars-gantt-chip overdue">Overdue / Overdue: IRS / Overdue: FRS</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    _render_matrix(
        client,
        masters,
        entries,
        holidays,
        year=year,
        admin=admin,
        current_user_name=current_name,
        auditor_options=auditor_options,
        custodian_filter=custodian_filter,
        auditor_filter=auditor_filter,
        status_filter=status_filter,
        month_filter=month_filter,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    st.divider()
    st.markdown("### Holiday Exclusions Used for the Five-Working-Day Count")
    st.caption("Only active Regular, Special Non-Working, and Local Special Non-Working entries are excluded. Special Working days remain working days.")
    if holidays:
        holiday_table = pd.DataFrame([
            {
                "Date": _date_text(row.get("holiday_date")),
                "Holiday": _clean_text(row.get("holiday_name")),
                "Coverage": _clean_text(row.get("coverage")),
                "Type": _clean_text(row.get("holiday_type")),
            }
            for row in holidays
        ])
        st.dataframe(holiday_table, use_container_width=True, hide_index=True, height=min(360, 80 + len(holiday_table) * 34))
    else:
        st.warning("No active holiday records are loaded for this year. Upload them in Gantt Master Data.")


def _render_holiday_admin(
    client: Any,
    current_user: dict[str, Any],
    *,
    holiday_template_path: Path,
) -> None:
    actor = _user_name(current_user)
    st.markdown("### Holiday Calendar for Initial Report / FRS Deadlines")
    st.caption(
        "Upload official national, Province of Rizal, and San Mateo, Rizal holidays. "
        "Special Working holidays are stored for reference but are not excluded from the count."
    )
    if holiday_template_path.exists():
        st.download_button(
            "Download Holiday Calendar Excel Template",
            data=holiday_template_path.read_bytes(),
            file_name="Gantt_Holiday_Calendar_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    uploaded = st.file_uploader(
        "Upload Holiday Calendar Excel",
        type=["xlsx", "xls"],
        key="iars_gantt_holiday_upload_v4520",
    )
    if uploaded is not None:
        try:
            parsed = parse_holiday_upload(uploaded.getvalue())
            st.success(f"Validation passed: {len(parsed):,} holiday row(s) detected.")
            preview = parsed.rename(columns={
                "holiday_date": "Holiday Date",
                "holiday_name": "Holiday Name",
                "coverage": "Coverage",
                "holiday_type": "Holiday Type",
                "source_reference": "Source Reference",
                "active": "Active",
            })
            st.dataframe(preview, use_container_width=True, hide_index=True)
            if st.button("Import / Update Holiday Calendar", type="primary", use_container_width=True):
                count = upsert_holiday_records(client, parsed.to_dict("records"), actor)
                st.success(f"{count:,} holiday row(s) imported or updated successfully.")
                st.rerun()
        except Exception as exc:
            st.error(str(exc))

    try:
        holidays = list_holidays(client, None, active_only=False)
    except Exception as exc:
        st.error(f"Unable to load Holiday Calendar: {exc}")
        return

    holiday_map = {str(row.get("id")): row for row in holidays}
    choices = [""] + list(holiday_map)
    selected_id = st.selectbox(
        "Holiday record to edit",
        choices,
        format_func=lambda item: "Add a new holiday" if not item else (
            f"{_date_text(holiday_map[item].get('holiday_date'))} — "
            f"{_clean_text(holiday_map[item].get('holiday_name'))} — "
            f"{_clean_text(holiday_map[item].get('coverage'))}"
        ),
        key="iars_gantt_holiday_record_select_v4520",
    )
    selected = holiday_map.get(selected_id, {})
    with st.form("iars_gantt_holiday_record_form_v4520"):
        col1, col2 = st.columns([1, 2])
        holiday_date = col1.date_input(
            "Holiday Date",
            value=_parse_date(selected.get("holiday_date")) or _today_pht(),
        )
        holiday_name = col2.text_input("Holiday Name", value=_clean_text(selected.get("holiday_name")))
        col3, col4 = st.columns(2)
        coverage_value = _clean_text(selected.get("coverage")) or HOLIDAY_COVERAGES[0]
        coverage = col3.selectbox(
            "Coverage",
            HOLIDAY_COVERAGES,
            index=HOLIDAY_COVERAGES.index(coverage_value) if coverage_value in HOLIDAY_COVERAGES else 0,
        )
        type_value = _clean_text(selected.get("holiday_type")) or HOLIDAY_TYPES[0]
        holiday_type = col4.selectbox(
            "Holiday Type",
            HOLIDAY_TYPES,
            index=HOLIDAY_TYPES.index(type_value) if type_value in HOLIDAY_TYPES else 0,
        )
        source = st.text_input("Source Reference", value=_clean_text(selected.get("source_reference")))
        active = st.checkbox("Active holiday", value=bool(selected.get("active", True)))
        save = st.form_submit_button("Save Holiday", type="primary", use_container_width=True)
    if save:
        row = {
            "holiday_date": holiday_date,
            "holiday_name": holiday_name,
            "coverage": coverage,
            "holiday_type": holiday_type,
            "source_reference": source,
            "active": active,
        }
        try:
            if selected_id:
                update_holiday_record(client, selected_id, row, actor)
            else:
                upsert_holiday_records(client, [row], actor)
            st.success("Holiday record saved.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    if selected_id:
        action_label = "Deactivate Holiday" if bool(selected.get("active", True)) else "Reactivate Holiday"
        if st.button(action_label, key="iars_gantt_toggle_holiday_v4520"):
            try:
                set_holiday_active(client, selected_id, not bool(selected.get("active", True)), actor)
                st.success("Holiday status updated.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    if holidays:
        table = pd.DataFrame([
            {
                "Holiday Date": _date_text(row.get("holiday_date")),
                "Holiday Name": _clean_text(row.get("holiday_name")),
                "Coverage": _clean_text(row.get("coverage")),
                "Holiday Type": _clean_text(row.get("holiday_type")),
                "Excluded from Count": "Yes" if _holiday_type_key(row.get("holiday_type")) in NON_WORKING_HOLIDAY_TYPES and bool(row.get("active", True)) else "No",
                "Active": "Yes" if bool(row.get("active", True)) else "No",
            }
            for row in holidays
        ])
        st.dataframe(table, use_container_width=True, hide_index=True, height=min(620, 90 + len(table) * 34))


def render_gantt_master_data_page(
    client: Any,
    current_user: dict[str, Any],
    *,
    template_path: str | Path,
) -> None:
    _render_gantt_css()
    actor = _user_name(current_user)
    st.markdown(
        '<div class="iars-gantt-title"><h2>Gantt Master Data</h2>'
        '<p>Admin-only maintenance for the custodian audit universe and the holiday calendar used by automatic initial-report/FRS working-day deadlines.</p></div>',
        unsafe_allow_html=True,
    )
    setup = gantt_setup_status(client)
    if not setup.ready:
        st.warning(setup.message)
        st.code("SUPABASE_GANTT_V4_5_20_WORKFLOW_MIGRATION.sql", language=None)
        return

    template = Path(template_path)
    tabs = st.tabs(["Custodian Master Data", "Holiday Calendar"])
    with tabs[0]:
        if template.exists():
            st.download_button(
                "Download Gantt Master Data Excel Template",
                data=template.read_bytes(),
                file_name="Gantt_Master_Data_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        uploaded = st.file_uploader(
            "Upload Gantt Master Data Excel",
            type=["xlsx", "xls"],
            key="iars_gantt_master_upload_v4520",
        )
        if uploaded is not None:
            try:
                parsed = parse_master_upload(uploaded.getvalue())
                st.success(f"Validation passed: {len(parsed):,} master-data row(s) detected.")
                preview = parsed[["company_department", "custodian", "audit_task", "accountability"]].rename(columns={
                    "company_department": "Company",
                    "custodian": "Custodian",
                    "audit_task": "Audit Task",
                    "accountability": "Accountability",
                })
                st.dataframe(preview, use_container_width=True, hide_index=True)
                if st.button("Import / Update Master Data", type="primary", use_container_width=True):
                    count = upsert_master_records(client, parsed.to_dict("records"), actor)
                    st.success(f"{count:,} master-data row(s) imported or updated successfully.")
                    st.rerun()
            except Exception as exc:
                st.error(str(exc))

        st.divider()
        try:
            masters = list_master_records(client, active_only=False)
        except Exception as exc:
            st.error(f"Unable to load Gantt Master Data: {exc}")
            return

        active_count = sum(bool(row.get("active", True)) for row in masters)
        metric_cols = st.columns(4)
        metric_cols[0].metric("Records", len(masters))
        metric_cols[1].metric("Active", active_count)
        metric_cols[2].metric("Custodians", len({_clean_text(row.get('custodian')) for row in masters}))
        metric_cols[3].metric("Audit Tasks", len({_clean_text(row.get('audit_task')) for row in masters}))

        record_map = {str(row.get("id")): row for row in masters}

        with st.expander("Delete Gantt Master Data Records", expanded=False):
            st.warning(
                "Deletion is permanent. Any monthly Gantt schedules linked to the deleted "
                "master record(s) will also be deleted. The Holiday Calendar will remain unchanged."
            )
            delete_mode = st.radio(
                "Deletion mode",
                ["Single record", "Multiple records", "Delete all records"],
                horizontal=True,
                key="iars_gantt_master_delete_mode_v4532",
            )

            def _record_label(item: str) -> str:
                row = record_map.get(item, {})
                return (
                    f"{_clean_text(row.get('company_department'))} — "
                    f"{_clean_text(row.get('custodian'))} — "
                    f"{_clean_text(row.get('audit_task'))} — "
                    f"{_format_accountability(row.get('accountability'))}"
                )

            delete_ids: list[str] = []
            required_phrase = "DELETE"
            if delete_mode == "Single record":
                selected_delete_id = st.selectbox(
                    "Record to delete",
                    [""] + list(record_map),
                    format_func=lambda item: "Select one record" if not item else _record_label(item),
                    key="iars_gantt_master_delete_single_v4532",
                )
                delete_ids = [selected_delete_id] if selected_delete_id else []
            elif delete_mode == "Multiple records":
                delete_ids = st.multiselect(
                    "Records to delete",
                    list(record_map),
                    format_func=_record_label,
                    key="iars_gantt_master_delete_multiple_v4532",
                )
                if delete_ids:
                    st.caption(f"{len(delete_ids):,} record(s) selected for permanent deletion.")
            else:
                delete_ids = list(record_map)
                required_phrase = "DELETE ALL"
                st.error(
                    f"This will permanently delete all {len(delete_ids):,} Gantt Master Data "
                    "record(s) and every linked monthly schedule."
                )

            acknowledged = st.checkbox(
                "I understand that this action cannot be undone.",
                key="iars_gantt_master_delete_ack_v4532",
            )
            confirmation = st.text_input(
                f'Type {required_phrase} to confirm',
                key="iars_gantt_master_delete_confirm_v4532",
            )
            delete_ready = bool(
                delete_ids
                and acknowledged
                and _clean_text(confirmation).upper() == required_phrase
            )
            delete_label = {
                "Single record": "Delete Selected Record",
                "Multiple records": "Delete Selected Records",
                "Delete all records": "Delete All Master Data",
            }[delete_mode]
            if st.button(
                delete_label,
                type="primary",
                use_container_width=True,
                disabled=not delete_ready,
                key="iars_gantt_master_delete_execute_v4532",
            ):
                try:
                    deleted = (
                        delete_all_master_records(client)
                        if delete_mode == "Delete all records"
                        else delete_master_records(client, delete_ids)
                    )
                    st.success(
                        f"{deleted:,} Gantt Master Data record(s) and their linked schedules "
                        "were permanently deleted."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Unable to delete Gantt Master Data: {exc}")

        st.markdown("### Add or Edit a Master Record")
        choices = [""] + list(record_map)
        selected_id = st.selectbox(
            "Record to edit",
            choices,
            format_func=lambda item: "Add a new record" if not item else (
                f"{_clean_text(record_map[item].get('company_department'))} — "
                f"{_clean_text(record_map[item].get('custodian'))} — "
                f"{_clean_text(record_map[item].get('audit_task'))} — "
                f"{_format_accountability(record_map[item].get('accountability'))}"
            ),
            key="iars_gantt_master_record_select_v4520",
        )
        selected = record_map.get(selected_id, {})
        with st.form("iars_gantt_master_record_form_v4520"):
            col1, col2 = st.columns(2)
            company = col1.text_input("Company", value=_clean_text(selected.get("company_department")))
            custodian = col2.text_input("Custodian", value=_clean_text(selected.get("custodian")))
            col3, col4 = st.columns([2, 1])
            task = col3.text_input("Audit Task", value=_clean_text(selected.get("audit_task")))
            accountability = col4.text_input("Accountability", value=_clean_text(selected.get("accountability")))
            active = st.checkbox("Active record", value=bool(selected.get("active", True)))
            st.caption("Frequency is automatic and counts Done audits separately for this exact four-field record.")
            save_record = st.form_submit_button("Save Master Record", type="primary", use_container_width=True)
        if save_record:
            data = {
                "company_department": company,
                "custodian": custodian,
                "audit_task": task,
                "accountability": accountability,
                "active": active,
            }
            try:
                if selected_id:
                    update_master_record(client, selected_id, data, actor)
                else:
                    upsert_master_records(client, [data], actor)
                st.success("Gantt Master Data saved successfully.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        if selected_id:
            action_label = "Deactivate Record" if bool(selected.get("active", True)) else "Reactivate Record"
            if st.button(action_label, key="iars_gantt_toggle_master_v4520"):
                try:
                    set_master_active(client, selected_id, not bool(selected.get("active", True)), actor)
                    st.success("Master-record status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        st.markdown("### Current Master Data")
        if masters:
            table = pd.DataFrame([
                {
                    "Company": _clean_text(row.get("company_department")),
                    "Custodian": _clean_text(row.get("custodian")),
                    "Audit Task": _clean_text(row.get("audit_task")),
                    "Accountability": _format_accountability(row.get("accountability")),
                    "Status": "Active" if bool(row.get("active", True)) else "Inactive",
                }
                for row in masters
            ])
            st.dataframe(table, use_container_width=True, hide_index=True, height=min(620, 90 + len(table) * 35))
        else:
            st.info("No Gantt Master Data records yet.")

    with tabs[1]:
        _render_holiday_admin(
            client,
            current_user,
            holiday_template_path=template.parent / "gantt_holiday_calendar_template.xlsx",
        )
