# IARS V4.4.94 Test Results

## Passed — 3 consecutive runs

- Python compilation: `app.py`, `iars_parser.py`, `iars_pdf_editor.py`
- Blank-Issue-No continuation row title detection
- `OUTDATED DAILY MONITORING` captured after `INCOMPLETE RECEIPT INFORMATION`
- Document order preserved
- Same Issue No. inherited
- Sub-issue index incremented
- Continuation recommendation assigned to the correct finding
- Ordinary narrative continuation not misclassified as a new finding
- Next numbered issue remains separate
- Two actual findings under one Task ID both retained

## Regression checks

Existing local PDFs were reprocessed without unintended new rows:

- `2026IAD269_Eldia_Marvihills.pdf`
- `tagged_2026IAD269_Eldia_Marvihills.pdf`
- `AUDIT REPORT ASR NELSON CUSTODIO.pdf`
- `AUDIT REPORT TSS ESPINASE.pdf`

The attached 2026IAD236 page-break structure was reproduced as a focused table fixture because the attachment was available to the model as a rendered/file reference rather than a local container path.
