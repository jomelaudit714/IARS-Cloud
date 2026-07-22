# IARS V4.4.78 Changelog

## 1. EDL logo alignment

- Shifted the sidebar EDL logo slightly farther to the right.
- No other sidebar spacing or Dashboard layout was changed.

## 2. Circular recommendation extraction

The recommendation parser previously treated `no.` as a sentence ending when a recommendation exceeded the normal concise-text limit. This caused:

`Review Circular 2020- 001 no.`

instead of the complete recommendation.

Corrections:

- `No.`, `no.`, `Nos.`, and `nos.` are protected during sentence parsing.
- Recommendations that cite a numbered Circular are preserved in full.
- Closing quotation marks no longer cause a duplicate final period.

Validated against `2026IAD269_Eldia_Marvihills.pdf`:

- Circular 2020-001 no. 4 recommendation: complete
- Circular 2020-001 no. 6 recommendation: complete

## 3. Automatic clearing of successful upload actions

File upload fields now clear only after a successful final action:

- Generate Extraction
- Generate Extraction and Archive Original PDFs
- Archive Original PDFs Only
- PDF Tagging after tagged-PDF download or successful archive
- Shared PDF Archive direct upload
- Audit Workpapers upload
- Policies & Memoranda upload
- Weekly Itinerary submission
- Master Data activation

If processing or upload fails, the selected file remains available so the user can retry.

Generate Extraction results remain visible after the PDF uploader is cleared, including the editable records and Excel download.

## Not changed

- Audit classification and scoring rules
- Operations Audit filters
- Weekly Itinerary Dashboard layout
- Recent Archive Activity size
- PDF Tagging editor behavior before final download/archive
- Profile/avatar crop workflow
