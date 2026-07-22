# V4.4.78 Patch Instructions

Replace these files in the current GitHub repository:

1. `app.py`
2. `iars_parser.py`
3. `iars_weekly_itinerary.py`

No Supabase SQL or dependency change is required.

After committing the files:

1. Reboot the Streamlit application.
2. Perform a hard refresh using `Ctrl + F5`.
3. Test Generate Extraction using `2026IAD269_Eldia_Marvihills.pdf`.

Expected recommendation for Issue 2:

`Review Circular 2020- 001 no. 4 stating “Each disbursement must be supported by original copies of valid supporting documents and must be stamped “PAID” after payment to avoid re-use or double payment.”`

Expected upload behavior:

- Successful action: uploader clears automatically.
- Failed action: uploader retains the selected file for retry.
- Generate Extraction results remain displayed after the input PDF list clears.
