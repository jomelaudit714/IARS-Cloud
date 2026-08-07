IARS V4.5.48 — Notification Center

BASELINE
- Exact deployed GitHub ZIP provided by the user: IARS-Cloud-main (2).zip
- Baseline app header version: V4.5.47

NEW FEATURES
- Notification bell for every signed-in user with unread badge.
- Browser-tab unread count: (N) Internal Audit Report System.
- Weekly Itinerary Approved notification to the affected auditor.
- Weekly Itinerary For Revision notification to the affected auditor, including admin remarks when available.
- New Policy / Memorandum notification broadcast to all users after a successful upload.
- Administrator Information / Announcement composer for all users or one selected active user.
- Mark as Read and Mark All as Read.
- Notification action shortcuts to Weekly Itinerary, Policies & Memoranda, or Dashboard.

IMPORTANT DATABASE STEP
1. Run SUPABASE_NOTIFICATIONS_V4_5_48.sql once in the Supabase SQL Editor.
2. Then deploy the V4.5.48 files to GitHub and reboot Streamlit.

DEPLOYMENT
1. Extract the ZIP.
2. Upload all contents to the GitHub repository root and replace matching files.
3. Run the notification SQL migration if it has not yet been run.
4. Reboot Streamlit and hard refresh once.
5. Confirm the header shows v4.5.48.

NOTES
- Notification failures are isolated and never block itinerary approval/return or policy upload.
- There is intentionally no global auto-refresh timer. This protects PDF Tagging and other interactive modules from background reruns. New notifications appear on the next normal rerun/navigation, or when the user opens the bell and clicks Refresh.
