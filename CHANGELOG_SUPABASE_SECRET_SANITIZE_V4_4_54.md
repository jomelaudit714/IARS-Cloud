# IARS V4.4.54 – Supabase Secret Sanitizer

## Base
- Built from V4.4.53.

## Why
- User confirmed the Streamlit Cloud Secrets were not changed.
- After the segmentation fault was fixed, the app reached Supabase initialization and showed `Invalid API key`.
- The pinned Supabase client validates the key format strictly.

## Fixed
- Added normalization for Supabase secret values:
  - trims spaces
  - removes accidental surrounding quotes
  - removes `Bearer ` prefix
  - removes line breaks and whitespace inside the key
  - trims trailing slash from Supabase URL
- Added safer diagnostic error message that shows only key length/dot count/start hint, not the full secret.

## Kept
- Stable dependency pins from V4.4.52/V4.4.53.
- Streamlit 1.47 image compatibility patch.
- Simple auto-fit avatar upload.
- Centered See Avatar and Change Avatar popups.
- Stale popup cleanup.
- PDF Tagging original and untouched.
