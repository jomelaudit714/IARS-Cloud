IARS V4.5.43 DEPLOYMENT

1. Use this ZIP as a complete deployment package based on V4.5.42.
2. Extract the ZIP.
3. Upload the extracted contents directly to the GitHub repository root and replace existing files.
4. Reboot/redeploy the Streamlit app.
5. Confirm that the header shows IARS v4.5.43.
6. Hard-refresh the browser once after deployment.

NO SUPABASE MIGRATION IS REQUIRED FOR V4.5.43.

PRIMARY GANTT CHECKS AFTER DEPLOYMENT
- Click any ordinary/static Gantt cell and use arrow keys: focus should move without opening a popup.
- Move the focus box onto a month schedule cell using arrow keys: no popup should open.
- Click the colored month schedule box with the mouse/touch pointer: the month editor should open.
- The month editor must scroll internally on shorter screens.
- Verify the status/date formats against CHANGE_MANIFEST_V4_5_43.txt.
