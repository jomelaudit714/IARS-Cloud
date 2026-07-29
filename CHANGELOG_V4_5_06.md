# IARS V4.5.06

## Sidebar branding
- Added `assets/sidebar_edl_logo.png`, cropped from the approved login artwork.
- The embedded `GROUP OF COMPANIES` text is now light cream and readable.
- `render_sidebar_brand()` now uses the sidebar-specific logo first, with `edl_logo.png` as fallback.
- Removed the old forced `translateX(28px)` sidebar shift so the logo is centered.
- The separate sidebar line `EDL GROUP OF COMPANIES` is also light cream.

## Dashboard spacing
- Raised the `Welcome back` section by 24.8 px using a negative top margin.
- Because this reduces normal document flow, the metric cards and all Dashboard content below it also move upward.

## Version
- Updated the visible version to `4.5.06`.
