IARS V4.5.51 DEPLOYMENT

1. Run SUPABASE_NOTIFICATIONS_V4_5_51.sql in the SAME Supabase project used by IARS.
   This is required for the per-user Open & Delete behavior.
2. Upload/replace the files from the V4.5.51 ZIP in the GitHub repository root.
3. Reboot/redeploy Streamlit Cloud.
4. Confirm the header displays v4.5.51.
5. Test with two accounts/browsers:
   - Keep the auditor account open on any IARS page.
   - From Admin, approve/return an itinerary or save a Gantt month assigned to that auditor.
   - The auditor badge and browser-tab count should update automatically on the live polling cycle (about 2 seconds) without manual refresh while the IARS session remains connected.
6. Open & Delete behavior:
   - Information/Announcement -> full message dialog.
   - Weekly Itinerary -> exact itinerary record/image.
   - Yearly Audit Gantt -> exact monthly schedule editor.
   - Policy/Memorandum -> exact document preview.

No other Supabase migration is required for V4.5.51 beyond the V4.5.48 notification setup already deployed and the new V4.5.51 additive migration.
