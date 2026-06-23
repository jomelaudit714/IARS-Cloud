# IARS v3.2 Test Results

## Source validation
- Python compilation passed for `app.py`, `iars_archive.py`, `iars_parser.py`, and `iars_pdf_editor.py`.
- Parser imports and Master Data option loading passed.

## Exact-label tests
- Findings output uses only `Classification_Matrix → Category`; no trailing score remains in the Findings value.
- Score is retrieved separately from `Classification_Matrix → Score`.
- Currency-format variants such as `₱3,000.00` and `P3,000.00` map to the exact Master Data category text.
- Response output preserved the current Master Data value `Do Some ADJUSTMENT`.
- Frequency output preserved the current Master Data values such as `FIRST time` and `SECOND time`.
- Auditor matching returned the exact Master Data value `Jomel Santiago`.
- Edited output normalization refreshed Score, Improve Score, Net Score, User, and canonical labels before Excel download.

## Current Master Data preservation
- `data/Master_Data.xlsx` is byte-for-byte identical to the validated uploaded `Master_Data(4).xlsx`.
- All existing user edits were preserved.

## Existing archive controls
- `list_additional_auditors` and `add_additional_auditor` remain available.
- Supabase auditor migration and archive features remain unchanged.
