# IARS v4.4.14 — Profile Menu Fixes

- Replaced the URL/query-parameter profile trigger with a Streamlit session-state trigger so opening the profile menu does not return the user to the login page.
- Added clearer framed controls for Change Username and Change Password.
- Reworked profile-picture persistence to use the private `iars-profile-pictures` Supabase Storage bucket and store only the object path in `iars_profiles`.
- Added specific readiness diagnostics for the profile table and Storage bucket instead of a single generic storage error.
- Added a polished circular close button and retained Sign Out inside the profile menu.
- Enlarged the top-right avatar to 46×46 px and expanded the profile card for balanced spacing.
- Updated `SUPABASE_PROFILE_SETUP.sql` so it can safely be run again over an earlier profile setup.
