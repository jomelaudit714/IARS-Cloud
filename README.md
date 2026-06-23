# IARS v3.5.1 — FORTH time label correction

This package retains all IARS v3.5 changes and applies only the requested frequency-label correction:

- `FOURTH Time` / `Fourth Time` → `FORTH time`

The correction is applied in:

- Master Data → `Frequency_Master`
- Master Data → `Frequency_Keywords`
- IARS frequency dropdown/fallback value
- Frequency normalization and scoring
- External-system export

All other values, database headers, audit types, response labels, case-status labels, and extraction rules remain unchanged.

## Deployment

Upload all files to the same GitHub repository and commit them together, or replace only:

- root-level `iars_parser.py`
- `data/Master_Data.xlsx`

Then reboot the Streamlit app.
