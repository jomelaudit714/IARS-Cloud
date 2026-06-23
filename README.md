# Internal Audit Report System (IARS) v3.2


## Exact Master Data labels

- **Findings** now stores only the exact `Classification_Matrix → Category` value.
- The classification score is stored only in the separate **Score** column.
- **Reaction/Response** values use the exact spelling, capitalization, and internal spacing from `Response_Master → Response`.
- **Frequency** values use the exact spelling, capitalization, and internal spacing from `Frequency_Master → Frequency`.
- **Audited By1** and Uploaded By dropdown values preserve the exact auditor name from `Auditors → Auditor`.
- If a Findings category is changed in the generated-record editor, Score, Improve Score, Net Score, User, and canonical labels are refreshed from the current Master Data before download.

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

## Current Master Data workbook

The package includes the user's validated current workbook as `data/Master_Data.xlsx`. The workbook was copied without altering its data.

## Existing features preserved
- Multiple PDF extraction and consolidated Excel output
- Blank `#` column
- `yyyy-mm-dd` Encoded Date and Date Reported
- PDF textbox editor with page persistence, typing, dragging, and resizing
- Frequency, auditee, explanation, PCV-detail, and issue-title rules
- Supabase private PDF archive, preview, search, download, and confirmed deletion
