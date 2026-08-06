IARS V4.5.31 CLEAN FULL DEPLOYMENT

FIXED
- Removed the unsupported lazy parameter from st.dataframe for Streamlit 1.58.0 compatibility.
- Yearly Audit Gantt now renders instead of crashing with: ArrowMixin.dataframe() got an unexpected keyword argument 'lazy'.
- Native single-cell month selection remains enabled.
- Clicking a January-December cell stays on Yearly Audit Gantt and opens the month editor.
- Company through Frequency remain pinned during horizontal scrolling.
- Existing Gantt workflow, status colors, deadlines, and filters are retained.

DEPLOYMENT
1. Extract this ZIP.
2. Upload all extracted files/folders to the GitHub repository root.
3. Replace existing files.
4. Reboot the Streamlit app.
5. Confirm the header shows v4.5.31.

No new Supabase SQL migration is required.
