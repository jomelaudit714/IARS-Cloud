# Changelog — IARS v4.2.0

## Visual reliability corrections

- Replaced data-URI images with native `st.image()` rendering for the exact EDL logo and Internal Audit visual.
- The exact original `assets/edl_logo.png` is now displayed on the login page and sidebar.
- The Internal Audit reports/compliance/workpapers image is now displayed as a native Streamlit image on the login page and Dashboard.
- Replaced sidebar radio navigation with full-width navigation buttons to remove visible radio circles.
- Added a gold active-page state and professional navy inactive navigation state.
- Refined login and Dashboard containers for dependable rendering on Streamlit Community Cloud.
- Hidden Streamlit developer toolbar elements from the user-facing interface.

## Functional impact

No changes were made to authentication, extraction, PDF tagging, archive compression, shared PDF visibility, report-template library, policy/memorandum library, Master Data, export values, or Supabase tables.
