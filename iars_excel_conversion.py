from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
import base64
from pathlib import Path
import hashlib
import re
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from openpyxl import load_workbook


WAREHOUSE_OUTPUT_HEADERS = [
    "id",
    "login_date",
    "sap_no",
    "sap_date",
    "locations",
    "stock_status",
    "task",
    "product",
    "uom",
    "record_qty",
    "count_qty",
    "remarks",
    "auditor_name",
]

WAREHOUSE_TEMPLATE_PATH = (
    Path(__file__).resolve().parent / "assets" / "warehouse_conversion_template.xlsx"
)
# Embedded approved template fallback. This keeps the module operational even when
# deployment tools copy Python files but omit the assets folder.
WAREHOUSE_TEMPLATE_XLSX_BASE64 = (
    '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'
)
PHILIPPINE_ZONE = ZoneInfo("Asia/Manila")


class WarehouseConversionError(ValueError):
    """Raised when an uploaded SAP workbook does not match the Warehouse format."""


@dataclass(frozen=True)
class WarehouseFilenameMetadata:
    source_stem: str
    location: str
    remarks: str
    company_code: str
    sap_no: str
    stock_status: str


@dataclass(frozen=True)
class WarehouseSourceRecord:
    item_no: str
    product: str
    uom: Any
    record_qty: Any


@dataclass(frozen=True)
class WarehouseConversionResult:
    output_bytes: bytes
    output_filename: str
    metadata: WarehouseFilenameMetadata
    process_date: date
    auditor_name: str
    records: tuple[WarehouseSourceRecord, ...]
    source_signature: str

    @property
    def row_count(self) -> int:
        return len(self.records)

    def preview_rows(self, limit: int = 200) -> list[dict[str, Any]]:
        shown = self.records[: max(0, int(limit))]
        return [
            {
                "login_date": self.process_date.isoformat(),
                "sap_no": self.metadata.sap_no,
                "sap_date": self.process_date.isoformat(),
                "locations": self.metadata.location,
                "stock_status": self.metadata.stock_status,
                "task": "Balance",
                "product": record.product,
                "uom": record.uom,
                "record_qty": record.record_qty,
                "count_qty": None,
                "remarks": self.metadata.remarks,
                "auditor_name": self.auditor_name,
            }
            for record in shown
        ]


def philippine_today() -> date:
    return datetime.now(PHILIPPINE_ZONE).date()


def _clean_uploaded_stem(filename: str) -> str:
    raw_name = Path(str(filename or "").strip()).name
    if not raw_name:
        raise WarehouseConversionError("The uploaded Excel filename is missing.")
    stem = Path(raw_name).stem
    # Browsers commonly append duplicate-download suffixes such as (1).
    stem = re.sub(r"\s*\(\d+\)\s*$", "", stem).strip()
    stem = re.sub(r"\s+", " ", stem)
    if not stem:
        raise WarehouseConversionError("The uploaded Excel filename is invalid.")
    return stem


def parse_warehouse_filename(
    filename: str,
    *,
    process_date: date | None = None,
) -> WarehouseFilenameMetadata:
    conversion_date = process_date or philippine_today()
    stem = _clean_uploaded_stem(filename)
    words = stem.split()
    if len(words) < 3:
        raise WarehouseConversionError(
            "Filename must follow the Warehouse pattern, for example: "
            "Cebu Damage Warehouse EPLSI.xlsx or Cebu Good Stocks EPLSI.xlsx."
        )

    location = words[0].strip()
    remarks_word = words[1].strip()
    company_code = words[-1].strip().upper()
    location_code = re.sub(r"[^A-Za-z0-9]", "", location)[:3].upper()

    if len(location_code) < 3:
        raise WarehouseConversionError(
            "The first filename word must contain at least three letters for sap_no."
        )
    if not company_code:
        raise WarehouseConversionError("The last filename word/company code is missing.")

    remarks_key = remarks_word.casefold()
    if remarks_key == "damage":
        remarks = "Damage"
        stock_suffix = "DW"
    elif remarks_key == "good":
        remarks = "Good"
        stock_suffix = "GS"
    else:
        raise WarehouseConversionError(
            "The second filename word must be either Damage or Good."
        )

    sap_no = f"{location_code}{conversion_date:%y%m%d}-{company_code}"
    stock_status = f"{company_code}-{stock_suffix}"
    return WarehouseFilenameMetadata(
        source_stem=stem,
        location=location,
        remarks=remarks,
        company_code=company_code,
        sap_no=sap_no,
        stock_status=stock_status,
    )


