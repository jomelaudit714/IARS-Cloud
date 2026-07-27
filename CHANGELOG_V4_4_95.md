# IARS V4.4.95

## Policies & Memoranda schema fix

- Added the required `document_library.subject_category` Supabase migration.
- Added `notify pgrst, 'reload schema'` so the API schema cache refreshes after migration.
- Added a pre-upload schema check for Policies & Memoranda.
- The app now stops before uploading to Storage when `subject_category` is missing, instead of uploading first and then failing during metadata insertion.
- Added a clear, actionable error telling the administrator which SQL file to run.
- Applied the same schema validation before editing policy metadata.
- Preserved all V4.4.94 extraction and continuation-issue fixes.
