# Test Results — IARS v4.4.11

Exact browser interaction sequence tested against the packaged PDF editor component:

- Click outside deselects textbox: passed
- One normal left click inside text focuses editor immediately: passed
- Typing works after that single click: passed
- Click outside, then one click back inside focuses immediately: passed
- Delete/retyping path after one-click return: passed
- Long-press plus drag inside text moves whole textbox: passed
- Drag on plain side/border moves whole textbox: passed
- Drag on small blue handle resizes textbox: passed
- Resize does not shift top-left position: passed
- Final one-click edit after move and resize: passed
- Font size retained during test: 18 px
- Browser page errors: 0
- Browser console errors: 0
- Python compilation: passed
- JavaScript syntax check: passed
- Preview-only authentication bypass: excluded from deployment package
- Private secrets.toml: excluded from deployment package
