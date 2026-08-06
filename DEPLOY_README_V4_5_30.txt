IARS V4.5.30 CLEAN FULL DEPLOYMENT

FIXED
- Clicking a January-December month cell no longer changes the browser URL.
- Month selection uses Streamlit native single-cell selection and keeps the active page on Yearly Audit Gantt.
- The selected month opens the existing Admin/Auditor editor dialog.
- Company through Frequency remain pinned during horizontal scrolling.
- The grid header remains visible inside the native scrollable table.
- Repeated clicks on the same month cell are reset and accepted immediately.

DEPLOYMENT
1. Extract this ZIP.
2. Upload all extracted files/folders to the GitHub repository root.
3. Replace existing files.
4. Reboot the Streamlit app.
5. Confirm the header shows v4.5.30.

No new Supabase SQL migration is required.
