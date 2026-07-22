# Deployment Instructions — V4.4.73

## 1. Run the database setup

Open the SQL Editor of the same Supabase project used by IARS and run:

`SUPABASE_WEEKLY_ITINERARY_SETUP.sql`

This creates:

- private bucket: `iars-weekly-itineraries`
- table: `weekly_itineraries`

## 2. Replace/add files in GitHub

Replace:

- `app.py`
- `iars_parser.py`
- `data/Master_Data.xlsx`

Add:

- `iars_weekly_itinerary.py`
- `SUPABASE_WEEKLY_ITINERARY_SETUP.sql`

Do not delete the other existing repository files.

## 3. Redeploy

Commit the changes, reboot the Streamlit app, then refresh the browser using `Ctrl + F5`.

The displayed version should be `V4.4.73`.
