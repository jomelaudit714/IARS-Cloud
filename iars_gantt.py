from __future__ import annotations

from calendar import month_name
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable
import html
import re

import pandas as pd
import streamlit as st


GANTT_MASTER_TABLE = "iars_gantt_master"
GANTT_SCHEDULE_TABLE = "iars_gantt_schedule"
GANTT_STATUSES = ["Planned", "In Progress", "Done", "Overdue"]
MONTHS = list(range(1, 13))
PHILIPPINE_TIMEZONE = timezone(timedelta(hours=8))

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
    first = name.split()[0]
    return first[:14]


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


def _today_pht() -> date:
    return datetime.now(PHILIPPINE_TIMEZONE).date()


def effective_status(entry: dict[str, Any], *, today: date | None = None) -> str:
    status = _clean_text(entry.get("status")) or "Planned"
    if status == "Done":
        return "Done"
    planned = _parse_date(entry.get("planned_date"))
    check_date = today or _today_pht()
    if planned and planned < check_date:
        return "Overdue"
    return status if status in GANTT_STATUSES else "Planned"


def gantt_setup_status(client: Any) -> GanttSetupStatus:
    if client is None:
        return GanttSetupStatus(False, "Supabase is not connected.")
    try:
        client.table(GANTT_MASTER_TABLE).select("id").limit(1).execute()
        client.table(GANTT_SCHEDULE_TABLE).select("id").limit(1).execute()
        return GanttSetupStatus(True, "")
    except Exception as exc:
        return GanttSetupStatus(
            False,
            "Yearly Audit Gantt tables are not ready. Run SUPABASE_GANTT_SETUP.sql in Supabase, then refresh IARS. "
            f"Details: {exc}",
        )


def list_master_records(client: Any, *, active_only: bool = False) -> list[dict[str, Any]]:
    query = client.table(GANTT_MASTER_TABLE).select("*")
    if active_only:
        query = query.eq("active", True)
    rows = _response_rows(query.order("company_department").order("custodian").execute())
    return rows


def list_schedule_entries(
    client: Any,
    schedule_year: int,
    *,
    auditor_full_name: str | None = None,
) -> list[dict[str, Any]]:
    query = (
        client.table(GANTT_SCHEDULE_TABLE)
        .select("*")
        .eq("schedule_year", int(schedule_year))
    )
    if auditor_full_name:
        query = query.ilike("auditor_full_name", _clean_text(auditor_full_name))
    return _response_rows(query.order("schedule_month").execute())


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
    response = (
        client.table(GANTT_MASTER_TABLE)
        .upsert(
            payloads,
            on_conflict="company_department,custodian,audit_task",
        )
        .execute()
    )
    returned = _response_rows(response)
    return len(returned) if returned else len(payloads)


def update_master_record(client: Any, record_id: str, row: dict[str, Any], actor: str) -> None:
    payload = _master_payload(row, actor)
    client.table(GANTT_MASTER_TABLE).update(payload).eq("id", record_id).execute()


