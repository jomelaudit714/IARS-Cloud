# Changelog — V4.4.84

## Master Data

- Moved **Auditor Directory** and **Add New Auditor** from Shared PDF Archive to the administrator-only Master Data module.
- Retained the existing Supabase auditor-directory storage and dropdown integration.

## Shared PDF Archive

- Removed the **Filename** column from the visible archive table.
- Retained the filename internally for View, Download, preview captions, and downloaded filenames.
- Archive table now displays:
  - Audit Reference
  - Auditee Name
  - Uploaded Date
  - Uploaded By
  - View
  - Download
- Removed vertical spacing between archive rows.
- Strengthened the continuous grid borders so adjacent rows and columns share one clean border line.
- Adjusted column widths and header typography so every heading stays inside its corresponding border.

## Unchanged

- Search can still find records by filename even though Filename is not displayed.
- Full-document PDF preview is retained.
- View, Download, archive upload, deletion, and filters are retained.
- Other IARS modules and extraction rules are unchanged.
