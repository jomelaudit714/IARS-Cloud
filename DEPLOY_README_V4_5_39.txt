IARS V4.5.39 — Recommendation Continuity and Smart 150-Character Capture

BASELINE
- IARS V4.5.38 complete deployment ZIP.

DEPLOYMENT
1. Extract this ZIP.
2. Upload the extracted files and folders directly to the GitHub repository root.
3. Replace existing files.
4. Reboot Streamlit.
5. Confirm that the header displays v4.5.39.

NO DATABASE MIGRATION
- No Supabase SQL change is required.

TARGET CHANGE
- Preserve complete recommendation wording and punctuation when it fits within 150 characters.
- Keep "Again, we recommend..." as one recommendation.
- Use Recommendation2 only for a genuinely separate recommendation.
- Safely shorten recommendations longer than 150 characters without splitting words.
