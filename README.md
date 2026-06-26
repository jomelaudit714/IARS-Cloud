# IARS v3.9.0 — EDL Audit Pro Interface

This release applies the EDL Group visual identity and a professional Internal Audit design to the existing v3.8.2 system. It retains the multi-user admin-approved login, shared PDF archive, direct archive options, automatic PDF compression, exact database headers, Master Data behavior, and all extraction logic.

## Interface changes

- EDL logo integrated into the login page, application header, and sidebar
- EDL-inspired navy, gold, red, green, and blue color system
- Branded login experience with Sign In, Sign Up, Verify, and Reset Password tabs
- New Home dashboard with employee, auditor, archive, and connection status cards
- Recent shared archive activity on the Home page
- Redesigned sidebar with branded account, Master Data, and archive status panels
- Updated workspace tabs: Home, Generate Extraction, PDF Tagging, and PDF Archive
- Improved cards, forms, file uploaders, buttons, data tables, alerts, and responsive mobile layout
- Light main workspace with a dark navy Internal Audit sidebar

## Existing functionality retained

- All signed-in auditors may view, search, preview, and download PDFs uploaded by other auditors
- Uploaded PDFs may be processed using any of these options:
  1. Generate extraction only
  2. Generate extraction and archive original PDFs
  3. Archive original PDFs only
- Automatic PDF compression before archive upload
- Administrator-only archive deletion, Master Data updates, and account administration
- Admin-approved username/nickname login without SMS
- Exact 27-column external-system export headers
- Exact Master Data Findings, Response, Frequency, and Auditor labels
- Blank `by02` when no second auditor is indicated

## Deployment

The ZIP is arranged with the deployment files at its root. Extract it, upload the files to the GitHub repository used by Streamlit, commit them together, and reboot the app.

No new Supabase SQL migration is required if v3.8.2 was already working.
