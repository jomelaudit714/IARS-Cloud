# IARS V4.4.81 Changelog

## Full-document preview standard

- Policies & Memoranda PDF preview now renders every page continuously in one centered, scrollable popup.
- Shared PDF Archive preview now renders every page continuously in one centered, scrollable popup.
- Removed PDF page selectors from both preview modules.
- Increased preview width and PDF render resolution for clearer reading.

## PDF Tagging

- PDF Tagging now opens in a centered full-document popup.
- Every PDF page is displayed in sequence, allowing continuous scrolling without changing a page selector.
- Each page remains independently taggable.
- Updated the PDF editor component to merge page state safely so one page cannot overwrite tags saved on another page.

## Generate Extraction

- Added a manual **Clear Records** button beside **Download Consolidated Excel Output**.
- Clear Records removes the generated table, archive results, and processing messages only after the user chooses to clear them.
- Downloading the Excel file does not automatically delete the generated records.

## Download layout

- Corrected the Policies & Memoranda download header/button alignment.
- Replaced wrapping download text with stable, centered labels and icon-only table action headings.

## Unchanged

- Audit extraction and classification rules
- Duplicate-report notification
- Weekly Itinerary module
- Policies folder search, category, admin edit, and delete functions
- Authentication, sidebar, dashboard, archive storage, and Master Data
