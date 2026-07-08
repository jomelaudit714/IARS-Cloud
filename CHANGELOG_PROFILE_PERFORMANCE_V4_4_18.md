# CHANGELOG_PROFILE_PERFORMANCE_V4_4_18

## Purpose
Improve the perceived speed and smoothness of IARS login, sign out, and page navigation based on the reported delay/white-screen video.

## Fixes Applied

1. Login transition
- Removed the extra success-message/mask step before dashboard rerender.
- Session is now set directly after valid credentials and reruns immediately.
- User/profile data is cached in the active Streamlit session to avoid repeated Supabase reads after login.

2. Sign out transition
- Replaced the Streamlit Sign Out button with a direct front-end sign-out route.
- This avoids rendering the old dashboard/profile-menu state during logout.
- Sign-out now clears the session and returns directly to the login page route.

3. Sidebar and dashboard navigation
- Removed unnecessary explicit `st.rerun()` calls from sidebar navigation buttons.
- Navigation now uses the current button-triggered rerun only, preventing double rerun/flicker.
- Dashboard quick actions retain callback-based navigation.

4. Repeated Supabase reads reduced
- Active user/profile cache added for the current session.
- Additional auditors list is short-term cached.
- Dashboard archive/workpaper/policy list calls are short-term cached.
- Dashboard overview limits are reduced for faster first paint.

5. White-screen / stale portion protection
- Added a lightweight browser-side transition veil for auth and route changes.
- This prevents old page fragments or a blank white frame from being visible while Streamlit reconciles the next page.

## Files Updated
- `app.py`
- `iars_auth.py`
- `iars_theme.py`

## Version
- Updated visible app version to `4.4.18`.
