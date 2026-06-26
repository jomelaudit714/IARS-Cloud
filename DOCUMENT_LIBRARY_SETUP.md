# Report Templates and Policies & Memoranda Setup

IARS v4.0.0 adds a shared document library for Excel, Word and PDF files.

## 1. Create the Supabase table and bucket

1. Open the same Supabase project used by the IARS PDF archive.
2. Open **SQL Editor**.
3. Create a new query.
4. Paste and run `SUPABASE_DOCUMENT_LIBRARY_SETUP.sql`.
5. A successful run normally shows **Success. No rows returned**.

The migration creates:

- Private Storage bucket: `iars-document-library`
- Metadata table: `document_library`

## 2. Optional Streamlit Secrets entries

The code uses the default names automatically. You may add these values under the existing `[supabase]` section:

```toml
[supabase]
documents_bucket = "iars-document-library"
documents_table = "document_library"
```

## 3. Access controls

- All signed-in auditors may browse and download files.
- All signed-in auditors may upload approved working resources.
- Only the IARS administrator may delete files.
- The Supabase bucket remains private and is accessed only through the server-side service-role key.

## 4. Supported files

- Excel: `.xlsx`, `.xls`
- Word: `.docx`, `.doc`
- PDF: `.pdf`
