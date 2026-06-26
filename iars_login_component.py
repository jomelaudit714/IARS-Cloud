from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import streamlit as st


def _asset_data_uri(filename: str) -> str:
    path = Path(__file__).resolve().parent / "assets" / filename
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


LOGIN_HTML = r"""
<div class="login-shell">
  <section class="visual-panel" aria-label="EDL Internal Audit">
    <img id="login-visual" alt="EDL Internal Audit Report System" />
  </section>

  <section class="form-panel">
    <div class="form-wrap">
      <header class="form-header">
        <h1>Sign in to your account</h1>
        <p>Access your internal audit workspace</p>
      </header>

      <div class="field-group">
        <label for="username">Username</label>
        <input id="username" type="text" autocomplete="username" placeholder="Enter your username" />
      </div>

      <div class="field-group">
        <label for="password">Password</label>
        <div class="password-wrap">
          <input id="password" type="password" autocomplete="current-password" placeholder="Enter your password" />
          <button id="toggle-password" class="icon-button" type="button" aria-label="Show password">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Zm9.5 3.1a3.1 3.1 0 1 0 0-6.2 3.1 3.1 0 0 0 0 6.2Z"/></svg>
          </button>
        </div>
      </div>

      <div class="options-row">
        <label class="remember"><input id="remember" type="checkbox" /><span>Remember me</span></label>
        <button id="forgot" type="button" class="link-button">Forgot password?</button>
      </div>

      <button id="sign-in" type="button" class="primary-button">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a5 5 0 0 0-5 5v2H5.7A1.7 1.7 0 0 0 4 10.7v8.6A1.7 1.7 0 0 0 5.7 21h12.6a1.7 1.7 0 0 0 1.7-1.7v-8.6A1.7 1.7 0 0 0 18.3 9H17V7a5 5 0 0 0-5-5Zm-3 7V7a3 3 0 1 1 6 0v2H9Zm3 4a1.5 1.5 0 0 1 .8 2.77V18h-1.6v-2.23A1.5 1.5 0 0 1 12 13Z"/></svg>
        <span>Sign In</span>
      </button>

      <div class="divider"><span>or</span></div>

      <button id="sign-up" type="button" class="secondary-button">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 12a5 5 0 1 0-6 0c-4.2 1.1-7 4-7 8h2c0-3.4 3.4-6 8-6s8 2.6 8 6h2c0-4-2.8-6.9-7-8Zm-3-2a3 3 0 1 1 0-6 3 3 0 0 1 0 6Zm8-6v3h-3v2h3v3h2V9h3V7h-3V4h-2Z"/></svg>
        <span>Sign Up</span>
      </button>

      <button id="verify" type="button" class="verify-button">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 4 5v6c0 5.3 3.4 9.7 8 11 4.6-1.3 8-5.7 8-11V5l-8-3Zm0 2.1 6 2.2V11c0 4.1-2.4 7.6-6 8.8-3.6-1.2-6-4.7-6-8.8V6.3l6-2.2Zm-1.1 10.5-2.4-2.4-1.4 1.4 3.8 3.8 6-6-1.4-1.4-4.6 4.6Z"/></svg>
        <span>Verify Your Account</span>
      </button>

      <p class="authorized">Authorized EDL Internal Audit personnel only.</p>
      <p id="inline-error" class="inline-error" role="alert"></p>
    </div>
  </section>
</div>
"""


