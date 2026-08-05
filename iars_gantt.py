from __future__ import annotations

from calendar import month_name, monthrange
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Iterator
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
    company = _clean_text(row.get("company_department") or row.get("Company / Department"))
    custodian = _clean_text(row.get("custodian") or row.get("Custodian"))
    task = _clean_text(row.get("audit_task") or row.get("Audit Task"))
    accountability = _clean_text(row.get("accountability") or row.get("Accountability"))
    active_raw = row.get("active", row.get("Active", True))
    if isinstance(active_raw, str):
        active = active_raw.strip().casefold() not in {"no", "n", "false", "0", "inactive"}
    else:
        active = bool(active_raw)
    if not company or not custodian or not task:
        raise GanttError("Company / Department, Custodian, and Audit Task are required.")
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
            "company_department": "Company / Department",
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
        raise GanttError("Every row must contain Company / Department, Custodian, and Audit Task.")
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
            "Exact duplicate master-data rows were found. Company / Department, Custodian, "
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
    if not entry:
        return "＋ Schedule", "empty"
    info = report_stage_info(entry, holiday_rows)
    display_stage = _display_stage(info.stage)
    nickname = _clean_text(entry.get("auditor_nickname")) or nickname_for(entry.get("auditor_full_name"))
    if info.stage in {"Planned", "In Progress", "Overdue"}:
        date_label = f"Due: {_box_date(entry.get('planned_date'))}"
    elif info.stage in {"Done", "Overdue: IRS", "For FRS", "Overdue: FRS"}:
        date_label = f"Due: {_box_date(info.deadline)}"
    else:
        date_label = f"Submitted: {_box_date(entry.get('final_report_submitted_at'))}"
    return f"{display_stage}\n{nickname}\n{date_label}", _stage_slug(display_stage)


