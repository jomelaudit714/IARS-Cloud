# IARS V4.4.55 – Camera Menu, Avatar Dialog Fit, Login Enter Fix

## Base
- Built from the user-confirmed stable V4.4.51 ZIP.

## Fixed
1. Camera icon target
   - Camera icon now consistently opens only the camera avatar menu:
     - See Avatar
     - Change Avatar
   - The invisible Edit Profile trigger was narrowed so it does not overlap the camera icon area.
   - Camera popover is rendered after the Edit Profile popover so it wins click priority.

2. Change Avatar dialog vertical fit
   - Avatar dialog is more compact.
   - Preview images are smaller.
   - Dialog max-height is limited and scrollable when needed.

3. Login Enter key behavior
   - Forgot Password is no longer a form submit button.
   - Sign In is now the only submit button inside the sign-in form.
   - Pressing Enter in username/password submits Sign In instead of opening Forgot Password.

## Kept
- PDF Tagging original and untouched.
- Simple auto-fit avatar upload.
- No avatar component.
- No cropper.
