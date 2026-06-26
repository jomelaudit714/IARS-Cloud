import streamlit as st
from iars_theme import apply_iars_theme, render_login_hero

st.set_page_config(page_title='IARS Login Preview', layout='wide', initial_sidebar_state='collapsed')
apply_iars_theme()
left, right = st.columns([1.03,0.97], gap='small', vertical_alignment='center')
with left:
    render_login_hero()
with right:
    with st.container(border=True, key='iars_auth_card'):
        st.markdown('<div class="edl-auth-title"><h1>Sign in to your account</h1><p>Access your internal audit workspace</p></div>', unsafe_allow_html=True)
        with st.form('preview_form'):
            st.text_input('Username', placeholder='Enter your username')
            st.text_input('Password', placeholder='Enter your password', type='password')
            c1,c2=st.columns([1,1])
            with c1: st.checkbox('Remember me')
            with c2: st.markdown('<div style="text-align:right;padding-top:.55rem;color:#175CD3;font-size:.9rem">Forgot password?</div>', unsafe_allow_html=True)
            st.form_submit_button('🔒  Sign In', type='primary', use_container_width=True)
        st.markdown('<div class="edl-auth-divider">or</div>', unsafe_allow_html=True)
        st.button('👤  Sign Up', use_container_width=True)
        st.button('🛡️  Verify Your Account', use_container_width=True)