def _render_gantt_css() -> None:
    st.markdown(
        """
        <style>
        .iars-gantt-title h2 {font-size:1.72rem!important;font-weight:800!important;margin-bottom:.2rem!important;color:#0B2B55!important;}
        .iars-gantt-title p {color:#667085!important;margin-top:0!important;}
        .iars-gantt-alert {border:1px solid #991B1B;background:#B91C1C;color:#fff;border-radius:14px;padding:1rem 1.1rem;margin:.5rem 0 1rem;}
        .iars-gantt-alert strong {font-size:1.02rem;display:block;margin-bottom:.18rem;}
        .iars-gantt-alert ul {margin:.45rem 0 0 1.1rem;padding:0;}
        .iars-gantt-notice {border:1px solid #D6A129;background:#FFF8E6;color:#594200;border-radius:14px;padding:1rem 1.1rem;margin:.5rem 0 1rem;}
        .iars-gantt-notice strong {display:block;margin-bottom:.18rem;}
        .iars-gantt-access-note {border-left:4px solid #C78B12;background:#FFF9E8;border-radius:8px;padding:.75rem .9rem;color:#344054;margin:.4rem 0 1rem;}
        /* V4.5.26 uses Streamlit's native dataframe grid. Its header is frozen by
           the grid itself, so it no longer depends on fragile CSS selectors for
           nested st.columns wrappers. */
        [class*="st-key-iars-gantt-grid-v4526"] [data-testid="stDataFrame"] {border:1px solid #D9E2EE!important;border-radius:14px!important;overflow:hidden!important;}
        [class*="st-key-iars-gantt-grid-v4526"] canvas {cursor:pointer!important;}
        .iars-gantt-legend {display:flex;flex-wrap:wrap;gap:.42rem;margin:.35rem 0 .7rem;}
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


def _reset_gantt_grid_selection() -> None:
    try:
        st.session_state["iars_gantt_grid_generation_v4526"] = int(
            st.session_state.get("iars_gantt_grid_generation_v4526", 0)
        ) + 1
    except Exception:
        pass


def _finish_month_editor() -> None:
    _reset_gantt_grid_selection()
    st.rerun()


def _event_cells(event: Any) -> list[tuple[int, str]]:
    if event is None:
        return []
    selection = getattr(event, "selection", None)
    if selection is None and isinstance(event, dict):
        selection = event.get("selection")
    cells = getattr(selection, "cells", None)
    if cells is None and isinstance(selection, dict):
        cells = selection.get("cells")
    output: list[tuple[int, str]] = []
    for cell in cells or []:
        if isinstance(cell, (list, tuple)) and len(cell) == 2:
            try:
                output.append((int(cell[0]), str(cell[1])))
            except (TypeError, ValueError):
                continue
    return output


def _text_column(label: str, *, pinned: bool = False, width: int = 104) -> Any:
    namespace = getattr(st, "column_config", None)
    factory = getattr(namespace, "TextColumn", None) if namespace is not None else None
    if callable(factory):
        return factory(label, width=width, pinned=pinned, alignment="center")
    return label


def _gantt_cell_style(value: Any) -> str:
    first_line = str(value or "").splitlines()[0].strip()
    base = "text-align:center;font-weight:700;white-space:pre-line;border:1px solid #D9E2EE;"
    if first_line in {"Overdue", "Overdue: IRS", "Overdue: FRS"}:
        return base + "background-color:#B91C1C;color:#FFFFFF;"
    palette = {
        "Scheduled": ("#EAF2FF", "#1E3A8A", "#3B82F6"),
        "In Progress": ("#FFF4E5", "#7C2D12", "#F59E0B"),
        "Done": ("#DCFCE7", "#14532D", "#22C55E"),
        "For FRS": ("#ECFEFF", "#164E63", "#0891B2"),
        "FRS": ("#D1FAE5", "#064E3B", "#047857"),
        "＋ Schedule": ("#FAFBFC", "#667085", "#CBD5E1"),
    }
    background, foreground, border = palette.get(first_line, ("#FFFFFF", "#344054", "#D9E2EE"))
    return base + f"background-color:{background};color:{foreground};border-color:{border};"


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
                on_dismiss=_reset_gantt_grid_selection,
            )
        except TypeError:
            decorator = dialog_factory(title)

        @decorator
        def _dialog() -> None:
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

    if entry is None:
        if not admin:
            st.caption("No audit assignment for your account.")
            return
        options = list(dict.fromkeys([name for name in auditor_options if _clean_text(name)]))
        if not options:
            st.error("No auditor account is available for assignment.")
            return
        with st.form(f"gantt_plan_new_{unique}"):
            auditor = st.selectbox(
                "Auditor",
                options,
                format_func=lambda name: f"{name} — {nickname_for(name)}",
                key=f"gantt_new_auditor_{unique}",
            )
            st.text_input("Status", value="Scheduled", disabled=True, key=f"gantt_new_status_{unique}")
            st.text_input("Due Date", value=_box_date(due_date), disabled=True, key=f"gantt_new_due_{unique}")
            save = st.form_submit_button("Save Scheduled Audit", type="primary", use_container_width=True)
        if save:
            try:
                upsert_schedule_entry(
                    client,
                    master_id=master_id,
                    schedule_year=year,
                    schedule_month=month,
                    auditor_full_name=auditor,
                    status="Planned",
                    planned_date=due_date,
                    actor=current_user_name,
                )
                st.success("Scheduled audit saved.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))
        return

    stage = report_stage_info(entry, holiday_rows)
    assigned = _clean_text(entry.get("auditor_full_name"))
    st.caption(f"Assigned auditor: {assigned} — {nickname_for(assigned)}")

    if admin and effective_status(entry) != "Done":
        options = list(dict.fromkeys([name for name in auditor_options if _clean_text(name)] + [assigned]))
        selected_index = options.index(assigned) if assigned in options else 0
        stored_status = _clean_text(entry.get("status"))
        if stored_status not in {"Planned", "In Progress"}:
            stored_status = "Planned"
        with st.form(f"gantt_plan_edit_{unique}"):
            auditor = st.selectbox(
                "Auditor",
                options,
                index=selected_index,
                format_func=lambda name: f"{name} — {nickname_for(name)}",
                key=f"gantt_edit_auditor_{unique}",
            )
            st.text_input("Status", value=_display_stage(stored_status), disabled=True, key=f"gantt_edit_status_{unique}")
            st.text_input("Due Date", value=_box_date(due_date), disabled=True, key=f"gantt_edit_due_{unique}")
            save = st.form_submit_button("Update Assignment", type="primary", use_container_width=True)
        if save:
            try:
                upsert_schedule_entry(
                    client,
                    master_id=master_id,
                    schedule_year=year,
                    schedule_month=month,
                    auditor_full_name=auditor,
                    status=stored_status,
                    planned_date=due_date,
                    actor=current_user_name,
                )
                st.success("Audit assignment updated.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))
        if st.button("Delete Monthly Assignment", key=f"gantt_delete_{unique}", use_container_width=True):
            try:
                delete_schedule_entry(client, str(entry.get("id") or ""))
                st.success("Monthly assignment deleted.")
                _finish_month_editor()
            except Exception as exc:
                st.error(str(exc))
        return

    if not admin and _name_key(assigned) != _name_key(current_user_name):
        st.info("This audit is assigned to another auditor.")
        return

    if effective_status(entry) != "Done":
        if admin:
            st.info("The assigned auditor controls In Progress and Done updates.")
            return
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
    if not admin:
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
    else:
        st.write(f"**Date of Audit:** {_display_date(entry.get('accomplished_date'))}")

    if stage.stage in {"Done", "Overdue: IRS"}:
        st.write(f"**Initial report deadline:** {_display_date(stage.deadline)}")
        if stage.overdue:
            st.error("Overdue: IRS — submit the initial report now.")
        elif admin:
            st.info("The initial-report five-working-day period is running.")
        if not admin:
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
            st.error("Overdue: FRS — finalize and submit the report now.")
        if admin:
            with st.form(f"gantt_frs_{unique}"):
                reference = st.text_input(
                    "FRS Reference / Remarks",
                    value=_clean_text(entry.get("final_report_reference")),
                    key=f"gantt_frs_ref_{unique}",
                )
                submit_frs = st.form_submit_button(
                    "FRS — Final Report Submitted",
                    type="primary",
                    use_container_width=True,
                )
            if submit_frs:
                try:
                    submit_final_report(
                        client,
                        entry_id=str(entry.get("id") or ""),
                        actor=current_user_name,
                        reference=reference,
                    )
                    st.success("FRS recorded using today's Philippine date.")
                    _finish_month_editor()
                except Exception as exc:
                    st.error(str(exc))
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
    month_headers = [month_name[month] for month in MONTHS]
    rows: list[dict[str, Any]] = []
    for master in filtered:
        master_id = str(master.get("id") or "")
        row: dict[str, Any] = {
            "Company / Department": _clean_text(master.get("company_department")),
            "Custodian": _clean_text(master.get("custodian")),
            "Audit Task": _clean_text(master.get("audit_task")),
            "Accountability": _format_accountability(master.get("accountability")),
            "Frequency": f"{done_counts.get(master_id, 0)}×",
        }
        for month in MONTHS:
            entry = lookup.get((master_id, month))
            if entry and not admin and _name_key(entry.get("auditor_full_name")) != _name_key(current_user_name):
                entry = None
            if entry is None and not admin:
                row[month_name[month]] = "—"
            else:
                row[month_name[month]] = _month_box_label(entry, holiday_rows)[0]
        rows.append(row)

    frame = pd.DataFrame(rows)
    try:
        styled = frame.style.map(_gantt_cell_style, subset=month_headers)
        styled = styled.set_properties(
            subset=month_headers,
            **{"white-space": "pre-line", "text-align": "center", "vertical-align": "middle"},
        )
    except AttributeError:
        styled = frame.style.applymap(_gantt_cell_style, subset=month_headers)

    column_config: dict[str, Any] = {
        "Company / Department": _text_column("Company / Department", pinned=True),
        "Custodian": _text_column("Custodian", pinned=True),
        "Audit Task": _text_column("Audit Task", pinned=True),
        "Accountability": _text_column("Accountability", pinned=True),
        "Frequency": _text_column("Frequency", pinned=True),
    }
    for header in month_headers:
        column_config[header] = _text_column(header, pinned=False)

    generation = 0
    try:
        generation = int(st.session_state.get("iars_gantt_grid_generation_v4526", 0))
    except Exception:
        pass
    grid_key = f"iars-gantt-grid-v4526-{year}-{generation}"
    try:
        event = st.dataframe(
            styled,
            width="stretch",
            height=560,
            hide_index=True,
            column_config=column_config,
            row_height=78,
            key=grid_key,
            on_select="rerun",
            selection_mode="single-cell",
        )
    except TypeError:
        event = st.dataframe(
            styled,
            use_container_width=True,
            height=560,
            hide_index=True,
            column_config=column_config,
            row_height=78,
            key=grid_key,
        )

    cells = _event_cells(event)
    if cells:
        row_index, column_name = cells[-1]
        month_by_header = {month_name[month]: month for month in MONTHS}
        month = month_by_header.get(column_name)
        if month is not None and 0 <= row_index < len(filtered):
            master = filtered[row_index]
            master_id = str(master.get("id") or "")
            entry = lookup.get((master_id, month))
            if entry and not admin and _name_key(entry.get("auditor_full_name")) != _name_key(current_user_name):
                entry = None
            if admin or entry is not None:
                _open_month_editor_dialog(
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

    st.caption(
        f"Showing all {len(filtered)} matching custodian record(s) in one Gantt grid. "
        "The native grid freezes the full Company-to-December header during vertical scrolling and pins Company through Frequency during horizontal scrolling. Click a month cell to update it."
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
        '<p>Click a month cell to assign the auditor, update In Progress or Done, submit the initial report, or submit FRS. Scheduled due dates are automatically set to the last day of the month. Initial-report and FRS deadlines each use five working days, excluding weekends and active non-working holidays.</p></div>',
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

    if admin:
        st.markdown(
            '<div class="iars-gantt-access-note"><strong>Administrator/Supervisor:</strong> Click any month box to assign an auditor. After the initial report is submitted, click the month cell to mark FRS. FRS becomes overdue after five working days from the initial-report submission date.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="iars-gantt-access-note"><strong>Auditor — {html.escape(nickname_for(current_name))}:</strong> Click your assigned month cell to update In Progress or Done and submit the initial report. It becomes Overdue: IRS after five working days from the Date of Audit.</div>',
            unsafe_allow_html=True,
        )

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
                    "company_department": "Company / Department",
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

        st.markdown("### Add or Edit a Master Record")
        record_map = {str(row.get("id")): row for row in masters}
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
            company = col1.text_input("Company / Department", value=_clean_text(selected.get("company_department")))
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
                    "Company / Department": _clean_text(row.get("company_department")),
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
