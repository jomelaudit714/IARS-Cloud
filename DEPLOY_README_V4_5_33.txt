IARS V4.5.33 — COMPLETE CLEAN DEPLOYMENT

CHANGE
- Added Change Full Name in the top-right Edit Profile menu.
- Administrator full name is saved in iars_profiles.full_name_override.
- Auditor full name is saved in iars_users.full_name.
- The updated name immediately refreshes the user card and current session.
- Existing Change Username, Change Password, avatar, Gantt, archive, conversion and itinerary features are retained.

REQUIRED SUPABASE STEP FOR ADMINISTRATOR ACCOUNT
1. Open Supabase SQL Editor.
2. Run SUPABASE_PROFILE_FULL_NAME_MIGRATION_V4_5_33.sql once.
3. Upload this deployment to the repository root and replace existing files.
4. Reboot Streamlit.
5. Confirm v4.5.33 in the IARS header.

SECURITY
- Current password is required before changing the full name.
- The real Streamlit secrets.toml is not included.
