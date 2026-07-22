# V4.4.78 Test Results

## Compilation

- `app.py`: passed
- `iars_parser.py`: passed
- `iars_weekly_itinerary.py`: passed
- Repeated compilation: 3 consecutive passes

## Actual PDF extraction

Test file: `2026IAD269_Eldia_Marvihills.pdf`

- Circular 2020-001 no. 4 recommendation captured in full: 3 passes
- Circular 2020-001 no. 6 recommendation captured in full: 3 passes
- Output finding rows remained 2: passed

## Operations Audit regression checks

- Nelson Custodio combined cash/stock no-variance output: retained
- TSS Espinase Stock Overage P1,500 output: retained
- Fritz Paul Llanes Prepared/Audited-by mapping: retained

## Upload-reset checks

- Every `st.file_uploader` in `app.py` uses a versioned key: passed
- Weekly Itinerary uploader uses a versioned key: passed
- Reset helper changes widget identity after success: passed
- Failed archive status does not clear the uploader: passed
- Duplicate-skipped archive status is treated as completed: passed
- Generate Extraction output is persisted independently of the cleared uploader: passed

## Layout

- Sidebar logo visual offset changed from 22 px to 28 px: passed
- No lower Dashboard column-size change: verified
