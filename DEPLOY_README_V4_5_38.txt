IARS V4.5.38 — Locked Extraction Classification Rules

Changes:
- Policy/process/procedure/guideline citations in recommendation or narrative override the generic BEST-PRACT fallback and classify as NONCONF.
- Classification uses the full recommendation text before output truncation.
- Recommendation1 and Recommendation2 are each limited to 150 characters, including ellipsis.
- Existing PDF Tagging behavior from V4.5.37 is retained unchanged.

Deployment:
1. Extract this ZIP.
2. Upload the contents directly to the GitHub repository root and replace existing files.
3. Reboot Streamlit and confirm v4.5.38.
4. No Supabase migration is required.

Regression protection included:
- LOCKED_EXTRACTION_RULES.md
- tests/test_locked_extraction_rules.py
