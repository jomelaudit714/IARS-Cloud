# IARS V4.4.69 — Policies & Memoranda Company Folders

## Required deployment order

1. In the existing Supabase project, open **SQL Editor**.
2. Run `SUPABASE_DOCUMENT_FOLDER_MIGRATION.sql` once.
3. Replace these repository files:
   - `app.py`
   - `iars_document_library.py`
   - `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql`
4. Commit the changes and reboot the Streamlit app.
5. Refresh the browser using **Ctrl + F5**.

## New workflow

1. Open **Policies & Memoranda**.
2. Click **Create Folder**.
3. Enter the official company/group name, such as:
   - Estancia De Lorenzo
   - EDL Group of Companies
4. Open **Upload Policy or Memorandum**.
5. Select the company/group folder before uploading.
6. Click a company folder to open its popup.
7. Select a document, click **Open / Read Document**, then read or download it.

## Preview support

- PDF: page-by-page readable preview
- DOCX: readable text preview
- XLSX: worksheet table preview
- DOC/XLS: download available; browser preview is not supported

## Existing records

Policies and memoranda uploaded before this migration remain available under
**Unfiled / General**. New uploads must be assigned to a company/group folder.

## Files intentionally not included

The patch does not replace the parser, PDF Tagging editor, authentication,
archive, extraction worker, theme, or Master Data files.
