# Internal Audit Report System (IARS) v3.1

## New archive controls

### Uploaded By
- Uses active auditors from `data/Master_Data.xlsx` → `Auditors`.
- Also includes active auditors added through Supabase `auditors_master`.
- Includes a Search button, Clear button, and searchable dropdown.
- `Add New Auditor` is available in the unlocked **Saved PDFs** tab.
- Newly added auditors are stored permanently in Supabase and remain available after app restarts.
- Duplicate auditor names are blocked case-insensitively.
- Inactive auditors are not shown in new Uploaded By selections.

### Auditee Name
- Uses only official employee names from `data/Master_Data.xlsx` → `Employees`.
- Supports the current workbook column `Full Name` and also accepts `Employee Name` if the column is renamed later.
- Uses a searchable multiselect for reports with one or multiple auditees.
- Detected PDF header names and aliases are mapped to the official Master Data employee name.
- Automatic archive-after-extraction uses the canonical `Name` values produced by the parser.

## One-time Supabase migration

The PDF archive is already configured, but the new Add New Auditor feature needs one additional table.

1. Open Supabase → SQL Editor → New query.
2. Copy and run all contents of `SUPABASE_AUDITOR_MIGRATION.sql`.
3. Reboot or refresh IARS.
4. Unlock **Saved PDFs** and open **Add New Auditor**.

The main `SUPABASE_SETUP.sql` was also updated for new Supabase projects.

## Repaired Master Data workbook

The uploaded `Master_Data(3).xlsx` was fully imported and re-exported as a clean `.xlsx` package. All 15 sheets and the key Employees, Auditors, and Classification Matrix contents were preserved. The cleaned workbook is included as:

`data/Master_Data.xlsx`

Replace the previous GitHub `data/Master_Data.xlsx` with the file included in this ZIP. Keep your original workbook as a backup until the clean version is confirmed in Excel.

## Existing features preserved
- Multiple PDF extraction and consolidated Excel output
- Blank `#` column
- `yyyy-mm-dd` Encoded Date and Date Reported
- PDF textbox editor with page persistence, typing, dragging, and resizing
- Frequency, auditee, explanation, PCV-detail, and issue-title rules
- Supabase private PDF archive, preview, search, download, and confirmed deletion
