# IARS V4.4.90 Patch Instructions

Replace only the current repository file:

1. `app.py`

Then commit the change, reboot the Streamlit application, and perform a hard
refresh (`Ctrl + F5`).

No Supabase SQL, requirements, Master Data, or storage migration is required.

This patch must be applied on top of V4.4.89 or the current repository that
already contains the V4.4.89 parser correction.
