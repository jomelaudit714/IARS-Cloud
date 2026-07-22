
from pathlib import Path
import os

# Prevent PyArrow threaded mimalloc crashes before pandas/Streamlit data operations.
os.environ.setdefault("ARROW_DEFAULT_MEMORY_POOL", "system")
from io import BytesIO
from datetime import date
import base64
import hashlib
import html
import pickle
import subprocess
import sys
import tempfile
import re
import time

import pandas as pd
import streamlit as st

from iars_pdf_editor import pdf_textbox_editor
from iars_theme import (
    apply_iars_theme,
    render_app_header,
    render_feature_cards,
    render_metric_cards,
    render_section_header,
    render_sidebar_brand,
    render_sidebar_status,
    render_dashboard_hero,
    render_library_note,
    render_stepper,
    render_activity_list,
    # render_transition_guard intentionally not imported in V4.4.19 - sidebar navigation should not show a loading veil.
)
from iars_auth import (
    read_auth_config,
    render_auth_gate,
    render_account_sidebar,
    render_account_admin_page,
    render_profile_menu,
    is_admin_user,
)

from iars_archive import (
    ArchiveConfig,
    ArchiveError,
    ArchiveNotConfiguredError,
    DuplicateArchiveError,
    archive_is_configured,
    create_archive_client,
    delete_pdf as delete_archived_pdf,
    download_pdf as download_archived_pdf,
    extract_archive_metadata,
    filter_records as filter_archive_records,
    human_file_size,
    list_records as list_archive_records,
    list_additional_auditors,
    add_additional_auditor,
    read_archive_config,
    upload_pdf as upload_archived_pdf,
)


from iars_document_library import (
    COLLECTION_POLICIES,
    COLLECTION_TEMPLATES,
    DocumentLibraryConfig,
    DocumentLibraryError,
    DocumentLibraryNotConfiguredError,
    DuplicateDocumentError,
    DuplicateFolderError,
    create_document_folder,
    create_document_library_client,
    delete_document,
    document_library_is_configured,
    download_document,
    filter_documents,
    human_file_size as document_file_size,
    list_document_folders,
    list_documents,
    read_document_library_config,
    upload_document,
)

from iars_parser import (
    AUDITORS,
    master_finding_options,
    master_response_options,
    master_frequency_options,
    build_records,
    normalize_output_with_master,
    excel_bytes,
)

from iars_weekly_itinerary import (
    WeeklyItineraryConfig,
    render_dashboard_weekly_itinerary,
    render_weekly_itinerary_page,
)


SIDEBAR_EXPAND_ONCE_KEY = "iars_force_sidebar_expand_once"


