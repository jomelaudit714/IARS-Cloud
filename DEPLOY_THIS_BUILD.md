# Deploy IARS v4.4.15

1. Run the included latest `SUPABASE_PROFILE_SETUP.sql` in Supabase SQL Editor. It is safe to run over the earlier profile setup; do not drop the existing profile table or bucket.
2. Extract the ZIP locally.
3. Upload the extracted contents directly to the GitHub repository root, replacing the previous files.
4. Do not upload the ZIP as an unextracted file or place the project in an extra nested folder.
5. Commit to the branch used by Streamlit.
6. Open Streamlit **Manage app → Reboot app**.
7. Refresh the browser with **Ctrl + F5**.

JPG, JPEG, and PNG profile pictures are automatically centered, square-cropped, resized to 320 × 320 pixels, and fitted inside the circular avatar. The app uses Supabase Storage first and automatically falls back to the secure profile record when Storage is unavailable.
