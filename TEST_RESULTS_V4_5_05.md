# V4.5.05 Test Results

## Source validation
- Python compilation passed for `app.py`, `iars_auth.py`, and `iars_theme.py`.
- The packaged login artwork SHA-256 matches the uploaded approved `login_left_panel.png`.

## Render validation
- Viewport `1366x768`: **PASS**
  - object-fit: `contain`
  - transform: `none`
  - object-position: `50% 50%`
  - sidebar text color: `rgb(247, 231, 178)`
  - source image loaded: `1122 × 1402`
- Viewport `1920x1080`: **PASS**
  - object-fit: `contain`
  - transform: `none`
  - object-position: `50% 50%`
  - sidebar text color: `rgb(247, 231, 178)`
  - source image loaded: `1122 × 1402`

## Proof images
- `test_proof/render_1366x768.png`
- `test_proof/render_1920x1080.png`

The render test used the packaged image and the final CSS values from the patch.
