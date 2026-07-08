# IARS V4.4.20 – Profile Avatar Live Preview

## Added
- Interactive profile picture positioning using `streamlit-cropper`
- Live circular preview so the user can see the exact look inside the top-right avatar before saving
- Square output preview for the final saved file

## Updated
- Profile picture upload instructions now explain drag/reposition behavior
- Saved profile image still exports as optimized 320x320 JPEG for consistent display performance

## Fallback behavior
- If the cropper component is unavailable in a runtime environment, the system falls back to the centered auto-crop behavior instead of breaking the profile menu
