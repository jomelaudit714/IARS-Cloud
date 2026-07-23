# Deployment Instructions — V4.4.79

## 1. Run the database migration first

Open the same Supabase project used by IARS, open **SQL Editor**, and run:

`SUPABASE_POLICY_SUBJECT_CATEGORY_MIGRATION.sql`

The final query should show the `subject_category` column.

## 2. Replace or add these GitHub files

- `app.py`
- `iars_document_library.py`
- `assets/login_left_panel.png`

The ZIP also includes the unchanged current `iars_parser.py` and
`iars_weekly_itinerary.py` so the patch remains aligned with V4.4.78.

For a new document-library installation, use the included corrected:

- `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql`

## 3. Deploy

Commit the files, reboot the Streamlit app, then use **Ctrl + F5**.

No requirements update is needed.
