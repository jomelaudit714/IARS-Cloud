# CHANGELOG_NAVIGATION_NO_LOADING_V4_4_19

## Purpose
This build addresses the visible **Loading / Please wait** overlay that appeared every time the user switched between IARS modules.

## Fixes Applied
- Disabled the custom navigation loading veil for normal module/sidebar navigation.
- Added a browser-side suppressor so older transition handlers from the prior build are neutralized after deployment/refresh.
- Kept the transition veil limited to authentication actions only, such as Sign In and Sign Out.
- Added session-level caching for Shared PDF Archive records.
- Added session-level caching for Audit Workpapers and Policies & Memoranda lists.
- Added cache invalidation after upload, deletion, and manual refresh actions.
- Reduced repeated Supabase list calls during normal page switching.
- Updated app version display to 4.4.19.

## Expected Behavior
- Clicking Dashboard, Generate Extraction, PDF Tagging, Shared PDF Archive, Audit Workpapers, Policies & Memoranda, User Management, Master Data, or Settings should no longer show the large custom Loading card.
- First-time opening of a remote-data page may still need a short moment if Supabase is fetching records, but subsequent module switches should be smoother due to session cache.

## Note
Streamlit naturally reruns the script on widget clicks. This build removes the added custom loading overlay and reduces repeated remote calls, but it cannot convert Streamlit into a full single-page JavaScript app.
