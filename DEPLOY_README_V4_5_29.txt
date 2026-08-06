IARS V4.5.29 CLEAN FULL DEPLOYMENT

Changes:
- Moves authenticated modules upward to recover unused space below the fixed header.
- Renders the Gantt table directly in the Streamlit page, eliminating iframe click blocking.
- Freezes the Company-to-December header inside the Gantt scroll viewport.
- Lets Admin/Supervisor select every visible audit/report workflow status.
- Fits Accountability header and amount text inside the compact column.
- Removes the long Administrator/Supervisor instruction panel.

Deployment:
1. Extract this ZIP.
2. Upload the contents to the GitHub repository root and replace existing files.
3. Keep Supabase credentials only in Streamlit Secrets.
4. Reboot the Streamlit app.
5. Confirm the header shows v4.5.29.

No new Supabase migration is required.
