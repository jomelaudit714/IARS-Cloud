IARS V4.5.49 — Live Notification Polling

BASELINE
- Exact IARS V4.5.48 notification-center deployment.

LIVE BEHAVIOR
- Unread notification count is polled automatically every 3 seconds while the IARS session is open.
- The browser-tab title updates automatically to "(N) Internal Audit Report System" without a manual page refresh.
- The red unread badge over the fixed notification bell updates automatically without a full-app rerun.
- Opening the notification popover refreshes its list immediately using a fragment-only rerun.
- Mark-as-read and Mark-all-read rerun only the notification fragment.
- Navigation from a notification intentionally performs a normal page rerun.

SAFETY
- No global auto-refresh and no periodic full-app rerun.
- PDF Tagging, Gantt, Audit Extraction, Excel Conversion, Archive, Authentication, Theme, assets, dependencies, and existing SQL were not modified.

DEPLOYMENT
1. Deploy all files in this ZIP to the GitHub repository root, replacing the V4.5.48 files.
2. Reboot Streamlit and hard-refresh once after deployment.
3. Confirm v4.5.49 in the header / Settings.
4. Keep the IARS browser tab open. A new notification should appear in the bell badge and browser title within about 3 seconds even when another browser tab is active.

DATABASE
- No new Supabase migration is required beyond the V4.5.48 notification tables.
