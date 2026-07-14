# Changelog — V4.4.59

## Base

Built from the clean user-approved V4.4.58 ZIP.

## Sidebar restore fix

- Corrected the collapsed-sidebar restore selector for Streamlit 1.47.1.
- The actual Streamlit frontend test ID is `stExpandSidebarButton`.
- The restore control is now fixed at the upper-left and remains clickable even though the Streamlit header is visually hidden.
- The restore control uses the existing EDL navy-and-gold theme.
- Its icon is forced to remain visible in white.
- The sidebar still restores to its original width.
- The main content still expands while the sidebar is hidden.

## Retained unchanged

- Original EDL theme, logo design, colors, fonts, borders, shadows, icons, and header
- Sidebar contents positioned slightly higher
- EDL logo horizontally centered
- Five Dashboard summary cards
- Archive Status removed
- Quick Actions removed
- System Overview removed
- Recent Archive Activity layout
- Camera/avatar and login fixes
- Original PDF Tagging implementation
