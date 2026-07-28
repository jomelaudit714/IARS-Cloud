# IARS V4.4.96

## Policies & Memoranda
- Short table values are centered horizontally and vertically inside their bordered cells.
- Long titles and long metadata remain left-aligned for readability.
- Administrators can rename a normal company/group folder from inside the folder popup.
- Duplicate and blank folder names are blocked.
- Renaming changes the folder display name only; document links and stored files remain intact through the existing folder ID.

## Shared PDF Archive
- Administrators now see a Delete column in the archive table.
- The delete action opens a confirmation dialog and requires the word DELETE.
- Deletion removes both the private PDF and its archive database record.
- Non-admin users continue to see only View and Download.

## Compatibility
- Based on IARS V4.4.95.
- No new Supabase SQL or requirements update is required.
- The V4.4.95 subject_category migration remains required if it has not yet been run.
