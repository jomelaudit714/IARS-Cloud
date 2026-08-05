# Verification — IARS V4.5.21

## Automated checks completed

- Python compilation: passed.
- Full regression suite: 14 tests passed.
- Month-filter row-selection simulation: 120 repeated comparisons passed.
- One-page source validation: pagination controls removed.
- Fixed matrix validation: 5 identifying columns plus 12 month columns retained.
- Existing Gantt, holiday, IRS, FRS, Warehouse, LOGP, and Invoice regression tests retained and passed.
- Static browser render preview generated and visually inspected.
- ZIP integrity and required-file verification completed after packaging.

## Important limitation

The full live Streamlit application could not be launched in this runtime because the Streamlit package is unavailable. Final deployed click behavior and CSS positioning must therefore be confirmed after the package is uploaded to the live IARS repository and Streamlit is rebooted.
