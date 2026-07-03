# v4.4.15 Profile Menu Trigger and Storage Fix

- The visible “Open profile menu” control is removed. The invisible trigger now overlays only the existing top-right user card.
- JPG, JPEG, and PNG uploads are automatically EXIF-corrected, center-cropped to a square, resized to 320 × 320 pixels, and displayed with circular cover fitting.
- Profile picture saving tries Supabase Storage first and automatically falls back to the secure `profile_picture_data` field if Storage is unavailable.
- `SUPABASE_PROFILE_SETUP.sql` now includes explicit `service_role` grants for the profile table and Storage tables.
- Profile storage diagnostics now distinguish table access from bucket availability.
