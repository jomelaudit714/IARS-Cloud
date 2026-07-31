# V4.5.07 Test Results

## Browser simulation
- Total simulations: 200
- Passed: 200
- Failed: 0
- Tested alternating login/dashboard renders across fixed and randomized viewport sizes from 1000×700 to 1920×1200.

## Verified in every applicable simulation
- Login image: `object-fit: contain`
- Login image transform: `none`
- Login image natural size: 1122×1402
- Sidebar logo width: 146 px
- Sidebar logo center difference: no more than 0.6 px
- Sidebar label color: `rgb(247, 231, 178)` / `#F7E7B2`
- Header-to-Welcome gap: 22–25 px
- Version label: `v4.5.07`
- No horizontal overflow

## Asset verification
- V4.5.07 `login_left_panel.png` SHA-256 is identical to the approved V4.5.05 file:
  `e07a83dd91efe2ed86f49d64e16fffb8b95269253a46959bfb8560732db1a42a`
- The sidebar logo image contains visible light-colored pixels in the `GROUP OF COMPANIES` lettering region.