def _normalize_header(value: Any) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _remove_apostrophes(value: Any) -> str:
    text = "" if value is None else str(value)
    for apostrophe in ("'", "’", "‘", "ʼ", "`"):
        text = text.replace(apostrophe, "")
    return text.strip()


def _find_header_row_and_columns(worksheet: Any) -> tuple[int, dict[str, int]]:
    expected = {
        "item no": "item_no",
        "item description": "product",
        "inventory uom": "uom",
        "in stock": "record_qty",
    }
    max_scan_rows = min(max(worksheet.max_row, 1), 15)
    max_scan_cols = min(max(worksheet.max_column, 1), 30)

    for row_index in range(1, max_scan_rows + 1):
        found: dict[str, int] = {}
        for column_index in range(1, max_scan_cols + 1):
            normalized = _normalize_header(worksheet.cell(row_index, column_index).value)
            field_name = expected.get(normalized)
            if field_name:
                found[field_name] = column_index
        if set(found) == set(expected.values()):
            return row_index, found

    raise WarehouseConversionError(
        "Required SAP columns were not found: Item No., Item Description, "
        "Inventory UoM, and In Stock."
    )


def extract_warehouse_records(excel_bytes: bytes) -> tuple[WarehouseSourceRecord, ...]:
    if not excel_bytes:
        raise WarehouseConversionError("The uploaded SAP Excel file is empty.")

    try:
        workbook = load_workbook(BytesIO(excel_bytes), data_only=True, read_only=False)
    except Exception as exc:
        raise WarehouseConversionError(
            "The uploaded file could not be opened as a valid .xlsx workbook."
        ) from exc

    worksheet = workbook.active
    header_row, columns = _find_header_row_and_columns(worksheet)

    start_row: int | None = None
    for row_index in range(header_row + 1, worksheet.max_row + 1):
        item_no = worksheet.cell(row_index, columns["item_no"]).value
        if str(item_no or "").strip().upper() == "A01AMB01":
            start_row = row_index
            break

    if start_row is None:
        raise WarehouseConversionError(
            'Starting item "A01AMB01" was not found under the Item No. column.'
        )

    records: list[WarehouseSourceRecord] = []
    for row_index in range(start_row, worksheet.max_row + 1):
        item_no_value = worksheet.cell(row_index, columns["item_no"]).value
        product_value = worksheet.cell(row_index, columns["product"]).value
        uom_value = worksheet.cell(row_index, columns["uom"]).value
        quantity_value = worksheet.cell(row_index, columns["record_qty"]).value

        if all(value in (None, "") for value in (item_no_value, product_value, uom_value, quantity_value)):
            break

        item_no_text = str(item_no_value or "").strip()
        product_raw = "" if product_value is None else str(product_value).strip()
        total_marker = f"{item_no_text} {product_raw}".casefold()
        if "grand total" in total_marker or total_marker.strip() == "total" or item_no_text.casefold() == "total":
            break

        if not product_raw:
            raise WarehouseConversionError(
                f"Item Description is blank at source row {row_index}."
            )

        product = _remove_apostrophes(product_raw)
        uom = None if uom_value in (None, "") else uom_value
        records.append(
            WarehouseSourceRecord(
                item_no=item_no_text,
                product=product,
                uom=uom,
                record_qty=quantity_value,
            )
        )

    if not records:
        raise WarehouseConversionError("No Warehouse product rows were captured.")

    return tuple(records)


def _safe_output_filename(metadata: WarehouseFilenameMetadata, auditor_name: str) -> str:
    first_name = str(auditor_name or "Auditor").strip().split()[0] or "Auditor"
    raw = f"For Upload {metadata.company_code} {metadata.remarks} - {first_name}.xlsx"
    return re.sub(r'[<>:"/\\|?*]+', "_", raw)


def _load_template(template_path: Path | None = None):
    path = Path(template_path or WAREHOUSE_TEMPLATE_PATH)
    try:
        if path.exists():
            workbook = load_workbook(path)
        else:
            # Self-contained fallback: use the embedded approved workbook.
            template_bytes = base64.b64decode(WAREHOUSE_TEMPLATE_XLSX_BASE64)
            workbook = load_workbook(BytesIO(template_bytes))
    except Exception as exc:
        raise WarehouseConversionError(
            "The Warehouse conversion template could not be opened."
        ) from exc
    worksheet = workbook["For Uploading"] if "For Uploading" in workbook.sheetnames else workbook.active
    headers = [worksheet.cell(1, column).value for column in range(1, 14)]
    if headers != WAREHOUSE_OUTPUT_HEADERS:
        raise WarehouseConversionError(
            "The Warehouse conversion template headers do not match the approved format."
        )
    return workbook, worksheet


