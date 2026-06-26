# Changelog — IARS v4.0.0

## Interface

- Replaced the previous tab-first layout with professional sidebar navigation.
- Applied a refined Internal Audit palette using navy, white and restrained gold.
- Used the exact original EDL GROUP OF COMPANIES logo throughout the system.
- Added a redesigned login interface, dashboard hero, metric cards and quick actions.
- Fixed custom HTML rendering by using Streamlit HTML rendering instead of indented Markdown fragments.

## New libraries

- Added Report Templates Library supporting `.xlsx`, `.xls`, `.docx`, `.doc` and `.pdf`.
- Added Policies & Memoranda Archive supporting the same formats.
- Added search, category and file-type filtering, download, PDF first-page preview and administrator-only deletion.
- Added Supabase setup migration: `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql`.

## Administration

- Added full-page User Management.
- Added full-page Master Data Management with validation before replacement.
- Added read-only Settings page showing security and storage status.

## Existing functions retained

- Shared PDF Archive for all signed-in auditors.
- Direct PDF archive option with or without extraction.
- Automatic PDF compression.
- Exact database export headers and Master Data labels.
- Blank `by02` when no second auditor is indicated.
