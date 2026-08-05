# Verification — IARS V4.5.22

- Python compilation: required.
- Full automated test suite: required.
- Currency formatting checks: `5000 → ₱5,000.00`, `12345.5 → ₱12,345.50`.
- Static browser layout test: sticky header remains in the same vertical position after scrolling the Gantt viewport.
- Static browser layout test: horizontal scroll retains all January–December columns.
- ZIP extraction/integrity: required.

The local test environment does not include the Streamlit runtime package, so final deployed Streamlit verification is performed after repository upload and reboot.
