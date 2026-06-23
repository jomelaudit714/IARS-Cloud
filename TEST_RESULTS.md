# IARS v3.1 Test Results

## Source validation
- Python compilation passed for `app.py`, `iars_archive.py`, `iars_parser.py`, and `iars_pdf_editor.py`.
- New Supabase auditor functions passed simulated list, insert, active filtering, and duplicate-prevention tests.

## Master Data validation
- Uploaded workbook imported successfully with 15 sheets.
- Employees range retained: `A1:F1016`.
- Auditors range retained: `A1:F10`.
- Classification Matrix range retained: `A1:S39`.
- No spreadsheet formula-error strings were detected.
- Clean re-export preserved the tested key ranges exactly.
- Clean `.xlsx` ZIP integrity passed.

## Uploaded By tests
- Active Master Data auditors included.
- Inactive auditors excluded.
- Supabase-added active auditor included.
- Duplicate Master Data/cloud auditor returned only once.
- Case-insensitive cloud duplicate was blocked.
- Search filtering and clear-state logic passed at source level.

## Auditee Master Data tests
- Official names sourced from the Employees sheet.
- Header `Dianne Susie Berbano and Jinky Venise Angel` resolved to:
  - `Dianne Susie Capisonda Berbano`
  - `Jinky Venise Vicente Angel`
- Duplicate official names were removed.
- Canonical names from extraction output were joined correctly for archive metadata.

## Parser regression
- `2026IAD220_Jugine_Corpuz.pdf`: 4 rows generated.
- `2026IAD221_Timothy_So(1).pdf`: 1 row generated.
- `2026IAD209_Michelle_Mesa.pdf`: 3 rows generated.
- `tagged_2026IAD222_Vet_City_Marikina (2).pdf`: 7 rows generated.
- Required output headers including `#` and `Encoded Date` remained present.

## Deployment note
A live Add New Auditor insertion requires the user's Supabase project. Run `SUPABASE_AUDITOR_MIGRATION.sql` before using that button.

## Streamlit runtime tests
- Streamlit 1.58.0 `AppTest` completed with zero application exceptions.
- All three tabs loaded: Generate Extraction, PDF Tagging Editor, and Saved PDFs.
- Local Streamlit server started successfully and returned `ok` from the health endpoint.