def set_master_active(client: Any, record_id: str, active: bool, actor: str) -> None:
    client.table(GANTT_MASTER_TABLE).update(
        {
            "active": bool(active),
            "updated_by": actor,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", record_id).execute()


def upsert_schedule_entry(
    client: Any,
    *,
    master_id: str,
    schedule_year: int,
    schedule_month: int,
    auditor_full_name: str,
    status: str,
    planned_date: date | None,
    accomplished_date: date | None,
    remarks: str,
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
    if clean_status == "Done" and not accomplished_date:
        raise GanttError("Date accomplished is required when status is Done.")
    payload = {
        "master_id": master_id,
        "schedule_year": int(schedule_year),
        "schedule_month": int(schedule_month),
        "auditor_full_name": auditor,
        "auditor_nickname": nickname_for(auditor),
        "status": clean_status,
        "planned_date": planned_date.isoformat() if planned_date else None,
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
    if clean_status not in GANTT_STATUSES:
        raise GanttError("Select a valid status.")
    if clean_status == "Done" and not accomplished_date:
        raise GanttError("Date accomplished is required when status is Done.")
    client.table(GANTT_SCHEDULE_TABLE).update(
        {
            "status": clean_status,
            "accomplished_date": accomplished_date.isoformat() if accomplished_date else None,
            "remarks": _clean_text(remarks),
            "updated_by": current_user_name,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", entry_id).execute()


def delete_schedule_entry(client: Any, entry_id: str) -> None:
    client.table(GANTT_SCHEDULE_TABLE).delete().eq("id", entry_id).execute()


def parse_master_upload(file_bytes: bytes) -> pd.DataFrame:
    try:
        xls = pd.ExcelFile(BytesIO(file_bytes))
    except Exception as exc:
        raise GanttError(f"Unable to read the Excel file: {exc}") from exc
    sheet_name = "Gantt Master Data" if "Gantt Master Data" in xls.sheet_names else xls.sheet_names[0]
    raw = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name)
    raw = raw.dropna(how="all").copy()
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

    output = pd.DataFrame()
    for target in required:
        output[target] = raw[selected[target]]
    output["active"] = raw[selected["active"]] if "active" in selected else True
    output = output.dropna(how="all", subset=["company_department", "custodian", "audit_task"])
    output["company_department"] = output["company_department"].map(_clean_text)
    output["custodian"] = output["custodian"].map(_clean_text)
    output["audit_task"] = output["audit_task"].map(_clean_text)
    output["accountability"] = output["accountability"].map(_clean_text)
    if output[["company_department", "custodian", "audit_task"]].eq("").any(axis=None):
        raise GanttError("Every row must contain Company / Department, Custodian, and Audit Task.")
    output["active"] = output["active"].map(
        lambda value: _clean_text(value).casefold() not in {"no", "n", "false", "0", "inactive"}
        if isinstance(value, str)
        else bool(value)
    )
    duplicates = output.duplicated(
        subset=["company_department", "custodian", "audit_task"], keep=False
    )
    if duplicates.any():
        raise GanttError("Duplicate Company / Department + Custodian + Audit Task rows were found in the upload.")
    return output.reset_index(drop=True)


def _format_accountability(value: Any) -> str:
    text = _clean_text(value)
    if not text:
        return "—"
    try:
        number = float(text.replace(",", "").replace("₱", ""))
        if number.is_integer():
            return f"₱{number:,.0f}"
        return f"₱{number:,.2f}"
    except ValueError:
        return text


def done_frequency_by_custodian(
    masters: list[dict[str, Any]],
    entries: list[dict[str, Any]],
) -> dict[str, int]:
    """Count Done audit schedules per custodian for the loaded schedule year."""
    master_custodians = {
        str(master.get("id") or ""): _name_key(master.get("custodian"))
        for master in masters
        if master.get("id") and _name_key(master.get("custodian"))
    }
    counts: dict[str, int] = {}
    for entry in entries:
        if effective_status(entry) != "Done":
            continue
        custodian_key = master_custodians.get(str(entry.get("master_id") or ""))
        if custodian_key:
            counts[custodian_key] = counts.get(custodian_key, 0) + 1
    return counts


def _entry_lookup(entries: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    return {
        (str(entry.get("master_id") or ""), int(entry.get("schedule_month") or 0)): entry
        for entry in entries
        if entry.get("master_id") and int(entry.get("schedule_month") or 0) in MONTHS
    }


def _month_cell(entry: dict[str, Any] | None) -> str:
    if not entry:
        return '<div class="iars-gantt-empty">—</div>'
    status = effective_status(entry)
    nickname = _clean_text(entry.get("auditor_nickname")) or nickname_for(entry.get("auditor_full_name"))
    planned = _date_text(entry.get("planned_date"))
    accomplished = _date_text(entry.get("accomplished_date"))
    shown_date = accomplished if status == "Done" and accomplished else planned
    status_class = {
        "Done": "done",
        "In Progress": "progress",
        "Overdue": "overdue",
        "Planned": "planned",
    }.get(status, "planned")
    return (
        f'<div class="iars-gantt-month-box {status_class}">'
        f'<span class="iars-gantt-status">{html.escape(status)}</span>'
        f'<strong>{html.escape(nickname)}</strong>'
        f'<small>{html.escape(shown_date or "No date")}</small>'
        '</div>'
    )


def _render_gantt_css() -> None:
    st.markdown(
        """
        <style>
        .iars-gantt-title h2 {font-size:1.72rem!important;font-weight:800!important;margin-bottom:.2rem!important;color:#0B2B55!important;}
        .iars-gantt-title p {color:#667085!important;margin-top:0!important;}
        .iars-gantt-alert {border:1px solid #991B1B;background:#B91C1C;color:#fff;border-radius:14px;padding:1rem 1.1rem;margin:.5rem 0 1rem;}
        .iars-gantt-alert strong {font-size:1.02rem;display:block;margin-bottom:.18rem;}
        .iars-gantt-alert ul {margin:.45rem 0 0 1.1rem;padding:0;}
        .iars-gantt-table-wrap {width:100%;overflow-x:auto;border:1px solid #D9E2EE;border-radius:14px;background:#fff;margin:.65rem 0 1rem;}
        table.iars-gantt-table {border-collapse:separate;border-spacing:0;min-width:2240px;width:100%;font-size:.82rem;}
        .iars-gantt-table th {position:sticky;top:0;z-index:2;background:#EAF0F8;color:#0B2B55;font-size:1rem;font-weight:800;text-align:center;padding:.85rem .65rem;border-right:1px solid #CBD7E6;border-bottom:1px solid #B8C8DB;white-space:nowrap;}
        .iars-gantt-table th.left-head {text-align:left;}
        .iars-gantt-table td {padding:.55rem;border-right:1px solid #E1E8F0;border-bottom:1px solid #E1E8F0;vertical-align:middle;background:#fff;}
        .iars-gantt-table td.company {min-width:270px;font-weight:700;color:#0B2B55;}
        .iars-gantt-table td.custodian {min-width:220px;}
        .iars-gantt-table td.task {min-width:190px;}
        .iars-gantt-table td.accountability {min-width:135px;text-align:right;font-weight:700;}
        .iars-gantt-table td.frequency {min-width:90px;text-align:center;font-weight:700;}
        .iars-gantt-table td.month {min-width:112px;width:112px;padding:.38rem;}
        .iars-gantt-month-box {min-height:68px;border:1px solid #CCD6E3;border-radius:10px;padding:.42rem .48rem;display:flex;flex-direction:column;justify-content:center;gap:.12rem;background:#F8FAFC;}
        .iars-gantt-month-box strong {font-size:.98rem;color:#0B2B55;}
        .iars-gantt-month-box small {font-size:.69rem;color:#667085;}
        .iars-gantt-status {font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.03em;}
        .iars-gantt-month-box.planned {border-color:#D6A129;background:#FFF8E6;}
        .iars-gantt-month-box.progress {border-color:#2563EB;background:#EFF6FF;}
        .iars-gantt-month-box.done {border-color:#18864B;background:#ECFDF3;}
        .iars-gantt-month-box.overdue {border-color:#991B1B;background:#B91C1C;color:#fff;}
        .iars-gantt-month-box.overdue strong,.iars-gantt-month-box.overdue small,.iars-gantt-month-box.overdue .iars-gantt-status {color:#fff!important;}
        .iars-gantt-empty {min-height:68px;border:1px dashed #D4DCE7;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#98A2B3;background:#FAFBFC;}
        .iars-gantt-access-note {border-left:4px solid #C78B12;background:#FFF9E8;border-radius:8px;padding:.75rem .9rem;color:#344054;margin:.4rem 0 1rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_matrix(
    masters: list[dict[str, Any]],
    entries: list[dict[str, Any]],
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
    done_counts = done_frequency_by_custodian(masters, entries)
    current_key = _name_key(current_user_name)
    filtered: list[dict[str, Any]] = []
    for master in masters:
        master_id = str(master.get("id") or "")
        month_entries = [lookup.get((master_id, month)) for month in MONTHS]
        visible_month_entries = [entry for entry in month_entries if entry]
        if not admin:
            visible_month_entries = [
                entry for entry in visible_month_entries
                if _name_key(entry.get("auditor_full_name")) == current_key
            ]
            if not visible_month_entries:
                continue
        if custodian_filter != "All" and _clean_text(master.get("custodian")) != custodian_filter:
            continue
        if admin and auditor_filter != "All" and not any(
            _name_key(entry.get("auditor_full_name")) == _name_key(auditor_filter)
            for entry in visible_month_entries
        ):
            continue
        if status_filter != "All" and not any(
            effective_status(entry) == status_filter for entry in visible_month_entries
        ):
            continue
        if month_filter and not any(
            int(entry.get("schedule_month") or 0) == month_filter for entry in visible_month_entries
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
        if sort_by == "Auditor":
            return _clean_text((first_entry(master) or {}).get("auditor_full_name")).casefold()
        if sort_by == "Status":
            rank = {"Overdue": 0, "In Progress": 1, "Planned": 2, "Done": 3}
            return rank.get(effective_status(first_entry(master) or {}), 9)
        if sort_by == "Month":
            return int((first_entry(master) or {}).get("schedule_month") or 99)
        return _clean_text(master.get("custodian")).casefold()

    filtered.sort(key=sort_value, reverse=sort_desc)
    headers = [
        "Company / Department", "Custodian", "Audit Task", "Accountability", "Frequency"
    ] + [month_name[month] for month in MONTHS]
    header_html = "".join(
        f'<th class="{"left-head" if index < 3 else ""}">{html.escape(label)}</th>'
        for index, label in enumerate(headers)
    )
    rows_html = []
    for master in filtered:
        master_id = str(master.get("id") or "")
        cells = [
            f'<td class="company">{html.escape(_clean_text(master.get("company_department")))}</td>',
            f'<td class="custodian">{html.escape(_clean_text(master.get("custodian")))}</td>',
            f'<td class="task">{html.escape(_clean_text(master.get("audit_task")))}</td>',
            f'<td class="accountability">{html.escape(_format_accountability(master.get("accountability")))}</td>',
            f'<td class="frequency">{done_counts.get(_name_key(master.get("custodian")), 0)}×</td>',
        ]
        for month in MONTHS:
            entry = lookup.get((master_id, month))
            if entry and not admin and _name_key(entry.get("auditor_full_name")) != current_key:
                entry = None
            cells.append(f'<td class="month">{_month_cell(entry)}</td>')
        rows_html.append("<tr>" + "".join(cells) + "</tr>")
    if not rows_html:
        rows_html.append(
            '<tr><td colspan="17" style="padding:1.2rem;text-align:center;color:#667085;">No schedule matched the selected filters.</td></tr>'
        )
    st.markdown(
        '<div class="iars-gantt-table-wrap"><table class="iars-gantt-table"><thead><tr>'
        + header_html
        + '</tr></thead><tbody>'
        + "".join(rows_html)
        + '</tbody></table></div>',
        unsafe_allow_html=True,
    )
    return filtered


def _load_gantt_data(client: Any, year: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    masters = list_master_records(client, active_only=False)
    entries = list_schedule_entries(client, year)
    return masters, entries


def render_gantt_dashboard_alert(client: Any, current_user: dict[str, Any], *, admin: bool) -> None:
    _render_gantt_css()
    status = gantt_setup_status(client)
    if not status.ready:
        return
    current_name = _user_name(current_user)
    year = _today_pht().year
    try:
        entries = list_schedule_entries(client, year)
    except Exception:
        return
    if not admin:
        entries = [
            entry for entry in entries
            if _name_key(entry.get("auditor_full_name")) == _name_key(current_name)
        ]
    overdue = [entry for entry in entries if effective_status(entry) == "Overdue"]
    if not overdue:
        return
    try:
        masters = {str(row.get("id")): row for row in list_master_records(client, active_only=False)}
    except Exception:
        masters = {}
    lines = []
    for entry in overdue[:5]:
        master = masters.get(str(entry.get("master_id")), {})
        lines.append(
            f"<li><strong>{html.escape(_clean_text(master.get('custodian')) or 'Custodian')}</strong> — "
            f"{html.escape(_clean_text(master.get('audit_task')) or 'Audit task')} · "
            f"planned {html.escape(_date_text(entry.get('planned_date')) or 'without date')}</li>"
        )
    owner_text = "across all auditors" if admin else f"assigned to {html.escape(nickname_for(current_name))}"
    st.markdown(
        '<div class="iars-gantt-alert"><strong>⚠ Overdue audit schedule notification</strong>'
        f'<span>{len(overdue)} overdue audit schedule(s) {owner_text} require attention.</span>'
        f'<ul>{"".join(lines)}</ul>'
        '<div style="margin-top:.55rem;font-size:.78rem;opacity:.9;">Open Yearly Audit Gantt from the sidebar to update the accomplishment.</div></div>',
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
        '<p>One custodian per row with January through December displayed in separate monthly columns. Frequency is the automatic count of Done audits for the custodian in the selected year.</p></div>',
        unsafe_allow_html=True,
    )
    setup = gantt_setup_status(client)
    if not setup.ready:
        if admin:
            st.warning(setup.message)
            st.code("SUPABASE_GANTT_SETUP.sql", language=None)
        else:
            st.info("The Yearly Audit Gantt module is not yet available. Please contact the administrator.")
        return

    default_year = _today_pht().year
    year = int(st.selectbox("Schedule Year", list(range(default_year - 1, default_year + 4)), index=1, key="iars_gantt_year"))
    try:
        masters, entries = _load_gantt_data(client, year)
    except Exception as exc:
        st.error(f"Unable to load the Yearly Audit Gantt: {exc}")
        return

    visible_entries = entries if admin else [
        entry for entry in entries
        if _name_key(entry.get("auditor_full_name")) == _name_key(current_name)
    ]
    overdue_count = sum(effective_status(entry) == "Overdue" for entry in visible_entries)
    done_count = sum(effective_status(entry) == "Done" for entry in visible_entries)
    progress_count = sum(effective_status(entry) == "In Progress" for entry in visible_entries)
    metric_cols = st.columns(4)
    metric_cols[0].metric("Assigned Audits" if not admin else "Scheduled Audits", len(visible_entries))
    metric_cols[1].metric("Done", done_count)
    metric_cols[2].metric("In Progress", progress_count)
    metric_cols[3].metric("Overdue", overdue_count)

    if overdue_count:
        st.markdown(
            f'<div class="iars-gantt-alert"><strong>⚠ {overdue_count} overdue audit schedule(s)</strong>'
            '<span>Overdue boxes are displayed in solid red in the Gantt chart.</span></div>',
            unsafe_allow_html=True,
        )

    if admin:
        st.markdown(
            '<div class="iars-gantt-access-note"><strong>Administrator access:</strong> You can view all auditors, create or edit monthly assignments, and sort the full annual schedule.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="iars-gantt-access-note"><strong>Auditor access — {html.escape(nickname_for(current_name))}:</strong> Only schedules assigned to your account are displayed. You can update status, date accomplished, and accomplishment remarks.</div>',
            unsafe_allow_html=True,
        )

    custodian_options = ["All"] + sorted({_clean_text(row.get("custodian")) for row in masters if _clean_text(row.get("custodian"))}, key=str.casefold)
    filter_cols = st.columns(5 if admin else 4)
    custodian_filter = filter_cols[0].selectbox("Custodian", custodian_options, key="iars_gantt_filter_custodian")
    offset = 1
    auditor_filter = "All"
    if admin:
        auditor_filter = filter_cols[1].selectbox("Auditor", ["All"] + list(auditor_options), key="iars_gantt_filter_auditor")
        offset = 2
    status_filter = filter_cols[offset].selectbox("Status", ["All"] + GANTT_STATUSES, key="iars_gantt_filter_status")
    month_label = filter_cols[offset + 1].selectbox("Month", ["All"] + [month_name[m] for m in MONTHS], key="iars_gantt_filter_month")
    sort_by = filter_cols[offset + 2].selectbox("Sort by", ["Custodian", "Auditor", "Status", "Month"], key="iars_gantt_sort_by")
    sort_desc = st.toggle("Descending order", value=False, key="iars_gantt_sort_desc")
    month_filter = None if month_label == "All" else list(month_name).index(month_label)

    _render_matrix(
        masters,
        entries,
        admin=admin,
        current_user_name=current_name,
        custodian_filter=custodian_filter,
        auditor_filter=auditor_filter,
        status_filter=status_filter,
        month_filter=month_filter,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    st.divider()
    if admin:
        st.markdown("### Edit Monthly Audit Assignment")
        active_masters = [row for row in masters if bool(row.get("active", True))]
        if not active_masters:
            st.info("Upload or add active Gantt Master Data before creating a schedule.")
            return
        master_map = {str(row.get("id")): row for row in active_masters}
        master_ids = list(master_map)
        selected_master_id = st.selectbox(
            "Company / Custodian / Audit Task",
            master_ids,
            format_func=lambda item: f"{_clean_text(master_map[item].get('company_department'))} — {_clean_text(master_map[item].get('custodian'))} — {_clean_text(master_map[item].get('audit_task'))}",
            key="iars_gantt_edit_master",
        )
        selected_month = st.selectbox(
            "Month to schedule or edit",
            MONTHS,
            format_func=lambda value: month_name[value],
            key="iars_gantt_edit_month",
        )
        existing = _entry_lookup(entries).get((selected_master_id, selected_month), {})
        with st.form("iars_gantt_admin_assignment_form"):
            col1, col2, col3, col4 = st.columns(4)
            existing_auditor = _clean_text(existing.get("auditor_full_name"))
            options = list(auditor_options)
            if existing_auditor and existing_auditor not in options:
                options.append(existing_auditor)
            auditor_index = options.index(existing_auditor) if existing_auditor in options else 0
            assigned_auditor = col1.selectbox(
                "Assigned Auditor",
                options,
                index=auditor_index,
                format_func=lambda name: f"{name} — {nickname_for(name)}",
            )
            existing_status = effective_status(existing) if existing else "Planned"
            status_value = col2.selectbox("Status", GANTT_STATUSES, index=GANTT_STATUSES.index(existing_status))
            planned_value = col3.date_input(
                "Planned Audit Date",
                value=_parse_date(existing.get("planned_date")) or date(year, selected_month, 1),
            )
            accomplished_existing = _parse_date(existing.get("accomplished_date"))
            accomplished_value = col4.date_input(
                "Date Accomplished",
                value=accomplished_existing,
            )
            remarks_value = st.text_input("Remarks / Audit Reference", value=_clean_text(existing.get("remarks")))
            save_assignment = st.form_submit_button("Save Monthly Assignment", type="primary", use_container_width=True)
        if save_assignment:
            try:
                upsert_schedule_entry(
                    client,
                    master_id=selected_master_id,
                    schedule_year=year,
                    schedule_month=selected_month,
                    auditor_full_name=assigned_auditor,
                    status=status_value,
                    planned_date=planned_value,
                    accomplished_date=accomplished_value,
                    remarks=remarks_value,
                    actor=current_name,
                )
                st.success("Monthly audit assignment saved successfully.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
        if existing and st.button("Delete This Monthly Assignment", key="iars_gantt_delete_assignment"):
            try:
                delete_schedule_entry(client, str(existing.get("id")))
                st.success("Monthly audit assignment deleted.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    else:
        st.markdown("### Update My Audit Accomplishment")
        own_entries = [
            entry for entry in entries
            if _name_key(entry.get("auditor_full_name")) == _name_key(current_name)
        ]
        if not own_entries:
            st.info("No audit schedule is assigned to your account for the selected year.")
            return
        master_map = {str(row.get("id")): row for row in masters}
        entry_map = {str(entry.get("id")): entry for entry in own_entries}
        entry_ids = list(entry_map)
        selected_entry_id = st.selectbox(
            "Assigned Audit",
            entry_ids,
            format_func=lambda item: (
                f"{month_name[int(entry_map[item].get('schedule_month') or 1)]} — "
                f"{_clean_text(master_map.get(str(entry_map[item].get('master_id')), {}).get('custodian'))} — "
                f"{_clean_text(master_map.get(str(entry_map[item].get('master_id')), {}).get('audit_task'))}"
            ),
            key="iars_gantt_auditor_entry",
        )
        selected_entry = entry_map[selected_entry_id]
        with st.form("iars_gantt_auditor_accomplishment_form"):
            col1, col2 = st.columns(2)
            current_status = effective_status(selected_entry)
            status_value = col1.selectbox("Status", GANTT_STATUSES, index=GANTT_STATUSES.index(current_status))
            accomplished_value = col2.date_input(
                "Date Accomplished",
                value=_parse_date(selected_entry.get("accomplished_date")),
            )
            st.text_input("Assigned Auditor", value=f"{current_name} — {nickname_for(current_name)}", disabled=True)
            st.text_input("Planned Audit Date", value=_date_text(selected_entry.get("planned_date")), disabled=True)
            remarks_value = st.text_area("Accomplishment Remarks", value=_clean_text(selected_entry.get("remarks")))
            save_update = st.form_submit_button("Save Accomplishment Update", type="primary", use_container_width=True)
        if save_update:
            try:
                update_auditor_accomplishment(
                    client,
                    entry_id=selected_entry_id,
                    assigned_auditor=_clean_text(selected_entry.get("auditor_full_name")),
                    current_user_name=current_name,
                    status=status_value,
                    accomplished_date=accomplished_value,
                    remarks=remarks_value,
                )
                st.success("Your audit accomplishment was updated successfully.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


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
        '<p>Admin-only maintenance for Company / Department, Custodian, Audit Task, and Accountability. Frequency is calculated automatically from Done audits.</p></div>',
        unsafe_allow_html=True,
    )
    setup = gantt_setup_status(client)
    if not setup.ready:
        st.warning(setup.message)
        st.code("SUPABASE_GANTT_SETUP.sql", language=None)
        return

    template = Path(template_path)
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
        key="iars_gantt_master_upload",
    )
    if uploaded is not None:
        try:
            parsed = parse_master_upload(uploaded.getvalue())
            st.success(f"Validation passed: {len(parsed):,} master-data row(s) detected.")
            preview = parsed[[
                "company_department", "custodian", "audit_task", "accountability"
            ]].rename(columns={
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
            f"{_clean_text(record_map[item].get('audit_task'))}"
        ),
        key="iars_gantt_master_record_select",
    )
    selected = record_map.get(selected_id, {})
    with st.form("iars_gantt_master_record_form"):
        col1, col2 = st.columns(2)
        company = col1.text_input("Company / Department", value=_clean_text(selected.get("company_department")))
        custodian = col2.text_input("Custodian", value=_clean_text(selected.get("custodian")))
        col3, col4 = st.columns([2, 1])
        task = col3.text_input("Audit Task", value=_clean_text(selected.get("audit_task")))
        accountability = col4.text_input("Accountability", value=_clean_text(selected.get("accountability")))
        active = st.checkbox("Active record", value=bool(selected.get("active", True)))
        st.caption("Frequency is read-only and is calculated from the number of Done audits for the custodian in the selected year.")
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
        if st.button(action_label, key="iars_gantt_toggle_master"):
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