LOGIN_CSS = r"""
:host {
  display:block;
  width:100%;
  color:#061A36;
  font-family:Inter,"Segoe UI",Roboto,Arial,sans-serif;
}
* { box-sizing:border-box; }
button,input { font:inherit; }
.login-shell {
  width:100%;
  height:100dvh;
  min-height:0;
  overflow:hidden;
  display:grid;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  gap:10px;
  padding:4px;
  background:#F4F6FA;
}
.visual-panel,
.form-panel {
  min-width:0;
  min-height:0;
  height:calc(100dvh - 8px);
  border-radius:16px;
  overflow:hidden;
}
.visual-panel {
  background:#061A36;
  box-shadow:0 18px 44px rgba(6,26,54,.16);
}
.visual-panel img {
  width:100%;
  height:100%;
  display:block;
  object-fit:cover;
  object-position:center top;
}
.form-panel {
  display:flex;
  align-items:center;
  justify-content:center;
  background:#FFF;
  border:1px solid #DCE3EC;
  box-shadow:0 18px 44px rgba(16,24,40,.07);
  padding:clamp(18px,3.2vh,42px) clamp(28px,4.5vw,72px);
}
.form-wrap {
  width:min(100%,620px);
  margin:auto;
}
.form-header {
  text-align:center;
  margin:0 0 clamp(14px,2.4vh,28px);
}
.form-header h1 {
  margin:0;
  color:#061A36;
  font-size:clamp(28px,3.2vw,44px);
  line-height:1.07;
  font-weight:850;
  letter-spacing:-.035em;
}
.form-header p {
  margin:8px 0 0;
  color:#667085;
  font-size:clamp(14px,1.1vw,18px);
}
.field-group { margin-bottom:clamp(12px,2vh,20px); }
.field-group label {
  display:block;
  margin-bottom:7px;
  color:#061A36;
  font-size:15px;
  font-weight:750;
}
.field-group input {
  width:100%;
  height:clamp(46px,7vh,56px);
  border:1.5px solid #C8D2DF;
  border-radius:8px;
  background:#FFF;
  color:#061A36;
  outline:none;
  padding:0 18px;
  font-size:16px;
  transition:border-color .15s,box-shadow .15s;
}
.field-group input::placeholder { color:#98A2B3; }
.field-group input:focus {
  border-color:#174A86;
  box-shadow:0 0 0 4px rgba(23,74,134,.10);
}
.password-wrap { position:relative; }
.password-wrap input { padding-right:58px; }
.icon-button {
  position:absolute;
  right:10px;
  top:50%;
  transform:translateY(-50%);
  width:42px;
  height:42px;
  border:0;
  border-radius:8px;
  background:transparent;
  color:#344054;
  cursor:pointer;
  display:grid;
  place-items:center;
}
.icon-button:hover { background:#F2F4F7; }
.icon-button svg { width:23px;height:23px;fill:currentColor; }
.options-row {
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:16px;
  margin:0 0 clamp(12px,2vh,20px);
}
.remember {
  display:flex;
  align-items:center;
  gap:10px;
  color:#344054;
  font-size:16px;
  cursor:pointer;
}
.remember input {
  appearance:none;
  width:23px;
  height:23px;
  border:1.5px solid #B9C5D3;
  border-radius:5px;
  background:#FFF;
  display:grid;
  place-content:center;
  cursor:pointer;
}
.remember input:checked { background:#061A36;border-color:#061A36; }
.remember input:checked::after { content:"✓";color:#FFF;font-size:15px;font-weight:800; }
.link-button {
  border:0;
  background:transparent;
  color:#175CD3;
  font-size:16px;
  font-weight:650;
  cursor:pointer;
  padding:6px 0;
}
.primary-button,
.secondary-button {
  width:100%;
  height:clamp(48px,7vh,56px);
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:12px;
  font-size:17px;
  font-weight:780;
  cursor:pointer;
  transition:background .15s,border-color .15s,transform .08s;
}
.primary-button {
  color:#FFF;
  background:#061A36;
  border:1px solid #061A36;
}
.primary-button:hover { background:#0A2C59;border-color:#0A2C59; }
.primary-button:active,.secondary-button:active { transform:translateY(1px); }
.primary-button svg,.secondary-button svg,.verify-button svg {
  width:25px;
  height:25px;
  fill:currentColor;
}
.divider {
  display:flex;
  align-items:center;
  gap:18px;
  margin:clamp(10px,1.8vh,18px) 0;
  color:#667085;
  font-size:16px;
}
.divider::before,.divider::after { content:"";height:1px;background:#DCE3EC;flex:1; }
.secondary-button {
  color:#061A36;
  background:#FFF;
  border:2px solid #174A86;
}
.secondary-button:hover { background:#F7FAFD; }
.verify-button {
  width:100%;
  min-height:38px;
  margin-top:8px;
  border:0;
  background:transparent;
  color:#175CD3;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  font-size:18px;
  font-weight:780;
  cursor:pointer;
}
.verify-button:hover { color:#0B4DB8; }
.authorized {
  margin:clamp(8px,1.8vh,18px) 0 0;
  text-align:center;
  color:#667085;
  font-size:14px;
}
.inline-error {
  min-height:20px;
  margin:10px 0 0;
  color:#B42318;
  text-align:center;
  font-size:14px;
}
@media (max-height:720px) and (min-width:901px) {
  .login-shell { padding:6px; gap:8px; }
  .visual-panel,.form-panel { height:calc(100dvh - 12px); border-radius:14px; }
  .form-panel { padding:12px clamp(24px,4vw,56px); }
  .form-header { margin-bottom:12px; }
  .form-header h1 { font-size:30px; }
  .form-header p { margin-top:5px; font-size:14px; }
  .field-group { margin-bottom:10px; }
  .field-group label { margin-bottom:5px; font-size:14px; }
  .field-group input { height:44px; font-size:15px; }
  .options-row { margin-bottom:10px; }
  .remember,.link-button { font-size:14px; }
  .remember input { width:20px; height:20px; }
  .primary-button,.secondary-button { height:46px; font-size:16px; }
  .divider { margin:8px 0; font-size:14px; }
  .verify-button { margin-top:5px; min-height:32px; font-size:15px; }
  .authorized { margin-top:6px; font-size:12px; }
  .inline-error { min-height:14px; margin-top:4px; font-size:12px; }
}
@media (max-width:900px) {
  .login-shell { grid-template-columns:1fr; min-height:auto; }
  .visual-panel { min-height:440px; }
  .form-panel { min-height:auto;padding:38px 22px 44px; }
}
@media (max-width:560px) {
  .login-shell { padding:0;gap:0;background:#FFF; }
  .visual-panel,.form-panel { border-radius:0; }
  .visual-panel { min-height:360px; }
  .form-panel { border:0;box-shadow:none;padding:30px 18px 38px; }
  .form-header h1 { font-size:30px; }
  .options-row { align-items:flex-start; }
}
"""


