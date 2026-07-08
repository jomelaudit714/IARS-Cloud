# Deploy IARS v4.4.16

1. Run the included latest `SUPABASE_PROFILE_SETUP.sql` in Supabase SQL Editor. It is safe to run over the earlier profile setup; do not drop the existing profile table or bucket.
2. Extract the ZIP locally.
3. Upload the extracted contents directly to the GitHub repository root, replacing the previous files.
4. Do not upload the ZIP as an unextracted file or place the project in an extra nested folder.
5. Commit to the branch used by Streamlit.
6. Open Streamlit **Manage app → Reboot app**.
7. Refresh the browser with **Ctrl + F5**.

JPG, JPEG, and PNG profile pictures are automatically centered, square-cropped, resized to 320 × 320 pixels, and fitted inside the circular avatar. The app uses Supabase Storage first and automatically falls back to the secure profile record when Storage is unavailable.


## V4.4.16 Notes
- Use this build to fix profile menu click smoothness, remove the close button tooltip, improve profile picture upload, and keep the dashboard after browser refresh.
- No new SQL is required if SUPABASE_PROFILE_SETUP.sql was already applied.

## V4.4.19 Deployment Note
After GitHub deployment, perform a browser hard refresh once (`Ctrl + F5`) so the previous V4.4.18 loading-overlay JavaScript listener is fully cleared from the browser tab. This build also includes a suppressor for the old listener, but a hard refresh is still recommended after deployment.
