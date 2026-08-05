# IARS V4.5.23 — No-Wrap Sticky Gantt Header + Equal Compact Columns

- Fixed December appearing below the first columns by forcing all 17 Gantt columns to remain on one horizontal row.
- Made the complete Company / Department through December header sticky inside the Gantt vertical scroll area.
- Added a direct sticky rule on the actual Streamlit header row for more reliable behavior.
- Centered every header label inside its box.
- Set Company / Department, Custodian, Audit Task, Accountability, Frequency, and all month columns to the same compact 104 px width.
- Retained peso formatting with comma separators and two decimal places, for example `₱4,000.00`.
- No Supabase migration is required.
