# IARS V4.4.75 Dashboard and Weekly Itinerary Layout Patch

Replace these files in the current GitHub repository:

1. `app.py`
2. `iars_weekly_itinerary.py`

Then:

1. Commit the changes.
2. Reboot the Streamlit application.
3. Refresh the browser with `Ctrl + F5`.

No Supabase SQL or database migration is required for this update.

## Expected Dashboard

- The EDL logo is horizontally centered in the sidebar.
- Sidebar navigation begins closer to the logo.
- The application header, Welcome Back section, and cards are raised.
- Metric card text and values are larger and vertically balanced.
- The left Dashboard panel automatically shows the signed-in user's approved current itinerary image.
- The right Dashboard panel shows Recent Archive Activity.
- Administrators see pending approvals above their own approved current itinerary.
