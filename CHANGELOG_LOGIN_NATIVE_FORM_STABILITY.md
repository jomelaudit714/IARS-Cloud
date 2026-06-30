# Login Native Form Stability Fix

- Removed the interactive custom component from the sign-in page.
- Replaced it with a native Streamlit `st.form` so typing does not trigger reruns.
- Prevents username/password text from disappearing while typing.
- Avoids the custom-component WebSocket `CachedForwardMsg MISS` failure path.
- Retains the approved EDL split-screen login design and viewport-fit styling.
