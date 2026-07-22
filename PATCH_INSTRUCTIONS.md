# IARS Weekly Itinerary Dashboard Layout Patch — V4.4.74

## Replace in GitHub

Replace only:

1. `app.py`
2. `iars_weekly_itinerary.py`

Commit the changes, reboot the Streamlit app, and press `Ctrl + F5`.

## Supabase SQL

No new database migration is required for this layout update.

The ZIP includes the corrected full setup SQL and the prior permission hotfix for reference. Run `RUN_THIS_NOW_SUPABASE_PERMISSION_FIX.sql` only when the app still reports PostgreSQL error `42501` for `weekly_itineraries`.

## Result

- Weekly Itinerary popup fits the screen.
- Approved itinerary is automatically visible on the Dashboard.
- Weekly Itinerary is on the left.
- Recent Archive Activity is on the right.
- Dashboard metric cards occupy the full horizontal width.
