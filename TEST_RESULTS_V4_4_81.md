# IARS V4.4.81 Test Results

## Code validation

- Python compilation passed three consecutive runs.
- `app.py` and `iars_pdf_editor.py` AST parsing passed.
- PDF editor JavaScript syntax passed Node.js validation.

## Actual PDF rendering

Tested with two uploaded five-page audit reports:

- `2026IAD269_Eldia_Marvihills.pdf`
- `AUDIT REPORT ASR NELSON CUSTODIO.pdf`

Results:

- All five pages were rendered in sequence.
- Each page rendered at approximately 1071 × 1386 pixels using the release preview zoom.
- No page selector was required.

## Workflow checks

- Policies PDF preview rendered five continuous pages in a test harness.
- Generate Extraction Clear Records removed the saved payload and data-editor state in a test harness.
- Multi-page PDF Tagging state merge preserved tags from separate pages.
- Shared Archive and Policies preview state keys remain isolated.

## Clean package validation

- Clean ZIP extraction and compilation passed three consecutive runs.
- No `__pycache__` or `.pyc` files are included.