def _write_output_rows(
    worksheet: Any,
    records: Iterable[WarehouseSourceRecord],
    metadata: WarehouseFilenameMetadata,
    process_date: date,
    auditor_name: str,
) -> int:
    records = tuple(records)
    style_prototypes = [copy(worksheet.cell(2, column)._style) for column in range(1, 14)]
    alignment_prototypes = [copy(worksheet.cell(2, column).alignment) for column in range(1, 14)]
    protection_prototypes = [copy(worksheet.cell(2, column).protection) for column in range(1, 14)]

    clear_through = max(worksheet.max_row, len(records) + 1)
    for row_index in range(2, clear_through + 1):
        for column_index in range(1, 14):
            worksheet.cell(row_index, column_index).value = None

    excel_date = datetime.combine(process_date, datetime.min.time())
    for offset, record in enumerate(records, start=2):
        values = [
            None,
            excel_date,
            metadata.sap_no,
            excel_date,
            metadata.location,
            metadata.stock_status,
            "Balance",
            record.product,
            record.uom,
            record.record_qty,
            None,
            metadata.remarks,
            auditor_name,
        ]
        for column_index, value in enumerate(values, start=1):
            cell = worksheet.cell(offset, column_index)
            cell._style = copy(style_prototypes[column_index - 1])
            cell.alignment = copy(alignment_prototypes[column_index - 1])
            cell.protection = copy(protection_prototypes[column_index - 1])
            cell.value = value
            cell.number_format = "yyyy-mm-dd" if column_index in (2, 4) else "General"

    return len(records)


def build_warehouse_conversion(
    excel_bytes: bytes,
    filename: str,
    auditor_name: str,
    *,
    process_date: date | None = None,
    template_path: Path | None = None,
) -> WarehouseConversionResult:
    conversion_date = process_date or philippine_today()
    clean_auditor_name = str(auditor_name or "").strip()
    if not clean_auditor_name:
        raise WarehouseConversionError(
            "The signed-in user's full name is required for auditor_name."
        )

    metadata = parse_warehouse_filename(filename, process_date=conversion_date)
    records = extract_warehouse_records(excel_bytes)
    workbook, worksheet = _load_template(template_path)
    _write_output_rows(worksheet, records, metadata, conversion_date, clean_auditor_name)

    workbook.calculation.fullCalcOnLoad = True
    workbook.calculation.forceFullCalc = True
    buffer = BytesIO()
    workbook.save(buffer)
    output_bytes = buffer.getvalue()

    # Re-open the produced workbook as an integrity check before exposing it.
    try:
        verification_book = load_workbook(BytesIO(output_bytes), data_only=False, read_only=True)
        verification_sheet = verification_book["For Uploading"]
        if verification_sheet.max_row != len(records) + 1:
            raise WarehouseConversionError(
                "Converted row count did not match the captured SAP product count."
            )
    except WarehouseConversionError:
        raise
    except Exception as exc:
        raise WarehouseConversionError(
            "The converted Excel file failed the final workbook integrity check."
        ) from exc

    return WarehouseConversionResult(
        output_bytes=output_bytes,
        output_filename=_safe_output_filename(metadata, clean_auditor_name),
        metadata=metadata,
        process_date=conversion_date,
        auditor_name=clean_auditor_name,
        records=records,
        source_signature=hashlib.sha256(excel_bytes).hexdigest(),
    )


