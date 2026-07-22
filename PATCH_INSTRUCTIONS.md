# IARS V4.4.72 Patch Instructions

Replace only these files in the current GitHub repository:

1. `app.py`
2. `iars_parser.py`
3. `data/Master_Data.xlsx`

Do not replace the other current modules.

After committing the files:

1. Reboot the Streamlit application.
2. Wait for dependency processing to finish.
3. Open the app and press `Ctrl + F5`.
4. Generate the extraction again using `AUDIT REPORT TSS ESPINASE.pdf`.

Expected result: one Operations Audit row for `STOCK OVERAGE: P1,500` with
category `Stock Overage (below P3,000.00)` and `Audited By1 = Fritz Paul Llanes`.
