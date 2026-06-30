# Deploy Login Native Form Stability Fix

Replace the repository-root files with this package and commit them together.
The sign-in page no longer uses the custom component. Username and password are native Streamlit widgets inside one `st.form`.
Reboot Streamlit and hard-refresh the browser after deployment.
