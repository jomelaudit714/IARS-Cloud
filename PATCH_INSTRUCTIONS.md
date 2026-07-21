# IARS V4.4.70 — Operations Audit Rules Patch

## Replace only these files

1. `app.py`
2. `iars_parser.py`

Upload both files to the root of the current GitHub repository and overwrite the existing copies. Do not delete or replace the other current IARS files.

After committing the changes:

1. Reboot the Streamlit app.
2. Wait for deployment to finish.
3. Use `Ctrl + F5` in the browser.

## Operations Audit-only rules

1. Cash Count and Stock Count or location/place reports are classified as Operations Audit when the personnel position is one of the approved operations roles.
2. `No Cash Collections during Audit` is ignored as an issue/table.
3. Stock overage/shortage uses the P3,000 threshold.
4. Cash and stock no-variance titles are combined into one `No Findings` row.
5. `Date_End` retains the date range through the comma and excludes the year. Example: `January 1 to June 30,`.
6. `No Collections Shortage or Overage` is tagged `No Findings`.
7. `By01` comes from `Prepared by`, `Prepared/Audited by`, or `Audited by`.

Financial Audit behavior is unchanged.
