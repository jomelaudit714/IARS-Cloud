# IARS V4.4.69 Test Results

## Company-folder data layer

Passed in three consecutive runs:

- create a company folder
- reject the same folder name regardless of capitalization
- list active company folders
- upload a policy with its `folder_id`
- store the PDF under a company-specific Storage path
- preserve Audit Workpapers upload compatibility without a folder

## Application checks

- Python compilation: passed three consecutive runs
- Create Folder dialog is present
- Company-folder popup is present
- Policies & Memoranda routes to the folder-based view
- upload requires a selected company/group folder
- PDF page preview is present
- DOCX readable-text preview is present
- XLSX worksheet preview is present
- header and Settings version labels are both V4.4.69

## Database migration checks

- migration creates `document_library_folders`
- migration adds nullable `folder_id` to existing records
- foreign key uses `ON DELETE SET NULL`
- migration does not drop or truncate existing records
- existing documents remain visible under `Unfiled / General`

## Regression integrity

- `iars_parser.py` is unchanged from V4.4.68
- `iars_pdf_editor.py` is unchanged from V4.4.68
- requirements retain Streamlit 1.58.0 and PyArrow 24.0.0
- no authentication, archive, extraction-worker, theme, or Master Data file is included in the patch

A live Supabase transaction was not performed because the test environment does not have the user's Supabase credentials. The database functions were tested using a Supabase-compatible in-memory client harness.
