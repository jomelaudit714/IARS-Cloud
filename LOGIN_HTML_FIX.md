# IARS v3.9.1 Login HTML Fix

The login hero is now rendered through `st.html()` with a fully unindented HTML fragment. This prevents Streamlit Markdown from displaying the inner login markup as a gray code block.

Replace `iars_theme.py` and reboot the app. The package also bumps the visible interface version to v3.9.1.
