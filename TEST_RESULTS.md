# Test Results — IARS v4.0.0

## Completed checks

- All Python source files compile successfully.
- `app.py` references only functions available in the included modules.
- The supplied EDL logo is an exact byte-for-byte copy of the user's original logo.
- `data/Master_Data.xlsx` opens successfully and contains the required `Employees` and `Auditors` worksheets.
- Report Templates and Policies & Memoranda accept only Excel, Word and PDF extensions.
- Document-library storage paths, filtering and duplicate-hash helpers were tested.
- Existing parser API functions required by the interface are retained.
- No real credentials are included in the package.

## Deployment-dependent checks

The following require the user's Streamlit and Supabase environment:

- Actual account sign-in and administrator approval
- Actual Supabase uploads/downloads
- Actual PDF archive compression and storage
- Actual document-library uploads/downloads
- Browser rendering across desktop and tablet devices

Run `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql` before testing the two new document-library pages.