def render_warehouse_conversion_page(user: dict[str, Any]) -> None:
    import pandas as pd
    import streamlit as st

    st.markdown(
        """
        <style>
        .iars-excel-hero {
            border: 1px solid #DDE5EF;
            border-radius: 16px;
            padding: 1.05rem 1.15rem;
            margin: 0 0 .9rem 0;
            background: linear-gradient(135deg, #F8FAFD 0%, #FFFFFF 58%, #FFF9EB 100%);
            box-shadow: 0 8px 24px rgba(6,26,54,.06);
        }
        .iars-excel-hero h2 { margin: 0; color: #061A36; font-size: 1.35rem; }
        .iars-excel-hero p { margin: .28rem 0 0; color: #667085; font-size: .88rem; }
        .iars-excel-route {
            display: grid;
            grid-template-columns: 1fr auto 1fr auto 1fr;
            align-items: center;
            gap: .55rem;
            margin-top: .85rem;
        }
        .iars-excel-route div {
            min-height: 64px;
            border: 1px solid #E4EAF2;
            border-radius: 12px;
            padding: .65rem .72rem;
            background: rgba(255,255,255,.9);
        }
        .iars-excel-route strong { display:block; color:#061A36; font-size:.86rem; }
        .iars-excel-route span { color:#667085; font-size:.74rem; line-height:1.25; }
        .iars-excel-route b { color:#C78B12; font-size:1.1rem; }
        @media (max-width: 760px) {
            .iars-excel-route { grid-template-columns: 1fr; }
            .iars-excel-route b { display:none; }
        }
        </style>
        <div class="iars-excel-hero">
          <h2>Warehouse Excel Conversion</h2>
          <p>Convert an SAP Warehouse stock export into the approved upload template without changing the original file.</p>
          <div class="iars-excel-route">
            <div><strong>1. SAP Excel</strong><span>Upload the Warehouse stock file.</span></div>
            <b>→</b>
            <div><strong>2. IARS Conversion</strong><span>Validate, map and clean the required data.</span></div>
            <b>→</b>
            <div><strong>3. Compatible Output</strong><span>Download the approved 13-column template.</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("### Upload SAP Warehouse File")
        st.caption(
            "Accepted filename examples: Cebu Damage Warehouse EPLSI.xlsx or "
            "Cebu Good Stocks EPLSI.xlsx"
        )
        uploaded_file = st.file_uploader(
            "SAP Warehouse Excel",
            type=["xlsx"],
            key="warehouse_sap_excel_uploader_v4_5_12",
            help="The original SAP file remains unchanged.",
        )

    if uploaded_file is None:
        st.info(
            "Upload an SAP Warehouse .xlsx file. IARS will capture Item Description, "
            "Inventory UoM and In Stock beginning at item A01AMB01."
        )
        return

    auditor_name = str(
        user.get("full_name") or user.get("username") or ""
    ).strip()
    process_date = philippine_today()

    try:
        with st.spinner("Validating and converting the SAP Warehouse file…"):
            result = build_warehouse_conversion(
                uploaded_file.getvalue(),
                uploaded_file.name,
                auditor_name,
                process_date=process_date,
            )
    except WarehouseConversionError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"Warehouse conversion failed: {exc}")
        return

    metadata = result.metadata
    metric_columns = st.columns(4)
    metric_columns[0].metric("Products Captured", f"{result.row_count:,}")
    metric_columns[1].metric("SAP No.", metadata.sap_no)
    metric_columns[2].metric("Location", metadata.location)
    metric_columns[3].metric("Stock Status", metadata.stock_status)

    st.success(
        f"Conversion completed for {result.row_count:,} product rows. "
        "Apostrophes were removed and the output passed the workbook integrity check."
    )

    with st.expander("Conversion Details", expanded=True):
        details = pd.DataFrame(
            [
                ["Processing Date", result.process_date.isoformat()],
                ["Source Filename", uploaded_file.name],
                ["SAP No.", metadata.sap_no],
                ["Location", metadata.location],
                ["Remarks", metadata.remarks],
                ["Stock Status", metadata.stock_status],
                ["Task", "Balance"],
                ["Auditor Name", result.auditor_name],
            ],
            columns=["Field", "Generated Value"],
        )
        st.dataframe(details, hide_index=True, width="stretch")

    st.markdown("### Converted Data Preview")
    preview = pd.DataFrame(result.preview_rows(limit=200))
    st.dataframe(preview, hide_index=True, width="stretch", height=390)
    if result.row_count > len(preview):
        st.caption(f"Showing the first {len(preview):,} of {result.row_count:,} converted rows.")

    st.download_button(
        "⬇️ Download Converted Warehouse Excel",
        data=result.output_bytes,
        file_name=result.output_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"warehouse_download_{result.source_signature[:16]}",
        type="primary",
        width="stretch",
    )
    st.caption(
        "Output format: For Uploading sheet · 13 approved columns · dates in yyyy-mm-dd · "
        "count_qty and id remain blank."
    )