LOGIN_JS = r"""
export default function (component) {
  const { data, parentElement, setStateValue, setTriggerValue } = component
  const $ = (selector) => parentElement.querySelector(selector)

  const visual = $("#login-visual")
  const username = $("#username")
  const password = $("#password")
  const remember = $("#remember")
  const toggle = $("#toggle-password")
  const error = $("#inline-error")
  if (!visual || !username || !password || !remember || !toggle || !error) return

  visual.src = data?.leftImage || ""
  username.value = data?.username || ""
  remember.checked = Boolean(data?.remember)

  username.oninput = (event) => setStateValue("username", event.target.value)
  password.oninput = (event) => setStateValue("password", event.target.value)
  remember.onchange = (event) => setStateValue("remember", event.target.checked)

  toggle.onclick = () => {
    const visible = password.type === "text"
    password.type = visible ? "password" : "text"
    toggle.setAttribute("aria-label", visible ? "Show password" : "Hide password")
  }

  const submit = () => {
    const user = username.value.trim()
    const pass = password.value
    if (!user || !pass) {
      error.textContent = "Enter your username and password."
      return
    }
    error.textContent = ""
    setTriggerValue("submit", {
      username: user,
      password: pass,
      remember: remember.checked,
      nonce: Date.now(),
    })
  }

  $("#sign-in").onclick = submit
  password.onkeydown = (event) => { if (event.key === "Enter") submit() }
  username.onkeydown = (event) => { if (event.key === "Enter") password.focus() }
  $("#forgot").onclick = () => setTriggerValue("forgot", Date.now())
  $("#sign-up").onclick = () => setTriggerValue("signup", Date.now())
  $("#verify").onclick = () => setTriggerValue("verify", Date.now())
}
"""


_EXACT_LOGIN = st.components.v2.component(
    "iars_exact_login_phase1",
    html=LOGIN_HTML,
    css=LOGIN_CSS,
    js=LOGIN_JS,
)


def render_exact_login(*, key: str = "iars_exact_login") -> Any:
    state = st.session_state.get(key, {})
    return _EXACT_LOGIN(
        key=key,
        data={
            "leftImage": _asset_data_uri("login_left_panel.png"),
            "username": state.get("username", ""),
            "remember": state.get("remember", False),
        },
        width="stretch",
        height="content",
        on_username_change=lambda: None,
        on_password_change=lambda: None,
        on_remember_change=lambda: None,
        on_submit_change=lambda: None,
        on_forgot_change=lambda: None,
        on_signup_change=lambda: None,
        on_verify_change=lambda: None,
    )


def apply_exact_login_host_css() -> None:
    st.markdown(
        """
        <style>
        html, body, #root, .stApp {
          height:100vh !important;
          min-height:0 !important;
          margin:0 !important;
          padding:0 !important;
          overflow:hidden !important;
        }
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"],
        .stAppDeployButton,
        #MainMenu,
        footer {display:none !important;}
        section[data-testid="stSidebar"] {display:none !important;}
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        .main,
        .main > div,
        .block-container {
          height:100vh !important;
          min-height:0 !important;
          max-width:none !important;
          padding:0 !important;
          margin:0 !important;
          overflow:hidden !important;
          background:#F4F6FA !important;
        }
        [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlock"] > div {
          gap:0 !important;
          margin:0 !important;
          padding:0 !important;
        }
        [data-testid="stCustomComponentV2"],
        [data-testid="stCustomComponentV2"] > div {
          height:100vh !important;
          min-height:0 !important;
          width:100% !important;
          margin:0 !important;
          padding:0 !important;
          overflow:hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