def _force_sidebar_expanded_once(token: str) -> None:
    """Open the Streamlit 1.47 sidebar once after a successful sign-in.

    This helper intentionally lives in app.py so deployment cannot fail from
    a mismatched iars_theme.py file. It clears Streamlit's remembered collapsed
    state and clicks the native restore control only when the sidebar is closed.
    """
    import json
    import streamlit.components.v1 as components

    safe_token = json.dumps(str(token or ""))
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          html, body {{
            margin: 0;
            padding: 0;
            width: 1px;
            height: 1px;
            overflow: hidden;
            background: transparent;
          }}
        </style>
      </head>
      <body>
        <script>
          (() => {{
            const resetToken = {safe_token};
            const hostWindow = window.parent;
            const hostDocument = hostWindow.document;
            let attempts = 0;
            let stopped = false;

            function clearSavedSidebarState() {{
              try {{
                const keys = [];
                for (let index = 0; index < hostWindow.localStorage.length; index += 1) {{
                  const key = hostWindow.localStorage.key(index);
                  if (key && key.startsWith("stSidebarCollapsed-")) keys.push(key);
                }}
                for (const key of keys) hostWindow.localStorage.setItem(key, "false");
                hostWindow.localStorage.setItem("iarsSidebarResetToken", resetToken);
              }} catch (_) {{
                // Browser storage may be blocked. The native button remains the fallback.
              }}
            }}

            function expandSidebar() {{
              if (stopped) return;
              clearSavedSidebarState();

              const sidebar = hostDocument.querySelector(
                'section[data-testid="stSidebar"]'
              );
              if (sidebar && sidebar.getAttribute("aria-expanded") === "true") {{
                stopped = true;
                return;
              }}

              const expandButton = hostDocument.querySelector(
                '[data-testid="stExpandSidebarButton"]'
              );
              if (expandButton) {{
                expandButton.click();
                hostWindow.setTimeout(clearSavedSidebarState, 120);
                stopped = true;
                return;
              }}

              attempts += 1;
              if (attempts < 100) hostWindow.setTimeout(expandSidebar, 50);
            }}

            clearSavedSidebarState();
            expandSidebar();
          }})();
        </script>
      </body>
    </html>
    """
    components.html(html, width=1, height=1, scrolling=False)



def _apply_v4475_layout_refinements() -> None:
    """Compact the main Dashboard and align the sidebar branding."""
    st.markdown(
        """
        <style>
        /* Sidebar branding and vertical spacing */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 3px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stImage"] {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: -2px auto 0 !important;
            text-align: center !important;
        }
        section[data-testid="stSidebar"] [data-testid="stImage"] > div,
        section[data-testid="stSidebar"] [data-testid="stImage"] figure {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            margin: 0 auto !important;
        }
        section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stImage"]) {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        section[data-testid="stSidebar"] [data-testid="stImage"] img {
            display: block !important;
            margin: 0 auto !important;
            /* The supplied EDL PNG has asymmetric transparent padding. */
            transform: translateX(22px) !important;
        }
        section[data-testid="stSidebar"] .edl-sidebar-brand {
            margin-top: -.30rem !important;
            padding-top: 0 !important;
            padding-bottom: .22rem !important;
            text-align: center !important;
        }
        section[data-testid="stSidebar"] .edl-sidebar-brand h3 {
            margin-top: .35rem !important;
            margin-bottom: .03rem !important;
        }
        section[data-testid="stSidebar"] .edl-sidebar-section {
            margin-top: .02rem !important;
            margin-bottom: .18rem !important;
        }
        section[data-testid="stSidebar"] hr {
            margin: .42rem 0 !important;
        }

        /* Dashboard top-space recovery */
        .iars-dashboard-v4475-marker {display:none !important;}
        .stApp:has(.iars-dashboard-v4475-marker) .block-container {
            padding-top: 0 !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-topbar {
            margin-top: -25px !important;
            margin-bottom: .22rem !important;
            padding-top: .48rem !important;
            padding-bottom: .48rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-section-head {
            margin-top: .04rem !important;
            margin-bottom: .42rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .iars-dashboard-welcome {
            margin-top: -.05rem !important;
            margin-bottom: .38rem !important;
            align-items: flex-end !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .iars-dashboard-welcome h2 {
            font-size: 1.72rem !important;
            line-height: 1.08 !important;
            font-weight: 850 !important;
            letter-spacing: -.025em !important;
            margin: 0 0 .18rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .iars-dashboard-welcome p {
            font-size: .90rem !important;
            line-height: 1.25 !important;
            margin: 0 !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker)
        .block-container > div[data-testid="stVerticalBlock"] {
            gap: .48rem !important;
        }

        /* Dashboard metric cards */
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-grid {
            grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
            gap: .82rem !important;
            margin-top: .02rem !important;
            margin-bottom: .72rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-card {
            min-height: 152px !important;
            padding: 1.28rem 1.12rem 1.08rem !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-icon {
            width: 44px !important;
            height: 44px !important;
            right: .88rem !important;
            top: .82rem !important;
            font-size: 1.30rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-label {
            font-size: .92rem !important;
            line-height: 1.18 !important;
            padding-right: 3.4rem !important;
            margin-top: .35rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-value,
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-value.long {
            font-size: 2.02rem !important;
            line-height: 1.04 !important;
            margin: .62rem 0 .30rem !important;
            padding-right: 3.4rem !important;
        }
        .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-note {
            font-size: .82rem !important;
            line-height: 1.28 !important;
            padding-right: 2.9rem !important;
        }
        @media (max-width: 1200px) {
            .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-grid {
                grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            }
        }
        @media (max-width: 760px) {
            .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            }
            .stApp:has(.iars-dashboard-v4475-marker) .edl-metric-card {
                min-height: 138px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


EXTRACTION_WORKER_PATH = Path(__file__).with_name("iars_extract_worker.py")


def _build_records_isolated(
    pdf_bytes: bytes,
    filename: str,
    master_df,
    auditors_df,
    master_sheets,
    *,
    timeout_seconds: int = 240,
    worker_path: Path | None = None,
):
    """Run the unchanged IARS parser in a separate Python process.

    PDF and OCR libraries contain native code. A malformed PDF or a native
    library crash must not terminate the Streamlit application. The worker
    process returns the same ``(result_df, header, items)`` tuple produced by
    ``iars_parser.build_records``. If the worker stops unexpectedly, the main
    application stays online and reports a processing error for that PDF.
    """
    worker = Path(worker_path or EXTRACTION_WORKER_PATH)
    if not worker.exists():
        raise RuntimeError(f"Extraction worker is missing: {worker.name}")

    payload = {
        "pdf_bytes": bytes(pdf_bytes or b""),
        "filename": str(filename or "uploaded_report.pdf"),
        "master_df": master_df,
        "auditors_df": auditors_df,
        "master_sheets": master_sheets,
    }

    with tempfile.TemporaryDirectory(prefix="iars_extract_") as temp_dir:
        temp_root = Path(temp_dir)
        input_path = temp_root / "input.pkl"
        output_path = temp_root / "output.pkl"
        with input_path.open("wb") as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)

        try:
            completed = subprocess.run(
                [sys.executable, str(worker), str(input_path), str(output_path)],
                cwd=str(Path(__file__).resolve().parent),
                capture_output=True,
                text=True,
                timeout=max(30, int(timeout_seconds)),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"PDF extraction exceeded {timeout_seconds} seconds for {filename}."
            ) from exc

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()[-1600:]
            if completed.returncode < 0:
                signal_number = abs(completed.returncode)
                message = (
                    f"The PDF extraction engine stopped unexpectedly (signal {signal_number}) "
                    f"while processing {filename}. The IARS application remained online."
                )
            else:
                message = f"PDF extraction failed for {filename}."
            if detail:
                message += f" Details: {detail}"
            raise RuntimeError(message)

        if not output_path.exists():
            raise RuntimeError(f"The extraction worker returned no result for {filename}.")

        with output_path.open("rb") as handle:
            response = pickle.load(handle)

        if not isinstance(response, dict) or not response.get("ok"):
            error = "Unknown extraction worker error."
            if isinstance(response, dict):
                error = str(response.get("error") or error)
            raise RuntimeError(f"PDF extraction failed for {filename}: {error}")

        return response["result_df"], response["header"], response["items"]

st.set_page_config(
    page_title="Internal Audit Report System | EDL GROUP OF COMPANIES",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_iars_theme()
_apply_v4475_layout_refinements()
# V4.4.19: do not install the navigation loading veil. Streamlit will still rerun on clicks,
# but users will no longer see the "Loading / Please wait" card on every module switch.

auth_config = read_auth_config(st.secrets)
auth_client, auth_user = render_auth_gate(auth_config)

_sidebar_expand_token = st.session_state.pop(SIDEBAR_EXPAND_ONCE_KEY, "")
if _sidebar_expand_token:
    _force_sidebar_expanded_once(str(_sidebar_expand_token))

MASTER_DATA_PATH = Path("data/Master_Data.xlsx")

@st.cache_data(show_spinner=False)
def load_master_data(path: str):
    """Load permanent Master Data from repository."""
    xls = pd.ExcelFile(path)

    employees_df = pd.read_excel(path, sheet_name="Employees") if "Employees" in xls.sheet_names else pd.DataFrame()
    sheets = {
        sheet: pd.read_excel(path, sheet_name=sheet)
        for sheet in xls.sheet_names
    }

    return employees_df, sheets


def save_uploaded_master(uploaded_file):
    """Save uploaded Master Data to app folder.

    Note: On Streamlit Cloud, this persists during the current app runtime/session.
    For permanent update across redeploys, replace data/Master_Data.xlsx in GitHub.
    """
    MASTER_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MASTER_DATA_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())


def render_pdf_page(pdf_bytes: bytes, page_no: int, zoom: float = 1.4):
    """Render a PDF page to PNG for preview."""
    try:
        import fitz
        from PIL import Image
    except Exception:
        return None, None, None

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_no)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img, page.rect.width, page.rect.height


def draw_preview_box(img, x_percent, y_percent, box_width_px=220, box_height_px=32):
    """Draw a visible temporary box on the preview image before saving the tag."""
    try:
        from PIL import ImageDraw
    except Exception:
        return img

    if img is None:
        return img

    preview = img.copy()
    draw = ImageDraw.Draw(preview)
    img_w, img_h = preview.size

    x = float(x_percent) / 100 * img_w
    y = float(y_percent) / 100 * img_h

    rect = [
        x,
        y - box_height_px / 2,
        min(img_w - 1, x + box_width_px),
        min(img_h - 1, y + box_height_px / 2),
    ]

    # Multiple outlines make it visible without relying on a specific color too much.
    draw.rectangle(rect, outline="black", width=3)
    draw.rectangle([rect[0]+3, rect[1]+3, rect[2]-3, rect[3]-3], outline="white", width=2)
    return preview


def stamp_pdf_with_tags(pdf_bytes: bytes, tag_rows):
    """Insert single-line PDF tags using each textbox's exact selected font size."""
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for row in tag_rows:
        label_text = " ".join(str(row.get("Label Text", "") or "").split())
        if not label_text:
            continue

        try:
            page_index = int(row.get("Page", 1)) - 1
            x_percent = float(row.get("X %", 8))
            y_percent = float(row.get("Y %", 12))
            width_percent = float(row.get("Width %", 30))
            height_percent = float(row.get("Height %", 6))
            requested_font_size = float(row.get("Font Size", 11))
            style = str(row.get("Style", "Box") or "Box")
        except (TypeError, ValueError):
            continue

        if page_index < 0 or page_index >= len(doc):
            continue

        page = doc.load_page(page_index)
        x0 = max(0, min(100, x_percent)) / 100 * page.rect.width
        y0 = max(0, min(100, y_percent)) / 100 * page.rect.height
        width = max(1, min(100, width_percent)) / 100 * page.rect.width
        height = max(0.5, min(100, height_percent)) / 100 * page.rect.height
        x1 = min(page.rect.width, x0 + width)
        y1 = min(page.rect.height, y0 + height)
        rect = fitz.Rect(x0, y0, x1, y1)

        if style == "Highlight Box":
            page.draw_rect(rect, color=(0, 0, 0), fill=(1, 1, 0.65), width=0.7)
        elif style == "Box":
            page.draw_rect(rect, color=(0, 0, 0), fill=(1, 1, 1), width=0.7)

        horizontal_padding = min(2.0, max(0.7, rect.width * 0.02))
        vertical_padding = min(1.2, max(0.4, rect.height * 0.08))
        available_width = max(1.0, rect.width - (horizontal_padding * 2))
        available_height = max(1.0, rect.height - (vertical_padding * 2))

        # Respect the exact font size chosen in the PDF Tagging editor.
        # The editor expands the textbox height and offers Fit text for width.
        font_size = max(6.0, min(48.0, requested_font_size))

        # Vertically center the one-line tag inside the rectangle.
        baseline = rect.y0 + ((rect.height - font_size) / 2) + (font_size * 0.82)
        page.insert_text(
            fitz.Point(rect.x0 + horizontal_padding, baseline),
            label_text,
            fontsize=font_size,
            fontname="helv",
            color=(0, 0, 0),
        )

    output = BytesIO()
    doc.save(output, garbage=4, deflate=True)
    output.seek(0)
    return output.getvalue()


def image_to_data_uri(image):
    """Convert a rendered PIL page image to a browser-ready data URI."""
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def editor_file_id(file_name: str, pdf_bytes: bytes) -> str:
    digest = hashlib.sha256(pdf_bytes).hexdigest()[:12]
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in file_name)[:40]
    return f"{safe_name}_{digest}"


def component_editor_value(state):
    """Read the persistent Components v2 editor state."""
    if state is None:
        return {"pages": {}, "selected_id": None, "active_page": 1, "updated_at": 0}
    if isinstance(state, dict):
        value = state.get("editor", {})
    else:
        value = getattr(state, "editor", {})
    return value if isinstance(value, dict) else {"pages": {}}


def normalize_tag_text(tag_type: str, value: str):
    tag_type = str(tag_type or "").strip()
    value = str(value or "").strip()
    if not value:
        return ""

    mapping = {
        "Task ID": "Task ID",
        "Auditor": "Auditor",
        "Auditee": "Auditee",
        "Frequency Rate": "Frequency Rate",
        "Reaction": "Reaction",
    }
    label = mapping.get(tag_type, tag_type)
    return f"{label}: {value}"


def build_default_tag_rows(page_count: int = 1):
    return pd.DataFrame(
        [
            {"Page": 1, "Tag Type": "Task ID", "Value": "001", "Label Text": "Task ID: 001", "X %": 8.0, "Y %": 24.0, "Font Size": 11, "Style": "Box", "Box Width": 160, "Box Height": 24},
            {"Page": 1, "Tag Type": "Auditor", "Value": "Patricia Anne S. Del Rosario", "Label Text": "Auditor: Patricia Anne S. Del Rosario", "X %": 8.0, "Y %": 27.0, "Font Size": 11, "Style": "Box", "Box Width": 280, "Box Height": 24},
            {"Page": 1, "Tag Type": "Auditee", "Value": "Emerito Bondoc", "Label Text": "Auditee: Emerito Bondoc", "X %": 8.0, "Y %": 30.0, "Font Size": 11, "Style": "Box", "Box Width": 230, "Box Height": 24},
        ]
    )



def _clean_option(value):
    return " ".join(str(value or "").split()).strip()


def _master_display_option(value):
    """Preserve exact Master Data capitalization and internal spacing."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def get_employee_records(employees_df: pd.DataFrame):
    """Return canonical employee names and aliases from Master Data."""
    if employees_df is None or employees_df.empty:
        return []

    name_column = None
    for candidate in ("Employee Name", "Full Name", "Name"):
        if candidate in employees_df.columns:
            name_column = candidate
            break
    if not name_column:
        return []

    records = []
    for _, row in employees_df.iterrows():
        status = _clean_option(row.get("Status", "Active"))
        if status and status.casefold() not in {"active", ""}:
            continue
        full_name = _clean_option(row.get(name_column, ""))
        if not full_name:
            continue
        aliases = []
        for column in ("Alias 1", "Alias 2"):
            if column in employees_df.columns:
                alias = _clean_option(row.get(column, ""))
                if alias:
                    aliases.append(alias)
        records.append(
            {
                "name": full_name,
                "employee_id": _clean_option(row.get("Employee ID", "")),
                "aliases": aliases,
            }
        )
    return records


def normalize_name_for_match(value: str) -> str:
    return re.sub(r"[^A-Z0-9 ]+", " ", _clean_option(value).upper()).strip()


def resolve_auditee_defaults(raw_name: str, employee_records):
    """Resolve PDF header auditees to official Master Data employee names."""
    raw_name = _clean_option(raw_name)
    if not raw_name or not employee_records:
        return []

    chunks = [
        _clean_option(chunk)
        for chunk in re.split(r"\s+(?:AND|&)\s+|[;\n]+", raw_name, flags=re.I)
        if _clean_option(chunk)
    ]
    if not chunks:
        chunks = [raw_name]

    resolved = []
    for chunk in chunks:
        chunk_norm = normalize_name_for_match(chunk)
        chunk_tokens = [token for token in chunk_norm.split() if token]
        best_name = ""
        best_score = 0

        for record in employee_records:
            variants = [record["name"], *record.get("aliases", [])]
            for variant in variants:
                variant_norm = normalize_name_for_match(variant)
                variant_tokens = [token for token in variant_norm.split() if token]
                if not variant_tokens:
                    continue

                score = 0
                if chunk_norm == variant_norm:
                    score = 100
                elif variant_norm in chunk_norm or chunk_norm in variant_norm:
                    score = 90
                else:
                    shared = len(set(chunk_tokens) & set(variant_tokens))
                    if chunk_tokens and variant_tokens and chunk_tokens[0] == variant_tokens[0]:
                        score += 35
                    if chunk_tokens and variant_tokens and chunk_tokens[-1] == variant_tokens[-1]:
                        score += 35
                    score += min(shared, 3) * 10

                if score > best_score:
                    best_score = score
                    best_name = record["name"]

        if best_name and best_score >= 45 and best_name not in resolved:
            resolved.append(best_name)

    return resolved


def official_auditee_string(raw_name: str, employee_records) -> str:
    return "; ".join(resolve_auditee_defaults(raw_name, employee_records))


def build_auditor_options(master_auditors_df: pd.DataFrame, extra_rows):
    options = []
    seen = set()

    if master_auditors_df is not None and not master_auditors_df.empty and "Auditor" in master_auditors_df.columns:
        for _, row in master_auditors_df.iterrows():
            status = _clean_option(row.get("Status", "Active"))
            if status and status.casefold() not in {"active", ""}:
                continue
            name = _master_display_option(row.get("Auditor", ""))
            if name and name.casefold() not in seen:
                options.append(name)
                seen.add(name.casefold())

    for row in extra_rows or []:
        status = _clean_option(row.get("status", "Active"))
        if status.casefold() != "active":
            continue
        name = _master_display_option(row.get("auditor_name", ""))
        if name and name.casefold() not in seen:
            options.append(name)
            seen.add(name.casefold())

    return sorted(options, key=str.casefold)


def render_auditor_selector(label: str, key: str, auditor_options):
    """Search button + searchable dropdown for a single auditor."""
    search_state = f"{key}_applied_search"
    search_col, button_col, clear_col = st.columns([3, 1, 1])
    with search_col:
        query = st.text_input(
            "Search auditor",
            key=f"{key}_search_input",
            placeholder="Enter part of the auditor's name",
            label_visibility="collapsed",
        )
    with button_col:
        if st.button("Search", key=f"{key}_search_button", use_container_width=True):
            st.session_state[search_state] = query.strip()
    with clear_col:
        if st.button("Clear", key=f"{key}_clear_button", use_container_width=True):
            st.session_state[search_state] = ""

    applied = str(st.session_state.get(search_state, "") or "").strip().casefold()
    filtered = [name for name in auditor_options if applied in name.casefold()] if applied else list(auditor_options)
    if applied and not filtered:
        st.warning("No active auditor matched the search. Clear the search or add a new auditor.")

    select_options = [""] + filtered
    return st.selectbox(
        label,
        select_options,
        index=0,
        key=f"{key}_select",
        format_func=lambda value: "Select an auditor" if not value else value,
    )


def render_auditee_selector(label: str, key: str, employee_options, defaults=None):
    valid_defaults = [name for name in (defaults or []) if name in employee_options]
    return st.multiselect(
        label,
        employee_options,
        default=valid_defaults,
        key=key,
        placeholder="Type to search Master Data employee names",
    )


def canonical_names_from_result(result_df: pd.DataFrame) -> str:
    if result_df is None or result_df.empty or "Name" not in result_df.columns:
        return ""
    names = []
    for value in result_df["Name"].tolist():
        name = _clean_option(value)
        if name and name.casefold() not in {"none", "n/a", "not found"} and name not in names:
            names.append(name)
    return "; ".join(names)


@st.cache_data(show_spinner=False)
def cached_archive_metadata(pdf_bytes: bytes, filename: str):
    return extract_archive_metadata(pdf_bytes, filename)


def _normalized_audit_reference(value: str) -> str:
    """Normalize IAD reference numbers for reliable duplicate matching."""
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _normalized_archive_filename(value: str) -> str:
    """Normalize PDF filenames for a conservative duplicate fallback."""
    filename = Path(str(value or "")).name.casefold().strip()
    return re.sub(r"\s+", " ", filename)


def uploaded_archive_duplicate_matches(
    pdf_files,
    archive_records,
    *,
    metadata_loader=None,
) -> tuple[list[dict[str, str]], list[str]]:
    """Return duplicate details and non-fatal metadata warnings.

    Matching order:
    1. exact original-PDF SHA256
    2. normalized IAD reference
    3. exact original filename as a conservative fallback

    Metadata extraction errors are handled per PDF, so one unreadable file no
    longer disables duplicate checking for every uploaded report.
    """
    metadata_loader = metadata_loader or cached_archive_metadata

    records_by_reference: dict[str, list[dict]] = {}
    records_by_hash: dict[str, dict] = {}
    records_by_filename: dict[str, list[dict]] = {}

    for record in archive_records or []:
        reference = str(record.get("audit_reference", "") or "").strip()
        normalized_reference = _normalized_audit_reference(reference)
        if normalized_reference:
            records_by_reference.setdefault(normalized_reference, []).append(record)

        digest = str(record.get("sha256", "") or "").strip().lower()
        if digest:
            records_by_hash[digest] = record

        normalized_filename = _normalized_archive_filename(
            str(record.get("original_filename", "") or "")
        )
        if normalized_filename:
            records_by_filename.setdefault(normalized_filename, []).append(record)

    matches: list[dict[str, str]] = []
    warnings: list[str] = []
    seen: set[str] = set()

    for pdf_file in pdf_files or []:
        uploaded_name = Path(str(getattr(pdf_file, "name", "") or "uploaded.pdf")).name
        pdf_bytes = pdf_file.getvalue()
        digest = hashlib.sha256(pdf_bytes).hexdigest().lower()

        extracted_reference = ""
        try:
            defaults = metadata_loader(pdf_bytes, uploaded_name) or {}
            extracted_reference = str(defaults.get("audit_reference", "") or "").strip()
        except Exception as exc:
            warnings.append(f"{uploaded_name}: unable to read the IAD reference ({exc})")

        normalized_reference = _normalized_audit_reference(extracted_reference)
        normalized_filename = _normalized_archive_filename(uploaded_name)

        matched_record = records_by_hash.get(digest)
        match_basis = "exact PDF file"

        if matched_record is None and normalized_reference:
            reference_matches = records_by_reference.get(normalized_reference, [])
            matched_record = reference_matches[0] if reference_matches else None
            match_basis = "IAD reference"

        if matched_record is None and normalized_filename:
            filename_matches = records_by_filename.get(normalized_filename, [])
            matched_record = filename_matches[0] if filename_matches else None
            match_basis = "same filename"

        if matched_record is None:
            continue

        archived_reference = str(
            matched_record.get("audit_reference", "") or ""
        ).strip()
        archived_filename = Path(
            str(matched_record.get("original_filename", "") or uploaded_name)
        ).name
        display_value = archived_reference or extracted_reference or archived_filename
        identity = (
            _normalized_audit_reference(archived_reference or extracted_reference)
            or _normalized_archive_filename(archived_filename)
            or digest
        )
        if identity in seen:
            continue
        seen.add(identity)

        matches.append(
            {
                "display": display_value,
                "uploaded_filename": uploaded_name,
                "archived_filename": archived_filename,
                "audit_reference": archived_reference or extracted_reference,
                "match_basis": match_basis,
            }
        )

    return matches, warnings


def uploaded_archive_duplicate_references(pdf_files, archive_records) -> list[str]:
    """Compatibility wrapper returning duplicate display labels only."""
    matches, _ = uploaded_archive_duplicate_matches(pdf_files, archive_records)
    return [match["display"] for match in matches]


def render_duplicate_archive_notice(
    duplicate_matches: list[dict[str, str]],
    duplicate_check_error: str = "",
    duplicate_metadata_warnings: list[str] | None = None,
) -> None:
    """Render persistent duplicate-check feedback in the upload page."""
    duplicate_metadata_warnings = duplicate_metadata_warnings or []

    if duplicate_matches:
        duplicate_lines = []
        for match in duplicate_matches:
            reference = str(match.get("audit_reference", "") or "").strip()
            archived_filename = str(
                match.get("archived_filename", "") or ""
            ).strip()
            basis = str(match.get("match_basis", "") or "archive match").strip()
            label = reference or archived_filename or str(
                match.get("display", "") or "Archived report"
            )
            duplicate_lines.append(
                f"- **{label}** — {archived_filename} ({basis})"
            )

        st.error(
            "**Duplicate report(s) detected — already saved in the PDF Archive.**\n\n"
            + "\n".join(duplicate_lines)
            + "\n\nPlease review the uploaded report(s) before continuing."
        )

    if duplicate_check_error:
        st.warning(
            "**Duplicate checking could not be completed.** "
            f"{duplicate_check_error} Extraction is still available, but "
            "please verify the PDF Archive manually before saving."
        )
    elif duplicate_metadata_warnings and not duplicate_matches:
        st.warning(
            "The IAD reference could not be read from one or more PDFs. "
            "Exact-file and filename duplicate checks were still completed."
        )


@st.cache_resource(show_spinner=False)
def cached_archive_client(url: str, service_role_key: str, bucket: str, table: str):
    return create_archive_client(
        ArchiveConfig(
            url=url,
            service_role_key=service_role_key,
            bucket=bucket,
            table=table,
        )
    )


def archive_client_or_none(config: ArchiveConfig):
    if not archive_is_configured(config):
        return None
    try:
        return cached_archive_client(
            config.url,
            config.service_role_key,
            config.bucket,
            config.table,
        )
    except Exception:
        return None



@st.cache_resource(show_spinner=False)
def cached_document_library_client(
    url: str,
    service_role_key: str,
    bucket: str,
    table: str,
    folders_table: str,
):
    return create_document_library_client(
        DocumentLibraryConfig(
            url=url,
            service_role_key=service_role_key,
            bucket=bucket,
            table=table,
            folders_table=folders_table,
        )
    )


def document_library_client_or_none(config: DocumentLibraryConfig):
    if not document_library_is_configured(config):
        return None
    try:
        return cached_document_library_client(
            config.url,
            config.service_role_key,
            config.bucket,
            config.table,
            config.folders_table,
        )
    except Exception:
        return None

def archive_access_granted(config: ArchiveConfig) -> bool:
    if not archive_is_configured(config):
        return False
    if not config.access_pin:
        return False
    return bool(st.session_state.get("archive_access_granted", False))


def render_archive_setup_notice():
    st.warning("Permanent PDF archiving is not configured yet.")
    st.markdown(
        "1. Create a Supabase project.\n"
        "2. Run `SUPABASE_SETUP.sql` in the Supabase SQL Editor.\n"
        "3. Copy the values from `.streamlit/secrets.toml.example` into Streamlit **App settings > Secrets**.\n"
        "4. Use the **service-role key** only in Streamlit Secrets. Never commit it to GitHub."
    )
    st.code(
        '[supabase]\n'
        'url = "https://YOUR-PROJECT.supabase.co"\n'
        'service_role_key = "YOUR-SERVICE-ROLE-KEY"\n'
        'bucket = "audit-pdf-archive"\n'
        'table = "pdf_archive"\n\n'
        '[archive]\n'
        'access_pin = "YOUR-STRONG-INTERNAL-PIN"',
        language="toml",
    )


def render_archive_login(config: ArchiveConfig) -> bool:
    if not archive_is_configured(config):
        render_archive_setup_notice()
        return False
    if not config.access_pin:
        st.error("Set `[archive].access_pin` in Streamlit Secrets before opening the PDF archive.")
        return False
    if st.session_state.get("archive_access_granted", False):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.success("Saved PDFs archive is unlocked for this browser session.")
        with col_b:
            if st.button("Lock Archive"):
                st.session_state["archive_access_granted"] = False
                st.rerun()
        return True

    pin = st.text_input("Archive access PIN", type="password", key="archive_pin_input")
    if st.button("Unlock Saved PDFs", type="primary"):
        if pin == config.access_pin:
            st.session_state["archive_access_granted"] = True
            st.rerun()
        else:
            st.error("Incorrect archive PIN.")
    return False


def archive_pdf_with_feedback(
    client,
    config: ArchiveConfig,
    *,
    pdf_bytes: bytes,
    filename: str,
    audit_reference: str,
    auditee_name: str,
    document_type: str,
    uploaded_by: str,
):
    try:
        record = upload_archived_pdf(
            client,
            config,
            pdf_bytes=pdf_bytes,
            original_filename=filename,
            audit_reference=audit_reference,
            auditee_name=auditee_name,
            document_type=document_type,
            uploaded_by=uploaded_by,
        )
        compression = record.get("_compression", {}) or {}
        storage_path = record.get("storage_path", "")
        original_size = compression.get("original_size")
        stored_size = compression.get("stored_size", record.get("file_size"))
        reduction = compression.get("reduction_percent", 0)
        note = compression.get("compression_note", "")

        if compression.get("compression_applied"):
            details = (
                f"{storage_path} | Compressed {human_file_size(original_size)} → "
                f"{human_file_size(stored_size)} ({reduction}% smaller)"
            )
            status = "Archived and compressed"
        else:
            size_text = human_file_size(stored_size) if stored_size is not None else ""
            details = f"{storage_path} | {size_text} | {note}".strip(" |")
            status = "Archived"

        return {"Status": status, "File": filename, "Details": details}
    except DuplicateArchiveError as exc:
        return {"Status": "Duplicate skipped", "File": filename, "Details": str(exc)}
    except Exception as exc:
        return {"Status": "Archive failed", "File": filename, "Details": str(exc)}



def _safe_library_key(value: object) -> str:
    """Return a stable Streamlit key segment for folders and documents."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "")).strip("_")
    return cleaned[:90] or "item"


def _docx_preview_text(file_bytes: bytes, *, max_characters: int = 30000) -> str:
    """Extract readable paragraph text from a DOCX without extra dependencies."""
    import zipfile
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(BytesIO(file_bytes)) as archive:
        document_xml = archive.read("word/document.xml")
    root = ET.fromstring(document_xml)
    paragraphs: list[str] = []
    for paragraph in root.iter():
        if not str(paragraph.tag).endswith("}p"):
            continue
        parts = [
            str(node.text or "")
            for node in paragraph.iter()
            if str(node.tag).endswith("}t") and node.text
        ]
        line = "".join(parts).strip()
        if line:
            paragraphs.append(line)
        if sum(len(item) for item in paragraphs) >= max_characters:
            break
    return "\n\n".join(paragraphs)[:max_characters]


def _render_policy_document_preview(
    selected_bytes: bytes,
    selected_record: dict,
    *,
    key_prefix: str,
) -> None:
    """Render a readable preview for supported company-folder documents."""
    extension = str(selected_record.get("file_extension", "") or "").lower()

    if extension == "pdf":
        try:
            import fitz

            pdf_document = fitz.open(stream=selected_bytes, filetype="pdf")
            page_count = len(pdf_document)
            if page_count <= 0:
                st.warning("The selected PDF contains no readable pages.")
                return
            preview_page = st.number_input(
                "Page to read",
                min_value=1,
                max_value=page_count,
                value=1,
                step=1,
                key=f"{key_prefix}_pdf_page",
            )
            preview_image, _, _ = render_pdf_page(
                selected_bytes,
                int(preview_page) - 1,
                zoom=1.35,
            )
            if preview_image is not None:
                st.image(
                    preview_image,
                    caption=f"Page {int(preview_page)} of {page_count}",
                    use_container_width=True,
                )
            else:
                st.warning("The selected PDF page could not be rendered.")
        except Exception as exc:
            st.warning(f"PDF preview is unavailable: {exc}")
        return

    if extension == "docx":
        try:
            preview_text = _docx_preview_text(selected_bytes)
            if preview_text:
                st.text_area(
                    "Document preview",
                    value=preview_text,
                    height=520,
                    disabled=True,
                    key=f"{key_prefix}_docx_preview",
                )
            else:
                st.info("No readable paragraph text was found in this Word document.")
        except Exception as exc:
            st.warning(f"Word preview is unavailable: {exc}")
        return

    if extension == "xlsx":
        try:
            workbook = pd.ExcelFile(BytesIO(selected_bytes))
            selected_sheet = st.selectbox(
                "Worksheet to read",
                workbook.sheet_names,
                key=f"{key_prefix}_xlsx_sheet",
            )
            worksheet = pd.read_excel(
                BytesIO(selected_bytes),
                sheet_name=selected_sheet,
            )
            st.dataframe(
                worksheet.head(300),
                use_container_width=True,
                hide_index=True,
            )
            if len(worksheet) > 300:
                st.caption("Preview is limited to the first 300 rows.")
        except Exception as exc:
            st.warning(f"Excel preview is unavailable: {exc}")
        return

    st.info(
        "This older file format cannot be previewed safely inside IARS. "
        "Use the download button to open it in its original application."
    )


@st.dialog("Create Company Folder", width="medium")
def render_create_policy_folder_dialog(
    client,
    config: DocumentLibraryConfig,
    current_user: dict,
    *,
    folders_cache_key: str,
) -> None:
    """Create a company/group folder for Policies & Memoranda."""
    st.caption(
        "Use the official company or group name, such as Estancia De Lorenzo "
        "or EDL Group of Companies."
    )
    folder_name = st.text_input(
        "Company / Folder Name",
        placeholder="Example: Estancia De Lorenzo",
        key="policy_folder_create_name_v4_4_69",
    )
    folder_description = st.text_area(
        "Description (optional)",
        placeholder="Example: Policies and memoranda applicable to Estancia De Lorenzo.",
        key="policy_folder_create_description_v4_4_69",
    )
    if st.button(
        "Create Folder",
        type="primary",
        use_container_width=True,
        key="policy_folder_create_submit_v4_4_69",
    ):
        creator = str(
            current_user.get("full_name")
            or current_user.get("username")
            or "IARS User"
        )
        try:
            folder = create_document_folder(
                client,
                config,
                folder_name=folder_name,
                description=folder_description,
                created_by=creator,
                collection=COLLECTION_POLICIES,
            )
            _invalidate_session_cache(folders_cache_key)
            st.session_state["iars_policy_folder_success_v4_4_69"] = (
                f'Folder "{folder.get("folder_name", folder_name)}" was created successfully.'
            )
            st.rerun()
        except DuplicateFolderError as exc:
            st.warning(str(exc))
        except Exception as exc:
            st.error(str(exc))


@st.dialog("Policies & Memoranda Folder", width="large")
def render_policy_folder_documents_dialog(
    folder: dict,
    folder_records: list[dict],
    client,
    config: DocumentLibraryConfig,
    *,
    admin: bool,
    records_cache_key: str,
) -> None:
    """Show a company folder's documents in a readable/downloadable popup."""
    folder_name = str(folder.get("folder_name", "") or "Unfiled / General")
    folder_description = str(folder.get("description", "") or "").strip()
    st.markdown(f"### 📁 {folder_name}")
    if folder_description:
        st.caption(folder_description)

    if not folder_records:
        st.info("No policies or memoranda have been uploaded to this folder yet.")
        return

    display_rows = []
    for record in folder_records:
        display_rows.append(
            {
                "Title": record.get("title", ""),
                "Category": record.get("category", ""),
                "Version": record.get("version_label", ""),
                "Effective Date": record.get("effective_date", ""),
                "File Type": str(record.get("file_extension", "") or "").upper(),
                "Uploaded By": record.get("uploaded_by", ""),
                "Date Uploaded": str(record.get("uploaded_at", "") or "")[:10],
            }
        )
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)

    labels: list[str] = []
    records_by_label: dict[str, dict] = {}
    for index, record in enumerate(folder_records, start=1):
        label = (
            f"{record.get('title') or record.get('original_filename')} | "
            f"{record.get('category', '')} | "
            f"{str(record.get('file_extension', '') or '').upper()} | {index}"
        )
        labels.append(label)
        records_by_label[label] = record

    selected_label = st.selectbox(
        "Select a policy or memorandum to read",
        labels,
        key=f"policy_folder_document_select_{_safe_library_key(folder.get('id') or folder_name)}",
    )
    selected_record = records_by_label[selected_label]
    record_id = str(selected_record.get("id", "") or selected_record.get("storage_path", ""))
    record_key = _safe_library_key(record_id)
    bytes_key = f"policy_folder_document_bytes_{record_key}"
    loaded_id_key = f"policy_folder_document_loaded_id_{_safe_library_key(folder.get('id') or folder_name)}"

    metadata_left, metadata_right = st.columns(2)
    with metadata_left:
        st.markdown(f"**Category:** {selected_record.get('category', '') or 'General'}")
        st.markdown(f"**Version:** {selected_record.get('version_label', '') or 'Not specified'}")
    with metadata_right:
        st.markdown(f"**Effective Date:** {selected_record.get('effective_date', '') or 'Not specified'}")
        st.markdown(f"**File Size:** {document_file_size(selected_record.get('file_size'))}")

    description = str(selected_record.get("description", "") or "").strip()
    if description:
        st.caption(description)

    action_left, action_right = st.columns(2)
    with action_left:
        if st.button(
            "Open / Read Document",
            type="primary",
            use_container_width=True,
            key=f"policy_folder_open_{record_key}",
        ):
            try:
                selected_bytes = download_document(
                    client,
                    config,
                    str(selected_record.get("storage_path", "") or ""),
                )
                st.session_state[bytes_key] = selected_bytes
                st.session_state[loaded_id_key] = record_id
            except Exception as exc:
                st.error(str(exc))
    with action_right:
        st.caption("Open the document first to enable reading and downloading.")

    selected_bytes = None
    if st.session_state.get(loaded_id_key) == record_id:
        selected_bytes = st.session_state.get(bytes_key)

    if selected_bytes:
        st.download_button(
            "Download Selected Document",
            data=selected_bytes,
            file_name=str(selected_record.get("original_filename", "document")),
            mime=str(selected_record.get("mime_type", "application/octet-stream")),
            use_container_width=True,
            key=f"policy_folder_download_{record_key}",
        )
        st.divider()
        _render_policy_document_preview(
            selected_bytes,
            selected_record,
            key_prefix=f"policy_folder_preview_{record_key}",
        )

    if admin:
        with st.expander("Delete Selected Document — Administrator Only", expanded=False):
            st.warning("Deletion permanently removes the file and its library record.")
            confirmation = st.text_input(
                "Type DELETE to confirm",
                key=f"policy_folder_delete_confirm_{record_key}",
            )
            if st.button(
                "Delete Document",
                disabled=confirmation.strip().upper() != "DELETE",
                use_container_width=True,
                key=f"policy_folder_delete_{record_key}",
            ):
                try:
                    delete_document(client, config, selected_record)
                    _invalidate_session_cache(records_cache_key)
                    st.session_state.pop(bytes_key, None)
                    st.session_state.pop(loaded_id_key, None)
                    st.session_state["iars_policy_folder_success_v4_4_69"] = (
                        "The selected document was deleted successfully."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))


def render_policy_folder_library_page(
    *,
    client,
    config: DocumentLibraryConfig,
    ready: bool,
    current_user: dict,
    admin: bool,
) -> None:
    """Render Policies & Memoranda as company/group folders."""
    render_section_header(
        "Policies & Memoranda Archive",
        "Create company folders, upload controlled documents, and open each folder to read or download its contents.",
        badge="Company-Based Document Library",
    )
    render_library_note(
        "Company and group folders",
        "Create a folder for each company, such as Estancia De Lorenzo, or use EDL Group of Companies for group-wide policies and memoranda.",
        icon="📁",
    )

    if not ready or client is None:
        st.warning("The document library has not been configured in Supabase yet.")
        st.markdown(
            "Run `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql` for a new setup, or "
            "`SUPABASE_DOCUMENT_FOLDER_MIGRATION.sql` for an existing library."
        )
        return

    records_cache_key = "iars_doc_library_records_Policies_Memoranda_cache_v4_4_69"
    folders_cache_key = "iars_policy_company_folders_cache_v4_4_69"

    try:
        records = _session_ttl_cache(
            records_cache_key,
            120,
            lambda: list_documents(
                client,
                config,
                collection=COLLECTION_POLICIES,
                limit=3000,
            ),
        )
        folders = _session_ttl_cache(
            folders_cache_key,
            120,
            lambda: list_document_folders(
                client,
                config,
                collection=COLLECTION_POLICIES,
                active_only=True,
                limit=500,
            ),
        )
    except Exception as exc:
        st.error(
            "The company-folder feature is not ready in Supabase. Run "
            "`SUPABASE_DOCUMENT_FOLDER_MIGRATION.sql`, then refresh the app. "
            f"Details: {exc}"
        )
        return

    folder_name_by_id = {
        str(folder.get("id", "") or ""): str(folder.get("folder_name", "") or "")
        for folder in folders
        if str(folder.get("id", "") or "")
    }
    for record in records:
        record["folder_name"] = folder_name_by_id.get(
            str(record.get("folder_id", "") or ""),
            "Unfiled / General",
        )

    success_message = st.session_state.pop("iars_policy_folder_success_v4_4_69", "")
    if success_message:
        st.success(success_message)

    policy_count = sum(
        str(record.get("category", "") or "").casefold() == "policy"
        for record in records
    )
    memorandum_count = sum(
        str(record.get("category", "") or "").casefold() == "memorandum"
        for record in records
    )
    render_metric_cards(
        [
            {"label": "Company Folders", "value": f"{len(folders):,}", "note": "Active folders", "icon": "📁", "accent": "#C78B12"},
            {"label": "Total Documents", "value": f"{len(records):,}", "note": "Policies and memoranda", "icon": "📄", "accent": "#175CD3"},
            {"label": "Policies", "value": f"{policy_count:,}", "note": "Policy documents", "icon": "📘", "accent": "#148A4B"},
            {"label": "Memoranda", "value": f"{memorandum_count:,}", "note": "Memorandum documents", "icon": "📜", "accent": "#6938EF"},
        ]
    )

    action_left, action_right = st.columns([1, 4])
    with action_left:
        if st.button(
            "➕ Create Folder",
            type="primary",
            use_container_width=True,
            key="policy_create_folder_button_v4_4_69",
        ):
            render_create_policy_folder_dialog(
                client,
                config,
                current_user,
                folders_cache_key=folders_cache_key,
            )
    with action_right:
        st.caption(
            "Folders are shared with all signed-in IARS users. Use the official company or group name."
        )

    with st.expander("Upload Policy or Memorandum", expanded=False):
        if not folders:
            st.warning("Create at least one company/group folder before uploading a document.")

        uploaded_document = st.file_uploader(
            "Select Excel, Word or PDF file",
            type=["xlsx", "xls", "docx", "doc", "pdf"],
            key="document_upload_Policies_Memoranda_v4_4_69",
        )
        folder_options = [str(folder.get("folder_name", "") or "") for folder in folders]
        folder_by_name = {
            str(folder.get("folder_name", "") or ""): folder
            for folder in folders
        }
        selected_folder_name = st.selectbox(
            "Company / Group Folder",
            folder_options if folder_options else ["Create a folder first"],
            disabled=not bool(folder_options),
            key="policy_upload_folder_v4_4_69",
        )

        left, right = st.columns(2)
        with left:
            document_title = st.text_input(
                "Document Title",
                placeholder="Example: Revolving Fund Policy",
                key="document_title_Policies_Memoranda_v4_4_69",
            )
            document_category = st.selectbox(
                "Document Type",
                ["Policy", "Memorandum", "Procedure", "Guidelines", "Manual", "Circular", "Other"],
                key="document_category_Policies_Memoranda_v4_4_69",
            )
        with right:
            version_label = st.text_input(
                "Version / Revision",
                placeholder="Example: Rev. 02 or 2026 Edition",
                key="document_version_Policies_Memoranda_v4_4_69",
            )
            use_effective_date = st.checkbox(
                "Include effective/issuance date",
                key="document_use_date_Policies_Memoranda_v4_4_69",
            )
            effective_date = (
                st.date_input(
                    "Effective / Issuance Date",
                    key="document_effective_date_Policies_Memoranda_v4_4_69",
                )
                if use_effective_date
                else None
            )

        description = st.text_area(
            "Description / Purpose",
            placeholder="Briefly describe the scope or purpose of the document.",
            key="document_description_Policies_Memoranda_v4_4_69",
        )
        if st.button(
            "Upload to Selected Folder",
            type="primary",
            use_container_width=True,
            disabled=not bool(folder_options),
            key="document_upload_button_Policies_Memoranda_v4_4_69",
        ):
            if uploaded_document is None:
                st.error("Select a file before uploading.")
            else:
                selected_folder = folder_by_name.get(selected_folder_name, {})
                try:
                    uploader_name = str(
                        current_user.get("full_name")
                        or current_user.get("username")
                        or "IARS User"
                    )
                    record = upload_document(
                        client,
                        config,
                        collection=COLLECTION_POLICIES,
                        file_bytes=uploaded_document.getvalue(),
                        original_filename=uploaded_document.name,
                        title=document_title,
                        category=document_category,
                        description=description,
                        version_label=version_label,
                        effective_date=effective_date,
                        uploaded_by=uploader_name,
                        folder_id=str(selected_folder.get("id", "") or ""),
                        folder_name=selected_folder_name,
                    )
                    _invalidate_session_cache(records_cache_key)
                    st.session_state["iars_policy_folder_success_v4_4_69"] = (
                        f'{record.get("original_filename", uploaded_document.name)} was uploaded to "{selected_folder_name}".'
                    )
                    st.rerun()
                except DuplicateDocumentError as exc:
                    st.warning(str(exc))
                except Exception as exc:
                    st.error(str(exc))

    st.divider()
    render_section_header(
        "Company Folders",
        "Click a folder to view all documents assigned to that company or group.",
    )
    folder_search = st.text_input(
        "Search company folder",
        placeholder="Example: Estancia or EDL Group",
        key="policy_folder_search_v4_4_69",
    ).strip().casefold()

    folder_cards = list(folders)
    unfiled_records = [
        record for record in records
        if not str(record.get("folder_id", "") or "").strip()
    ]
    if unfiled_records:
        folder_cards.append(
            {
                "id": "",
                "folder_name": "Unfiled / General",
                "description": "Documents uploaded before company folders were enabled.",
                "_system_folder": True,
            }
        )

    if folder_search:
        folder_cards = [
            folder for folder in folder_cards
            if folder_search in str(folder.get("folder_name", "") or "").casefold()
        ]

    if not folder_cards:
        st.info("No company folders match the current search.")
        return

    columns = st.columns(3, gap="large")
    for index, folder in enumerate(folder_cards):
        folder_id = str(folder.get("id", "") or "")
        if folder_id:
            company_records = [
                record for record in records
                if str(record.get("folder_id", "") or "") == folder_id
            ]
        else:
            company_records = unfiled_records

        folder_name = str(folder.get("folder_name", "") or "Unfiled / General")
        folder_description = str(folder.get("description", "") or "").strip()
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"### 📁 {folder_name}")
                st.caption(
                    folder_description
                    or "Company-specific policies and memoranda."
                )
                st.markdown(
                    f"**{len(company_records):,} document(s)**"
                )
                if st.button(
                    "Open Folder",
                    use_container_width=True,
                    key=f"policy_folder_open_button_{index}_{_safe_library_key(folder_id or folder_name)}",
                ):
                    render_policy_folder_documents_dialog(
                        folder,
                        company_records,
                        client,
                        config,
                        admin=admin,
                        records_cache_key=records_cache_key,
                    )


def render_document_library_page(
    *,
    collection: str,
    client,
    config: DocumentLibraryConfig,
    ready: bool,
    current_user: dict,
    admin: bool,
) -> None:
    is_templates = collection == COLLECTION_TEMPLATES
    if not is_templates:
        render_policy_folder_library_page(
            client=client,
            config=config,
            ready=ready,
            current_user=current_user,
            admin=admin,
        )
        return

    page_title = "Audit Workpapers Library"
    page_subtitle = "Upload, organize and download reusable count sheets, inventory forms, working papers and audit workpapers."
    render_section_header(
        page_title,
        page_subtitle,
        badge="Shared Document Library",
    )
    render_library_note(
        "Supported document formats",
        "Microsoft Excel (.xlsx/.xls), Microsoft Word (.docx/.doc) and PDF (.pdf). All signed-in auditors may view and download files; deletion is administrator-only.",
        icon="📁",
    )

    if not ready or client is None:
        st.warning("The document library has not been created in Supabase yet.")
        st.markdown(
            "Run `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql` in the same Supabase project used by IARS, then refresh the app."
        )
        st.code(
            '[supabase]\n'
            'documents_bucket = "iars-document-library"\n'
            'documents_table = "document_library"',
            language="toml",
        )
        return

    records_cache_key = f"iars_doc_library_records_{collection}_cache_v4_4_19"
    try:
        records = _session_ttl_cache(
            records_cache_key,
            180,
            lambda: list_documents(client, config, collection=collection, limit=2000),
        )
    except Exception as exc:
        st.error(f"Unable to load the document library: {exc}")
        return

    extension_counts = {
        "Excel": sum(str(r.get("file_extension", "")).lower() in {"xls", "xlsx"} for r in records),
        "Word": sum(str(r.get("file_extension", "")).lower() in {"doc", "docx"} for r in records),
        "PDF": sum(str(r.get("file_extension", "")).lower() == "pdf" for r in records),
    }
    render_metric_cards(
        [
            {"label": "Total Documents", "value": f"{len(records):,}", "note": "Available to authorized users", "icon": "📁", "accent": "#C78B12"},
            {"label": "Excel Files", "value": f"{extension_counts['Excel']:,}", "note": "Worksheets and forms", "icon": "📊", "accent": "#178A52"},
            {"label": "Word Files", "value": f"{extension_counts['Word']:,}", "note": "Editable documents", "icon": "📝", "accent": "#2563EB"},
            {"label": "PDF Files", "value": f"{extension_counts['PDF']:,}", "note": "Controlled references", "icon": "📕", "accent": "#D92D20"},
        ]
    )

    upload_title = "Upload Report Template" if is_templates else "Upload Policy or Memorandum"
    with st.expander(upload_title, expanded=False):
        categories = (
            [
                "Count Sheet",
                "Inventory Count Sheet",
                "Audit Report Template",
                "Working Paper",
                "Audit Checklist",
                "Reconciliation Template",
                "Other",
            ]
            if is_templates
            else [
                "Policy",
                "Memorandum",
                "Procedure",
                "Guidelines",
                "Manual",
                "Circular",
                "Other",
            ]
        )
        uploaded_document = st.file_uploader(
            "Select Excel, Word or PDF file",
            type=["xlsx", "xls", "docx", "doc", "pdf"],
            key=f"document_upload_{collection}",
        )
        left, right = st.columns(2)
        with left:
            document_title = st.text_input(
                "Document Title",
                key=f"document_title_{collection}",
                placeholder="Example: Revolving Fund Count Sheet",
            )
            document_category = st.selectbox(
                "Category",
                categories,
                key=f"document_category_{collection}",
            )
        with right:
            version_label = st.text_input(
                "Version / Revision",
                key=f"document_version_{collection}",
                placeholder="Example: Rev. 02 or 2026 Edition",
            )
            use_effective_date = st.checkbox(
                "Include effective/issuance date",
                key=f"document_use_date_{collection}",
            )
            effective_date = (
                st.date_input(
                    "Effective / Issuance Date",
                    key=f"document_effective_date_{collection}",
                )
                if use_effective_date
                else None
            )
        description = st.text_area(
            "Description / Purpose",
            key=f"document_description_{collection}",
            placeholder="Briefly describe when this document should be used.",
        )
        if st.button(
            "Upload to Shared Library",
            type="primary",
            use_container_width=True,
            key=f"document_upload_button_{collection}",
        ):
            if uploaded_document is None:
                st.error("Select a file before uploading.")
            else:
                try:
                    uploader_name = str(
                        current_user.get("full_name")
                        or current_user.get("username")
                        or "IARS User"
                    )
                    record = upload_document(
                        client,
                        config,
                        collection=collection,
                        file_bytes=uploaded_document.getvalue(),
                        original_filename=uploaded_document.name,
                        title=document_title,
                        category=document_category,
                        description=description,
                        version_label=version_label,
                        effective_date=effective_date,
                        uploaded_by=uploader_name,
                    )
                    _invalidate_session_cache(f"iars_doc_library_records_{collection}_cache_v4_4_19")
                    st.success(f"{record.get('original_filename', uploaded_document.name)} was added to the shared library.")
                    st.rerun()
                except DuplicateDocumentError as exc:
                    st.warning(str(exc))
                except Exception as exc:
                    st.error(str(exc))

    st.divider()
    render_section_header(
        "Browse Documents",
        "Search and filter the shared library, then select a document to download.",
    )

    all_categories = sorted({str(r.get("category", "") or "General") for r in records}, key=str.casefold)
    all_extensions = sorted({str(r.get("file_extension", "") or "").upper() for r in records if r.get("file_extension")})
    f1, f2, f3, f4 = st.columns([2.2, 1, 1, 1])
    with f1:
        search_text = st.text_input(
            "Search",
            key=f"library_search_{collection}",
            placeholder="Title, filename, category, description or uploader",
        )
    with f2:
        category_filter = st.selectbox(
            "Category",
            ["All"] + all_categories,
            key=f"library_category_filter_{collection}",
        )
    with f3:
        extension_filter = st.selectbox(
            "File Type",
            ["All"] + all_extensions,
            key=f"library_extension_filter_{collection}",
        )
    with f4:
        uploaded_from = st.date_input(
            "Uploaded From",
            value=None,
            key=f"library_date_filter_{collection}",
        )

    filtered = filter_documents(
        records,
        search=search_text,
        category=category_filter,
        extension=extension_filter,
        start_date=uploaded_from if isinstance(uploaded_from, date) else None,
    )

    display_rows = []
    for record in filtered:
        display_rows.append(
            {
                "Title": record.get("title", ""),
                "Category": record.get("category", ""),
                "Type": str(record.get("file_extension", "")).upper(),
                "Version": record.get("version_label", ""),
                "Effective Date": record.get("effective_date", ""),
                "Uploaded By": record.get("uploaded_by", ""),
                "Date Uploaded": str(record.get("uploaded_at", ""))[:10],
                "Size": document_file_size(record.get("file_size")),
            }
        )

    st.caption(f"Showing {len(filtered)} of {len(records)} document(s).")
    if not display_rows:
        st.info("No documents match the current filters.")
        return

    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
    labels: list[str] = []
    record_by_label: dict[str, dict] = {}
    for index, record in enumerate(filtered, start=1):
        label = (
            f"{record.get('title') or record.get('original_filename')} | "
            f"{record.get('category', '')} | {str(record.get('file_extension', '')).upper()} | {index}"
        )
        labels.append(label)
        record_by_label[label] = record

    selected_label = st.selectbox(
        "Select document",
        labels,
        key=f"library_selected_{collection}",
    )
    selected_record = record_by_label[selected_label]
    action_1, action_2 = st.columns([1, 1])
    with action_1:
        if st.button(
            "Prepare Download",
            use_container_width=True,
            key=f"library_load_{collection}",
        ):
            try:
                data = download_document(
                    client,
                    config,
                    str(selected_record.get("storage_path", "")),
                )
                state_key = f"library_download_bytes_{collection}"
                st.session_state[state_key] = data
                st.session_state[f"library_download_id_{collection}"] = selected_record.get("id")
            except Exception as exc:
                st.error(str(exc))
    with action_2:
        st.caption(
            str(selected_record.get("description", "") or "No description provided.")
        )

    state_key = f"library_download_bytes_{collection}"
    if st.session_state.get(f"library_download_id_{collection}") == selected_record.get("id"):
        selected_bytes = st.session_state.get(state_key)
        if selected_bytes:
            st.download_button(
                "Download Selected Document",
                data=selected_bytes,
                file_name=str(selected_record.get("original_filename", "document")),
                mime=str(selected_record.get("mime_type", "application/octet-stream")),
                use_container_width=True,
                key=f"library_download_button_{collection}",
            )
            if str(selected_record.get("file_extension", "")).lower() == "pdf":
                try:
                    preview_image, _, _ = render_pdf_page(selected_bytes, 0, zoom=1.15)
                    if preview_image is not None:
                        st.image(preview_image, caption="PDF first-page preview", use_container_width=True)
                except Exception:
                    pass

    if admin:
        with st.expander("Delete Selected Document — Administrator Only", expanded=False):
            st.warning("Deletion permanently removes both the file and its library record.")
            confirmation = st.text_input(
                "Type DELETE to confirm",
                key=f"library_delete_confirm_{collection}_{selected_record.get('id')}",
            )
            if st.button(
                "Delete Document",
                disabled=confirmation.strip().upper() != "DELETE",
                key=f"library_delete_button_{collection}_{selected_record.get('id')}",
            ):
                try:
                    delete_document(client, config, selected_record)
                    _invalidate_session_cache(f"iars_doc_library_records_{collection}_cache_v4_4_19")
                    st.session_state.pop(state_key, None)
                    st.session_state.pop(f"library_download_id_{collection}", None)
                    st.success("Document deleted successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))



def _session_ttl_cache(key: str, ttl_seconds: int, loader):
    """Small session cache for remote Supabase list calls.

    It keeps normal page changes responsive while still refreshing shared data
    automatically after a short period.
    """
    now = time.time()
    cached = st.session_state.get(key)
    if isinstance(cached, dict):
        ts = float(cached.get("ts", 0) or 0)
        if now - ts < ttl_seconds and "value" in cached:
            return cached.get("value")
    value = loader()
    st.session_state[key] = {"ts": now, "value": value}
    return value


def _invalidate_session_cache(*keys: str) -> None:
    for key in keys:
        st.session_state.pop(key, None)


archive_config = read_archive_config(st.secrets)
archive_client = archive_client_or_none(archive_config)
archive_ready = archive_is_configured(archive_config) and archive_client is not None
archive_unlocked = archive_ready  # All authenticated IARS users may access the shared archive.

document_config = read_document_library_config(st.secrets)
document_client = document_library_client_or_none(document_config)
document_library_ready = (
    document_library_is_configured(document_config) and document_client is not None
)

weekly_itinerary_config = WeeklyItineraryConfig()
weekly_itinerary_ready = archive_ready and archive_client is not None

if MASTER_DATA_PATH.exists():
    master_df, master_sheets = load_master_data(str(MASTER_DATA_PATH))
else:
    master_df, master_sheets = pd.DataFrame(), {}

auditors_df = master_sheets.get("Auditors", pd.DataFrame())
employee_records = get_employee_records(master_df)
employee_options = sorted({record["name"] for record in employee_records}, key=str.casefold)

# Dropdown labels come directly from Master Data. Findings show category only;
# Score remains in the separate Score output column.
finding_options = master_finding_options(master_sheets)
response_options = master_response_options(master_sheets)
frequency_options = master_frequency_options(master_sheets)

additional_auditor_rows = []
additional_auditor_error = ""
if archive_ready and archive_client is not None:
    try:
        additional_auditor_rows = _session_ttl_cache(
            "iars_additional_auditors_cache_v4_4_19",
            90,
            lambda: list_additional_auditors(archive_client, active_only=False),
        )
    except Exception as exc:
        additional_auditor_error = str(exc)

auditor_options = build_auditor_options(auditors_df, additional_auditor_rows)
if not auditor_options:
    auditor_options = sorted({_clean_option(name) for name in AUDITORS if _clean_option(name)}, key=str.casefold)


def _clear_avatar_dialog_state_on_navigation() -> None:
    for key in [
        "iars_avatar_view_dialog_open",
        "iars_avatar_edit_dialog_open",
        "iars_avatar_dialog_mode",
        "profile_picture_pending_upload_signature",
        "profile_picture_pending_preview_bytes",
    ]:
        st.session_state.pop(key, None)

nav_options = [
    "🏠 Dashboard",
    "🗓️ Weekly Itinerary",
    "📄 Generate Extraction",
    "🏷️ PDF Tagging",
    "🗂️ Shared PDF Archive",
    "📚 Audit Workpapers",
    "📜 Policies & Memoranda",
]
audit_report_nav = [
    "📄 Generate Extraction",
    "🏷️ PDF Tagging",
    "🗂️ Shared PDF Archive",
]
standalone_nav = [
    "🏠 Dashboard",
    "🗓️ Weekly Itinerary",
    "📚 Audit Workpapers",
    "📜 Policies & Memoranda",
]
if is_admin_user(auth_user):
    nav_options.extend([
        "👥 User Management",
        "🗃️ Master Data",
    ])
    standalone_nav.extend([
        "👥 User Management",
        "🗃️ Master Data",
    ])
nav_options.append("⚙️ Settings")
standalone_nav.append("⚙️ Settings")
if st.session_state.get("main_navigation") not in nav_options:
    st.session_state["main_navigation"] = nav_options[0]

with st.sidebar:
    render_sidebar_brand()
    selected_page = st.session_state["main_navigation"]

    dashboard_label = "🏠 Dashboard"
    dashboard_selected = selected_page == dashboard_label
    if st.button(
        dashboard_label,
        key="sidebar_nav_dashboard",
        use_container_width=True,
        type="primary" if dashboard_selected else "secondary",
    ):
        _clear_avatar_dialog_state_on_navigation()
        st.session_state["main_navigation"] = dashboard_label

    audit_expanded = selected_page in audit_report_nav
    with st.expander("📂 Audit Report", expanded=audit_expanded):
        for audit_index, nav_label in enumerate(audit_report_nav):
            nav_key = re.sub(r"[^a-z0-9]+", "_", nav_label.lower()).strip("_")
            is_selected = nav_label == selected_page
            if st.button(
                nav_label,
                key=f"audit_nav_{audit_index}_{nav_key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                _clear_avatar_dialog_state_on_navigation()
                st.session_state["main_navigation"] = nav_label

    remaining_nav = [label for label in standalone_nav if label != dashboard_label]
    for nav_index, nav_label in enumerate(remaining_nav):
        nav_key = re.sub(r"[^a-z0-9]+", "_", nav_label.lower()).strip("_")
        is_selected = nav_label == selected_page
        if st.button(
            nav_label,
            key=f"sidebar_nav_{nav_index}_{nav_key}",
            use_container_width=True,
            type="primary" if is_selected else "secondary",
        ):
            _clear_avatar_dialog_state_on_navigation()
            st.session_state["main_navigation"] = nav_label

    st.divider()
    system_ok = archive_ready and document_library_ready and MASTER_DATA_PATH.exists()
    render_sidebar_status(
        "System operational" if system_ok else "Setup requires review",
        "Archive, libraries and Master Data are ready." if system_ok else "Open Dashboard or Settings for details.",
        ok=system_ok,
    )

selected_page = st.session_state["main_navigation"]
page_key = selected_page.split(" ", 1)[1] if " " in selected_page else selected_page
render_app_header(auth_user, version="4.4.76", page_title=page_key)
render_profile_menu(auth_client, auth_user, auth_config)



if page_key == "Dashboard":
    st.markdown('<span class="iars-dashboard-v4475-marker"></span>', unsafe_allow_html=True)
    display_name = str(auth_user.get("full_name") or auth_user.get("username") or "Auditor")
    role_label = "Administrator" if is_admin_user(auth_user) else "Auditor"

    home_archive_records = []
    home_archive_error = ""
    if archive_ready and archive_client is not None:
        try:
            home_archive_records = _session_ttl_cache(
                "iars_home_archive_records_cache_v4_4_19",
                75,
                lambda: list_archive_records(archive_client, archive_config, limit=200),
            )
        except Exception as exc:
            home_archive_error = str(exc)

    home_template_records = []
    home_policy_records = []
    home_library_error = ""
    if document_library_ready and document_client is not None:
        try:
            home_template_records = _session_ttl_cache(
                "iars_home_template_records_cache_v4_4_19",
                75,
                lambda: list_documents(
                    document_client, document_config, collection=COLLECTION_TEMPLATES, limit=200
                ),
            )
            home_policy_records = _session_ttl_cache(
                "iars_home_policy_records_cache_v4_4_19",
                75,
                lambda: list_documents(
                    document_client, document_config, collection=COLLECTION_POLICIES, limit=200
                ),
            )
        except Exception as exc:
            home_library_error = str(exc)

    st.markdown(
        '<div class="edl-section-head iars-dashboard-welcome"><div>'
        f'<h2>Welcome back, {html.escape(display_name)}!</h2>'
        '<p>Here is what is happening across the Internal Audit Report System.</p>'
        f'</div><div class="edl-section-badge">{html.escape(role_label)}</div></div>',
        unsafe_allow_html=True,
    )
    render_metric_cards(
        [
            {"label": "Employees", "value": f"{len(master_df):,}", "note": "Master Data records", "icon": "👥", "accent": "#175CD3"},
            {"label": "Active Auditors", "value": f"{len(auditor_options):,}", "note": "Approved users", "icon": "🧑‍💼", "accent": "#148A4B"},
            {"label": "Archived PDFs", "value": f"{len(home_archive_records):,}" if archive_ready else "Offline", "note": "Shared archive", "icon": "🗂️", "accent": "#6938EF"},
            {"label": "Audit Workpapers", "value": f"{len(home_template_records):,}" if document_library_ready else "Setup", "note": "Reusable resources", "icon": "📚", "accent": "#C88A08"},
            {"label": "Policies & Memos", "value": f"{len(home_policy_records):,}" if document_library_ready else "Setup", "note": "Controlled references", "icon": "📜", "accent": "#087E8B"},
        ]
    )

    itinerary_col, activity_col = st.columns([1.45, 1.0], gap="large")

    # Left: the approved itinerary is immediately visible and occupies the main
    # Dashboard workspace. Right: recent archive activity remains easy to scan.
    with itinerary_col:
        render_dashboard_weekly_itinerary(
            client=archive_client,
            current_user=auth_user,
            admin=is_admin_user(auth_user),
            ready=weekly_itinerary_ready,
            config=weekly_itinerary_config,
        )

    with activity_col:
        with st.container(border=True):
            render_section_header(
                "Recent Archive Activity",
                "Latest reports saved by authorized auditors.",
            )
            activity_rows = []
            for record in home_archive_records[:7]:
                activity_rows.append(
                    {
                        "icon": "📄",
                        "title": str(record.get("original_filename", "") or "Archived PDF"),
                        "subtitle": f"{record.get('audit_reference', '') or 'No reference'} · Uploaded by {record.get('uploaded_by', '') or 'Unknown'}",
                        "meta": str(record.get("uploaded_at", ""))[:16].replace("T", " "),
                    }
                )
            render_activity_list(activity_rows)
            if home_archive_error:
                st.warning(f"Archive activity could not be loaded: {home_archive_error}")
            if home_library_error:
                st.warning(f"Document-library activity could not be loaded: {home_library_error}")


if page_key == "Weekly Itinerary":
    render_section_header(
        "Weekly Itinerary",
        "Upload your weekly itinerary image for administrator approval and review your submission history.",
        badge="Private Auditor Submission",
    )
    render_weekly_itinerary_page(
        client=archive_client,
        current_user=auth_user,
        admin=is_admin_user(auth_user),
        ready=weekly_itinerary_ready,
        config=weekly_itinerary_config,
    )


if page_key == "PDF Tagging":
    render_stepper(["Upload PDF", "Add & Position Tags", "Review", "Generate / Archive"], active_index=0)
    st.caption(
        "Double-right-click the PDF to add a textbox. Click inside to type, "
        "drag the move tab to reposition, and drag the blue handles to resize. "
        "Use Font size for the exact text size. Changes save automatically after you pause or move to another control."
    )

    tag_pdf = st.file_uploader(
        "Upload PDF to tag",
        type=["pdf"],
        key="tag_pdf_upload",
    )

    if tag_pdf is not None:
        pdf_bytes = tag_pdf.getvalue()
        file_id = editor_file_id(tag_pdf.name, pdf_bytes)

        try:
            import fitz

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = len(doc)
        except Exception as exc:
            st.error(f"Unable to open PDF: {exc}")
            page_count = 0

        if page_count:
            reset_key = f"pdf_editor_reset_{file_id}"
            reset_version = int(st.session_state.get(reset_key, 0))
            component_key = f"iars_pdf_editor_{file_id}_v29_reset_{reset_version}"
            storage_key = f"iars_pdf_editor_{file_id}_v26_reset_{reset_version}"

            controls_left, controls_right = st.columns([1, 2])
            with controls_left:
                preview_page = st.number_input(
                    "Page to tag",
                    min_value=1,
                    max_value=page_count,
                    value=1,
                    step=1,
                    key=f"editor_page_{file_id}",
                )
            with controls_right:
                st.info(
                    "The first right-click marks the location. Right-click the same spot again "
                    "to create a textbox. Font size remains exact; use Fit text when you want the box to match the label. "
                    "Edits save automatically without a manual save button."
                )

            preview_img, page_width, page_height = render_pdf_page(
                pdf_bytes,
                int(preview_page) - 1,
                zoom=1.7,
            )

            if preview_img is None:
                st.error("Unable to render this PDF page.")
                current_editor = component_editor_value(st.session_state.get(component_key))
            else:
                editor_result = pdf_textbox_editor(
                    image_data=image_to_data_uri(preview_img),
                    page_number=int(preview_page),
                    storage_key=storage_key,
                    key=component_key,
                    height=940,
                )

                current_editor = component_editor_value(editor_result)
                pages = current_editor.get("pages", {})
                boxes = pages.get(str(int(preview_page)), []) if isinstance(pages, dict) else []
                nonempty_boxes = [box for box in boxes if str(box.get("text", "")).strip()]
                st.caption(
                    f"Page {int(preview_page)}: {len(boxes)} textbox(es), "
                    f"{len(nonempty_boxes)} containing text."
                )

            if not current_editor.get("pages"):
                current_editor = component_editor_value(st.session_state.get(component_key))
            all_pages = current_editor.get("pages", {}) if isinstance(current_editor, dict) else {}

            all_tag_rows = []
            if isinstance(all_pages, dict):
                for page_number_text, page_boxes in all_pages.items():
                    try:
                        page_number = int(page_number_text)
                    except (TypeError, ValueError):
                        continue
                    if page_number < 1 or page_number > page_count or not isinstance(page_boxes, list):
                        continue
                    for box in page_boxes:
                        label_text = " ".join(str(box.get("text", "") or "").split())
                        if not label_text:
                            continue
                        all_tag_rows.append(
                            {
                                "Page": page_number,
                                "Label Text": label_text,
                                "X %": float(box.get("x_pct", 0)),
                                "Y %": float(box.get("y_pct", 0)),
                                "Width %": float(box.get("w_pct", 30)),
                                "Height %": float(box.get("h_pct", 6)),
                                "Font Size": float(box.get("font_size", 11)),
                                "Style": str(box.get("style", "Box")),
                            }
                        )

            all_tag_rows.sort(key=lambda row: (row["Page"], row["Y %"], row["X %"]))

            if all_tag_rows:
                with st.expander(f"Review saved textbox data ({len(all_tag_rows)})"):
                    st.dataframe(pd.DataFrame(all_tag_rows), use_container_width=True, hide_index=True)
            else:
                st.info("No completed textbox tags yet. You may proceed without tags or add them in the editor.")

            action_left, action_middle, action_right = st.columns([1, 1, 1])
            with action_left:
                if st.button("Generate Tagged PDF", type="primary", disabled=not all_tag_rows):
                    try:
                        tagged_bytes = stamp_pdf_with_tags(pdf_bytes, all_tag_rows)
                        st.session_state[f"tagged_pdf_{file_id}"] = tagged_bytes
                        st.success("Tagged PDF generated successfully.")
                    except Exception as exc:
                        st.error(f"Unable to generate tagged PDF: {exc}")

            with action_middle:
                tagged_pdf = st.session_state.get(f"tagged_pdf_{file_id}")
                if tagged_pdf:
                    st.download_button(
                        "Download Tagged PDF",
                        data=tagged_pdf,
                        file_name=f"tagged_{tag_pdf.name}",
                        mime="application/pdf",
                    )

            with action_right:
                if st.button("Clear All PDF Tags"):
                    st.session_state[reset_key] = reset_version + 1
                    st.session_state.pop(component_key, None)
                    st.session_state.pop(f"tagged_pdf_{file_id}", None)
                    st.rerun()

            with st.expander("Save original/tagged PDF to permanent archive"):
                if not archive_ready:
                    render_archive_setup_notice()
                elif not archive_unlocked:
                    st.info("Unlock the archive in the Saved PDFs tab before saving files.")
                else:
                    archive_defaults = cached_archive_metadata(pdf_bytes, tag_pdf.name)
                    ar_ref = st.text_input(
                        "Audit Reference",
                        value=archive_defaults.get("audit_reference", ""),
                        key=f"tag_archive_ref_{file_id}",
                    )
                    tag_default_auditees = resolve_auditee_defaults(
                        archive_defaults.get("auditee_name", ""), employee_records
                    )
                    ar_names = render_auditee_selector(
                        "Auditee Name(s) — Master Data Employees",
                        f"tag_archive_name_{file_id}",
                        employee_options,
                        tag_default_auditees,
                    )
                    ar_name = "; ".join(ar_names)
                    ar_by = render_auditor_selector(
                        "Uploaded By",
                        f"tag_archive_by_{file_id}",
                        auditor_options,
                    )
                    ar_versions = st.multiselect(
                        "PDF version to archive",
                        ["Original", "Tagged"],
                        default=["Original"] + (["Tagged"] if st.session_state.get(f"tagged_pdf_{file_id}") else []),
                        key=f"tag_archive_versions_{file_id}",
                    )
                    if st.button("Save Selected PDF Version(s)", key=f"tag_archive_save_{file_id}"):
                        if not ar_by.strip():
                            st.error("Uploaded By is required.")
                        elif not ar_versions:
                            st.error("Select at least one PDF version.")
                        else:
                            archive_results = []
                            if "Original" in ar_versions:
                                archive_results.append(
                                    archive_pdf_with_feedback(
                                        archive_client,
                                        archive_config,
                                        pdf_bytes=pdf_bytes,
                                        filename=tag_pdf.name,
                                        audit_reference=ar_ref,
                                        auditee_name=ar_name,
                                        document_type="Original",
                                        uploaded_by=ar_by,
                                    )
                                )
                            if "Tagged" in ar_versions:
                                tagged_data = st.session_state.get(f"tagged_pdf_{file_id}")
                                if tagged_data:
                                    archive_results.append(
                                        archive_pdf_with_feedback(
                                            archive_client,
                                            archive_config,
                                            pdf_bytes=tagged_data,
                                            filename=f"tagged_{tag_pdf.name}",
                                            audit_reference=ar_ref,
                                            auditee_name=ar_name,
                                            document_type="Tagged",
                                            uploaded_by=ar_by,
                                        )
                                    )
                                else:
                                    archive_results.append({"Status": "Skipped", "File": f"tagged_{tag_pdf.name}", "Details": "Generate the tagged PDF first."})
                            st.dataframe(pd.DataFrame(archive_results), use_container_width=True, hide_index=True)
    else:
        st.info("Upload a PDF only when tags are needed. Otherwise, use Generate Extraction directly.")


if page_key == "Shared PDF Archive":
    render_library_note(
        "Controlled shared access",
        "All signed-in auditors may view and download archived PDFs. Files are compressed automatically; deletion remains administrator-only.",
        icon="🗂️",
    )

    if not archive_ready:
        render_archive_setup_notice()
    else:
        archive_client = archive_client_or_none(archive_config)
        if archive_client is None:
            st.error("Unable to connect to Supabase. Verify the URL and service-role key in Streamlit Secrets.")
        else:
            if is_admin_user(auth_user):
                st.markdown("### Auditor Directory")
                with st.expander("Add New Auditor", expanded=False):
                    if additional_auditor_error:
                        st.warning(
                            "The additional-auditor table is not ready. Run "
                            "SUPABASE_AUDITOR_MIGRATION.sql in Supabase, then refresh the app."
                        )
                    with st.form("add_new_auditor_form", clear_on_submit=True):
                        new_auditor_name = st.text_input("Auditor Full Name")
                        new_auditor_designation = st.text_input("Designation")
                        new_auditor_user = st.text_input("User / Display Name")
                        new_auditor_email = st.text_input("Email (optional)")
                        new_auditor_status = st.selectbox("Status", ["Active", "Inactive"])
                        add_auditor_submit = st.form_submit_button("Add New Auditor", type="primary")

                    if add_auditor_submit:
                        try:
                            add_additional_auditor(
                                archive_client,
                                auditor_name=new_auditor_name,
                                designation=new_auditor_designation,
                                user_display=new_auditor_user,
                                email=new_auditor_email,
                                status=new_auditor_status,
                                created_by="IARS Archive Admin",
                            )
                            _invalidate_session_cache("iars_additional_auditors_cache_v4_4_19")
                            st.success("New auditor added successfully and is now available in the dropdown.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

            st.markdown("### Upload PDFs Directly to Archive")
            st.caption("This is available to all signed-in auditors. Uploaded PDFs become visible in the shared archive.")
            saved_uploads = st.file_uploader(
                "Select one or multiple PDF files",
                type=["pdf"],
                accept_multiple_files=True,
                key="archive_direct_upload",
            )
            direct_uploaded_by = render_auditor_selector(
                "Uploaded By",
                "archive_direct_uploaded_by",
                auditor_options,
            )

            prepared_entries = []
            if saved_uploads:
                for index, uploaded in enumerate(saved_uploads):
                    data = uploaded.getvalue()
                    defaults = cached_archive_metadata(data, uploaded.name)
                    with st.expander(uploaded.name, expanded=len(saved_uploads) == 1):
                        ref = st.text_input(
                            "Audit Reference",
                            value=defaults.get("audit_reference", ""),
                            key=f"archive_ref_{index}_{uploaded.name}",
                        )
                        default_auditees = resolve_auditee_defaults(
                            defaults.get("auditee_name", ""), employee_records
                        )
                        selected_auditees = render_auditee_selector(
                            "Auditee Name(s) — Master Data Employees",
                            f"archive_auditee_{index}_{uploaded.name}",
                            employee_options,
                            default_auditees,
                        )
                        auditee = "; ".join(selected_auditees)
                        doc_type = st.selectbox(
                            "Document Type",
                            ["Original", "Tagged"],
                            key=f"archive_type_{index}_{uploaded.name}",
                        )
                    prepared_entries.append((uploaded.name, data, ref, auditee, doc_type))

                if st.button("Archive Selected PDFs", type="primary"):
                    if not direct_uploaded_by.strip():
                        st.error("Uploaded By is required.")
                    else:
                        results = []
                        for filename, data, ref, auditee, doc_type in prepared_entries:
                            results.append(
                                archive_pdf_with_feedback(
                                    archive_client,
                                    archive_config,
                                    pdf_bytes=data,
                                    filename=filename,
                                    audit_reference=ref,
                                    auditee_name=auditee,
                                    document_type=doc_type,
                                    uploaded_by=direct_uploaded_by,
                                )
                            )
                        _invalidate_session_cache("iars_archive_records_cache_v4_4_19")
                        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

            st.divider()
            title_col, refresh_col = st.columns([4, 1])
            with title_col:
                st.markdown("### Shared Archived PDF Records")
            with refresh_col:
                if st.button("Refresh List"):
                    st.session_state.pop("archive_preview_bytes", None)
                    _invalidate_session_cache("iars_archive_records_cache_v4_4_19")
                    st.rerun()

            try:
                records = _session_ttl_cache(
                    "iars_archive_records_cache_v4_4_19",
                    180,
                    lambda: list_archive_records(archive_client, archive_config),
                )
            except Exception as exc:
                st.error(f"Unable to load archive records: {exc}")
                records = []

            total_archive_bytes = sum(int(record.get("file_size") or 0) for record in records)
            archive_uploaders = {str(record.get("uploaded_by", "") or "").strip() for record in records if str(record.get("uploaded_by", "") or "").strip()}
            tagged_count = sum(str(record.get("document_type", "") or "").strip().casefold() == "tagged" for record in records)
            render_metric_cards(
                [
                    {"label": "Total Files", "value": f"{len(records):,}", "note": "Shared audit PDFs", "icon": "📄", "accent": "#175CD3"},
                    {"label": "Total Size", "value": human_file_size(total_archive_bytes), "note": "Compressed storage", "icon": "💾", "accent": "#C88A08"},
                    {"label": "Uploaded By", "value": f"{len(archive_uploaders):,}", "note": "Contributing auditors", "icon": "👥", "accent": "#148A4B"},
                    {"label": "Tagged PDFs", "value": f"{tagged_count:,}", "note": "Tagged document versions", "icon": "🏷️", "accent": "#6938EF"},
                ]
            )

            if not records:
                st.info("No PDFs have been archived yet.")
            else:
                filter_1, filter_2, filter_3, filter_4 = st.columns([2, 1, 1, 1])
                with filter_1:
                    search_text = st.text_input(
                        "Search",
                        placeholder="Audit reference, auditee, filename or uploader",
                        key="archive_search",
                    )
                with filter_2:
                    type_filter = st.selectbox("Document Type", ["All", "Original", "Tagged"], key="archive_type_filter")
                with filter_3:
                    start_filter = st.date_input("Uploaded From", value=None, key="archive_start_date")
                with filter_4:
                    end_filter = st.date_input("Uploaded To", value=None, key="archive_end_date")

                filtered = filter_archive_records(
                    records,
                    search=search_text,
                    document_type=type_filter,
                    start_date=start_filter if isinstance(start_filter, date) else None,
                    end_date=end_filter if isinstance(end_filter, date) else None,
                )

                display_rows = []
                for record in filtered:
                    display_rows.append(
                        {
                            "Audit Reference": record.get("audit_reference", ""),
                            "Auditee Name": record.get("auditee_name", ""),
                            "Filename": record.get("original_filename", ""),
                            "Type": record.get("document_type", ""),
                            "Uploaded Date": str(record.get("uploaded_at", ""))[:10],
                            "Uploaded By": record.get("uploaded_by", ""),
                            "File Size": human_file_size(record.get("file_size")),
                        }
                    )

                st.caption(f"Showing {len(filtered)} of {len(records)} archived PDF record(s) from all auditors.")
                if display_rows:
                    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)

                    labels = []
                    record_by_label = {}
                    for idx, record in enumerate(filtered, start=1):
                        label = (
                            f"{record.get('audit_reference') or 'No Ref'} | "
                            f"{record.get('auditee_name') or 'No Auditee'} | "
                            f"{record.get('document_type', '')} | "
                            f"{record.get('original_filename', '')} | {idx}"
                        )
                        labels.append(label)
                        record_by_label[label] = record

                    selected_label = st.selectbox("Select a PDF to preview or download", labels)
                    selected_record = record_by_label[selected_label]

                    if st.button("Load Selected PDF"):
                        try:
                            selected_bytes = download_archived_pdf(
                                archive_client,
                                archive_config,
                                selected_record.get("storage_path", ""),
                            )
                            st.session_state["archive_preview_bytes"] = selected_bytes
                            st.session_state["archive_preview_record_id"] = selected_record.get("id")
                        except Exception as exc:
                            st.error(str(exc))

                    selected_bytes = None
                    if st.session_state.get("archive_preview_record_id") == selected_record.get("id"):
                        selected_bytes = st.session_state.get("archive_preview_bytes")

                    if selected_bytes:
                        st.download_button(
                            "Download Selected PDF",
                            data=selected_bytes,
                            file_name=selected_record.get("original_filename", "archived.pdf"),
                            mime="application/pdf",
                        )
                        try:
                            import fitz

                            archive_doc = fitz.open(stream=selected_bytes, filetype="pdf")
                            preview_page = st.number_input(
                                "Preview Page",
                                min_value=1,
                                max_value=len(archive_doc),
                                value=1,
                                step=1,
                                key=f"archive_preview_page_{selected_record.get('id')}",
                            )
                            preview_image, _, _ = render_pdf_page(selected_bytes, int(preview_page) - 1, zoom=1.35)
                            if preview_image is not None:
                                st.image(preview_image, caption=f"Page {preview_page}", use_container_width=True)
                        except Exception as exc:
                            st.warning(f"PDF preview unavailable: {exc}")

                    if is_admin_user(auth_user):
                        st.markdown("#### Delete Selected PDF — Administrator Only")
                        st.warning("Deleting removes both the private Storage object and its archive metadata.")
                        confirmation = st.text_input(
                            "Type DELETE to confirm",
                            key=f"delete_confirm_{selected_record.get('id')}",
                        )
                        if st.button(
                            "Delete Selected PDF",
                            type="primary",
                            disabled=confirmation.strip().upper() != "DELETE",
                        ):
                            try:
                                delete_archived_pdf(archive_client, archive_config, selected_record)
                                _invalidate_session_cache("iars_archive_records_cache_v4_4_19", "iars_archive_duplicate_check_cache_v4_4_19")
                                st.session_state.pop("archive_preview_bytes", None)
                                st.session_state.pop("archive_preview_record_id", None)
                                st.success("Archived PDF deleted successfully.")
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))
                    else:
                        st.caption("Only the administrator can delete archived PDFs.")
                else:
                    st.info("No archived PDFs match the selected filters.")


if page_key == "Generate Extraction":
    if master_df.empty:
        st.warning(
            "Master Data is required before generating extraction records. Ask the administrator to upload data/Master_Data.xlsx from the Master Data page."
        )
        st.markdown('<div class="iars-app-ready-marker"></div>', unsafe_allow_html=True)
        st.stop()
    render_stepper(["Upload PDFs", "Choose Action", "Process Reports", "Review & Export"], active_index=0)
    st.markdown("### Upload Audit Reports")
    st.caption("Drag and drop one or multiple searchable PDF reports.")
    pdf_files = st.file_uploader(
        "Upload one or multiple audit report PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="extract_pdf_upload",
    )

    if pdf_files:
        st.success(f"{len(pdf_files)} PDF report(s) uploaded successfully.")

        duplicate_matches: list[dict[str, str]] = []
        duplicate_metadata_warnings: list[str] = []
        duplicate_check_error = ""

        if archive_ready and archive_client is not None:
            try:
                # Always request the current Archive records when a report is
                # uploaded. The previous 180-second cache could hide a report
                # that had just been saved by this or another signed-in user.
                archive_records_for_check = list_archive_records(
                    archive_client,
                    archive_config,
                    limit=1000,
                )
                duplicate_matches, duplicate_metadata_warnings = (
                    uploaded_archive_duplicate_matches(
                        pdf_files,
                        archive_records_for_check,
                    )
                )
            except Exception as exc:
                duplicate_check_error = str(exc) or exc.__class__.__name__
        elif archive_is_configured(archive_config):
            duplicate_check_error = "The PDF Archive connection is currently unavailable."

        render_duplicate_archive_notice(
            duplicate_matches,
            duplicate_check_error,
            duplicate_metadata_warnings,
        )

        upload_action_options = ["Generate extraction only"]
        if archive_ready:
            upload_action_options.extend([
                "Generate extraction and archive original PDFs",
                "Archive original PDFs only",
            ])

        upload_action = st.radio(
            "Choose what to do with the uploaded PDFs",
            upload_action_options,
            horizontal=True,
            key="extract_upload_action",
        )
        archive_requested = upload_action != "Generate extraction only"
        archive_only = upload_action == "Archive original PDFs only"
        extraction_uploaded_by = ""

        if archive_requested:
            st.info(
                "The original PDFs will be compressed and saved in the shared archive, "
                "where all signed-in auditors can view them."
            )
            extraction_uploaded_by = render_auditor_selector(
                "Uploaded By",
                "extract_archive_uploaded_by",
                auditor_options,
            )
        elif not archive_ready:
            st.caption("Permanent archive is unavailable until Supabase is configured.")

        action_button_label = "Archive Uploaded PDFs" if archive_only else "Generate Extraction"
        if st.button(action_button_label, type="primary"):
            all_results = []
            processing_errors = []
            archive_results = []

            if archive_requested and not extraction_uploaded_by.strip():
                st.error("Uploaded By is required when saving PDFs to the archive.")
                st.markdown('<div class="iars-app-ready-marker"></div>', unsafe_allow_html=True)
                st.stop()

            progress = st.progress(0)
            status = st.empty()

            for idx, pdf_file in enumerate(pdf_files, start=1):
                pdf_data = pdf_file.getvalue()
                try:
                    status.write(f"Processing {idx} of {len(pdf_files)}: {pdf_file.name}")

                    if archive_only:
                        defaults = cached_archive_metadata(pdf_data, pdf_file.name)
                        official_names = official_auditee_string(
                            str(defaults.get("auditee_name", "") or ""),
                            employee_records,
                        )
                        archive_results.append(
                            archive_pdf_with_feedback(
                                archive_client,
                                archive_config,
                                pdf_bytes=pdf_data,
                                filename=pdf_file.name,
                                audit_reference=str(defaults.get("audit_reference", "") or ""),
                                auditee_name=official_names or str(defaults.get("auditee_name", "") or ""),
                                document_type="Original",
                                uploaded_by=extraction_uploaded_by,
                            )
                        )
                    else:
                        result_df, header, items = _build_records_isolated(
                            pdf_data,
                            pdf_file.name,
                            master_df,
                            auditors_df,
                            master_sheets,
                        )
                        all_results.append(result_df)

                        if archive_requested:
                            archive_results.append(
                                archive_pdf_with_feedback(
                                    archive_client,
                                    archive_config,
                                    pdf_bytes=pdf_data,
                                    filename=pdf_file.name,
                                    audit_reference=str(header.get("audit_reference", "") or ""),
                                    auditee_name=(
                                        canonical_names_from_result(result_df)
                                        or official_auditee_string(str(header.get("auditee_name", "") or ""), employee_records)
                                    ),
                                    document_type="Original",
                                    uploaded_by=extraction_uploaded_by,
                                )
                            )

                except Exception as e:
                    processing_errors.append({
                        "Source PDF": pdf_file.name,
                        "Error": str(e),
                    })

                progress.progress(idx / len(pdf_files))

            status.empty()

            if archive_only and archive_results:
                st.success(f"Processed {len(archive_results)} PDF file(s) for the shared archive.")

            if all_results:
                final_df = pd.concat(all_results, ignore_index=True)

                st.subheader("Generated Records")
                st.caption(f"Generated {len(final_df)} finding row(s) from {len(all_results)} processed PDF file(s).")

                edited_result = st.data_editor(
                    final_df,
                    use_container_width=True,
                    num_rows="fixed",
                    column_config={
                        "Findings": st.column_config.SelectboxColumn(
                            "Findings",
                            options=finding_options,
                        ),
                        "Audited By1": st.column_config.SelectboxColumn(
                            "Audited By1",
                            options=[""] + auditor_options,
                        ),
                        "Reaction": st.column_config.SelectboxColumn(
                            "Reaction",
                            options=response_options,
                        ),
                        "Frequency": st.column_config.SelectboxColumn(
                            "Frequency",
                            options=frequency_options,
                        ),
                    },
                )

                edited_result = normalize_output_with_master(
                    edited_result,
                    master_sheets=master_sheets,
                    auditors_df=auditors_df,
                )

                st.download_button(
                    "Download Consolidated Excel Output",
                    data=excel_bytes(edited_result),
                    file_name="audit_extraction_consolidated.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            if archive_results:
                _invalidate_session_cache(
                    "iars_archive_records_cache_v4_4_19",
                    "iars_archive_duplicate_check_cache_v4_4_19",
                )
                st.subheader("Archive Results")
                st.dataframe(pd.DataFrame(archive_results), use_container_width=True, hide_index=True)

            if processing_errors:
                st.warning("Some PDF files were not processed.")
                st.dataframe(pd.DataFrame(processing_errors), use_container_width=True)

    else:
        st.info("Upload one or multiple audit report PDFs to start.")


if page_key == "Audit Workpapers":
    render_document_library_page(
        collection=COLLECTION_TEMPLATES,
        client=document_client,
        config=document_config,
        ready=document_library_ready,
        current_user=auth_user,
        admin=is_admin_user(auth_user),
    )


if page_key == "Policies & Memoranda":
    render_document_library_page(
        collection=COLLECTION_POLICIES,
        client=document_client,
        config=document_config,
        ready=document_library_ready,
        current_user=auth_user,
        admin=is_admin_user(auth_user),
    )


if page_key == "User Management" and is_admin_user(auth_user):
    render_section_header(
        "User Management",
        "Approve registrations, issue activation or reset codes, and manage authorized IARS accounts.",
        badge="Administrator Only",
    )
    render_account_admin_page(auth_client, auth_config)


if page_key == "Master Data" and is_admin_user(auth_user):
    render_section_header(
        "Master Data Management",
        "Review the active reference workbook and upload a validated replacement without changing the IARS code.",
        badge="Administrator Only",
    )

    current_sheets = list(master_sheets.keys())
    active_auditors_count = 0
    if not auditors_df.empty and "Auditor" in auditors_df.columns:
        if "Status" in auditors_df.columns:
            active_auditors_count = int(
                auditors_df["Status"].astype(str).str.strip().str.casefold().isin(["active", ""]).sum()
            )
        else:
            active_auditors_count = len(auditors_df)

    render_metric_cards(
        [
            {"label": "Employees", "value": f"{len(master_df):,}", "note": "Current employee records", "icon": "👥", "accent": "#2563EB"},
            {"label": "Active Auditors", "value": f"{active_auditors_count:,}", "note": "Available in dropdowns", "icon": "🧑‍💼", "accent": "#178A52"},
            {"label": "Worksheets", "value": f"{len(current_sheets):,}", "note": "Reference tables", "icon": "📑", "accent": "#C78B12"},
            {"label": "Workbook Status", "value": "Ready" if MASTER_DATA_PATH.exists() else "Missing", "note": str(MASTER_DATA_PATH), "icon": "🗃️", "accent": "#178A52" if MASTER_DATA_PATH.exists() else "#D92D20"},
        ]
    )

    with st.container(border=True):
        st.markdown("### Upload Updated Master Data")
        st.caption(
            "The workbook is checked first. The existing active file is replaced only after the new workbook passes validation."
        )
        uploaded_master = st.file_uploader(
            "Select Master_Data.xlsx",
            type=["xlsx"],
            key="master_data_page_upload",
        )
        if uploaded_master is not None:
            validation_errors: list[str] = []
            validation_notes: list[str] = []
            try:
                workbook_bytes = uploaded_master.getvalue()
                test_xls = pd.ExcelFile(BytesIO(workbook_bytes))
                required_sheets = {"Employees", "Auditors"}
                missing_sheets = sorted(required_sheets - set(test_xls.sheet_names))
                if missing_sheets:
                    validation_errors.append(
                        "Missing required worksheet(s): " + ", ".join(missing_sheets)
                    )
                if "Employees" in test_xls.sheet_names:
                    test_employees = pd.read_excel(BytesIO(workbook_bytes), sheet_name="Employees")
                    name_column = next(
                        (name for name in ("Employee Name", "Full Name", "Name") if name in test_employees.columns),
                        None,
                    )
                    if "Employee ID" not in test_employees.columns:
                        validation_errors.append("Employees sheet is missing the Employee ID column.")
                    if not name_column:
                        validation_errors.append("Employees sheet is missing an employee-name column.")
                    validation_notes.append(f"Employees detected: {len(test_employees):,}")
                if "Auditors" in test_xls.sheet_names:
                    test_auditors = pd.read_excel(BytesIO(workbook_bytes), sheet_name="Auditors")
                    for required_column in ("Auditor", "User", "Status"):
                        if required_column not in test_auditors.columns:
                            validation_errors.append(
                                f"Auditors sheet is missing the {required_column} column."
                            )
                    validation_notes.append(f"Auditors detected: {len(test_auditors):,}")
                validation_notes.append(f"Worksheets detected: {len(test_xls.sheet_names):,}")
            except Exception as exc:
                validation_errors.append(f"Unable to read the workbook: {exc}")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                st.success("Workbook validation passed. " + " · ".join(validation_notes))
                if st.button(
                    "Activate Updated Master Data",
                    type="primary",
                    use_container_width=True,
                    key="activate_master_data",
                ):
                    save_uploaded_master(uploaded_master)
                    st.cache_data.clear()
                    st.success("Master Data updated successfully. The app will now reload it.")
                    st.rerun()

    if current_sheets:
        st.divider()
        render_section_header(
            "Current Workbook Preview",
            "Select a worksheet to review the active values currently used by IARS.",
        )
        selected_sheet = st.selectbox(
            "Worksheet",
            current_sheets,
            key="master_data_preview_sheet",
        )
        preview_df = master_sheets.get(selected_sheet, pd.DataFrame())
        if isinstance(preview_df, pd.DataFrame):
            st.dataframe(preview_df.head(200), use_container_width=True, hide_index=True)
            if len(preview_df) > 200:
                st.caption(f"Showing the first 200 of {len(preview_df):,} rows.")


if page_key == "Settings":
    render_section_header(
        "System Settings",
        "Review the active IARS environment, security and storage configuration.",
        badge="System Information",
    )
    render_metric_cards(
        [
            {"label": "IARS Version", "value": "4.4.76", "note": "Exact-Reference EDL Enterprise UI", "icon": "⚙️", "accent": "#C78B12"},
            {"label": "PDF Archive", "value": "Connected" if archive_ready else "Offline", "note": archive_config.bucket if archive_ready else "Check Secrets", "icon": "🗂️", "accent": "#178A52" if archive_ready else "#D92D20"},
            {"label": "Document Library", "value": "Connected" if document_library_ready else "Setup", "note": document_config.bucket, "icon": "📚", "accent": "#6941C6" if document_library_ready else "#D92D20"},
            {"label": "Session Timeout", "value": f"{auth_config.session_timeout_minutes} min", "note": "Automatic security timeout", "icon": "🔐", "accent": "#2563EB"},
        ]
    )

    general_tab, security_tab, storage_tab = st.tabs(
        ["General", "Security & Access", "Storage & Libraries"]
    )
    with general_tab:
        with st.container(border=True):
            st.markdown("### General Configuration")
            st.text_input("System Name", value="Internal Audit Report System", disabled=True)
            st.text_input("Organization", value="EDL GROUP OF COMPANIES", disabled=True)
            st.text_input("Environment", value="Production", disabled=True)
            st.text_input("Master Data Path", value=str(MASTER_DATA_PATH), disabled=True)
    with security_tab:
        with st.container(border=True):
            st.markdown("### Security Controls")
            st.checkbox("Administrator approval required for new accounts", value=True, disabled=True)
            st.checkbox("All users authenticate using username and password", value=True, disabled=True)
            st.checkbox("Automatic logout after inactivity", value=True, disabled=True)
            st.checkbox("Archive deletion restricted to administrator", value=True, disabled=True)
            st.checkbox("Master Data updates restricted to administrator", value=True, disabled=True)
            st.caption(
                "Administrator credentials and code secrets are maintained in Streamlit Secrets and are not displayed in the application."
            )
    with storage_tab:
        with st.container(border=True):
            st.markdown("### Storage Configuration")
            st.checkbox("Automatic PDF compression", value=True, disabled=True)
            st.checkbox("All signed-in auditors may view shared PDFs", value=True, disabled=True)
            st.checkbox("All signed-in auditors may download templates and policies", value=True, disabled=True)
            st.text_input("PDF Archive Bucket", value=archive_config.bucket, disabled=True)
            st.text_input("Document Library Bucket", value=document_config.bucket, disabled=True)
            if not document_library_ready:
                st.warning(
                    "Run SUPABASE_DOCUMENT_LIBRARY_SETUP.sql to enable Audit Workpapers and Policies & Memoranda."
                )

# Signals that the authenticated page has completed rendering. The login-exit
# mask remains fully opaque until this marker reaches the browser.
st.markdown('<div class="iars-app-ready-marker"></div>', unsafe_allow_html=True)
