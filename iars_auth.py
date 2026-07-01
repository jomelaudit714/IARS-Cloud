from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import re
import secrets
from typing import Any

import streamlit as st

from iars_theme import render_brand_stripe, render_login_hero, render_section_header, render_sidebar_user, render_metric_cards


DEFAULT_USERS_TABLE = "iars_users"
DEFAULT_LOG_TABLE = "iars_auth_log"

SESSION_USER_ID = "iars_session_user_id"
SESSION_USERNAME = "iars_session_username"
SESSION_ROLE = "iars_session_role"
SESSION_LAST_ACTIVITY = "iars_session_last_activity"
ADMIN_LAST_CODE = "iars_admin_last_code"

PASSWORD_ITERATIONS = 310_000
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
MAX_CODE_ATTEMPTS = 5
ACTIVATION_CODE_HOURS = 24
RESET_CODE_MINUTES = 30


@dataclass(frozen=True)
class AuthConfig:
    url: str
    service_role_key: str
    users_table: str = DEFAULT_USERS_TABLE
    log_table: str = DEFAULT_LOG_TABLE
    admin_username: str = ""
    admin_password: str = ""
    admin_name: str = "IARS Administrator"
    code_secret: str = ""
    session_timeout_minutes: int = 30


def _secret_value(container: Any, key: str, default: str = "") -> str:
    try:
        value = container.get(key, default)
    except Exception:
        try:
            value = container[key]
        except Exception:
            value = default
    return str(value or "").strip()


def read_auth_config(secrets_container: Any) -> AuthConfig:
    """Read manual admin-code authentication settings from Streamlit Secrets."""
    supabase_section = {}
    admin_section = {}
    try:
        supabase_section = secrets_container.get("supabase", {})
        admin_section = secrets_container.get("iars_admin", {})
    except Exception:
        pass

    timeout_text = _secret_value(admin_section, "session_timeout_minutes", "30")
    try:
        timeout = max(5, min(480, int(timeout_text)))
    except ValueError:
        timeout = 30

    return AuthConfig(
        url=(
            _secret_value(supabase_section, "url")
            or _secret_value(secrets_container, "SUPABASE_URL")
        ),
        service_role_key=(
            _secret_value(supabase_section, "service_role_key")
            or _secret_value(secrets_container, "SUPABASE_SERVICE_ROLE_KEY")
        ),
        users_table=(
            _secret_value(admin_section, "users_table") or DEFAULT_USERS_TABLE
        ),
        log_table=(
            _secret_value(admin_section, "log_table") or DEFAULT_LOG_TABLE
        ),
        admin_username=_secret_value(admin_section, "username"),
        admin_password=_secret_value(admin_section, "password"),
        admin_name=(
            _secret_value(admin_section, "full_name") or "IARS Administrator"
        ),
        code_secret=_secret_value(admin_section, "code_secret"),
        session_timeout_minutes=timeout,
    )


def auth_is_configured(config: AuthConfig) -> bool:
    return bool(
        config.url
        and config.service_role_key
        and config.admin_username
        and config.admin_password
        and config.code_secret
    )


def create_auth_client(config: AuthConfig):
    if not auth_is_configured(config):
        raise RuntimeError("IARS account authentication is not configured.")
    from supabase import create_client

    return create_client(config.url, config.service_role_key)


def _response_rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _parse_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def normalize_username(value: str) -> str:
    username = str(value or "").strip().lower()
    username = re.sub(r"\s+", "", username)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,29}", username):
        raise ValueError(
            "Username must be 3–30 characters and may contain letters, numbers, periods, underscores, or hyphens."
        )
    return username


def clean_full_name(value: str) -> str:
    name = " ".join(str(value or "").split()).strip()
    if len(name) < 3:
        raise ValueError("Enter the user's full name.")
    return name[:150]


def clean_contact_number(value: str) -> str:
    """Keep contact number as optional profile information; it is not used for login."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    cleaned = re.sub(r"[^0-9+]", "", raw)
    if len(re.sub(r"\D", "", cleaned)) < 7:
        raise ValueError("Enter a valid contact number or leave it blank.")
    return cleaned[:30]


def validate_password(password: str, confirmation: str | None = None) -> str:
    password = str(password or "")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise ValueError("Password must contain at least one letter and one number.")
    if confirmation is not None and password != confirmation:
        raise ValueError("Passwords do not match.")
    return password


def _new_password_parts(password: str) -> tuple[str, str]:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return base64.b64encode(salt).decode("ascii"), base64.b64encode(digest).decode("ascii")


def _password_matches(password: str, salt_b64: str, expected_b64: str) -> bool:
    try:
        salt = base64.b64decode(str(salt_b64 or ""), validate=True)
        expected = base64.b64decode(str(expected_b64 or ""), validate=True)
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", str(password or "").encode("utf-8"), salt, PASSWORD_ITERATIONS
    )
    return hmac.compare_digest(actual, expected)


def _code_hash(config: AuthConfig, user_id: str, purpose: str, code: str) -> str:
    message = f"{purpose}:{user_id}:{code}".encode("utf-8")
    return hmac.new(config.code_secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def _new_code(config: AuthConfig, user_id: str, purpose: str) -> tuple[str, str]:
    code = f"{secrets.randbelow(900000) + 100000:06d}"
    return code, _code_hash(config, user_id, purpose, code)


def _fetch_user(client: Any, config: AuthConfig, username: str) -> dict[str, Any] | None:
    response = (
        client.table(config.users_table)
        .select("*")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    rows = _response_rows(response)
    return rows[0] if rows else None


def _fetch_user_by_id(client: Any, config: AuthConfig, user_id: str) -> dict[str, Any] | None:
    response = (
        client.table(config.users_table)
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    rows = _response_rows(response)
    return rows[0] if rows else None


def _list_users(client: Any, config: AuthConfig) -> list[dict[str, Any]]:
    response = (
        client.table(config.users_table)
        .select("*")
        .order("created_at", desc=True)
        .limit(1000)
        .execute()
    )
    return _response_rows(response)


def _update_user(client: Any, config: AuthConfig, user_id: str, values: dict[str, Any]) -> None:
    values = {**values, "updated_at": _iso(_utc_now())}
    client.table(config.users_table).update(values).eq("id", user_id).execute()


def _log_event(
    client: Any,
    config: AuthConfig,
    *,
    event_type: str,
    username: str = "",
    user_id: str | None = None,
    success: bool = True,
    details: str = "",
) -> None:
    try:
        client.table(config.log_table).insert(
            {
                "event_type": event_type,
                "username": str(username or "")[:60],
                "user_id": user_id,
                "success": bool(success),
                "details": str(details or "")[:500],
            }
        ).execute()
    except Exception:
        # Login must remain available even if the optional log table is unavailable.
        pass


def _set_session(user: dict[str, Any]) -> None:
    st.session_state[SESSION_USER_ID] = str(user.get("id", ""))
    st.session_state[SESSION_USERNAME] = str(user.get("username", ""))
    st.session_state[SESSION_ROLE] = str(user.get("role", "user"))
    st.session_state[SESSION_LAST_ACTIVITY] = _iso(_utc_now())
    # Show a short full-screen mask during the first authenticated rerun.
    # This prevents stale login widgets from remaining visible while the
    # dashboard DOM is being reconciled by Streamlit.
    st.session_state["iars_show_login_exit_mask"] = True


def clear_auth_session() -> None:
    for key in (
        SESSION_USER_ID,
        SESSION_USERNAME,
        SESSION_ROLE,
        SESSION_LAST_ACTIVITY,
        ADMIN_LAST_CODE,
    ):
        st.session_state.pop(key, None)


def is_admin_user(user: Any) -> bool:
    return bool(isinstance(user, dict) and user.get("role") == "admin")


def user_display_name(user: Any) -> str:
    if not isinstance(user, dict):
        return "IARS User"
    return str(user.get("full_name") or user.get("username") or "IARS User").strip()


def user_username(user: Any) -> str:
    if not isinstance(user, dict):
        return ""
    return str(user.get("username") or "").strip()


def restore_auth_session(client: Any, config: AuthConfig) -> dict[str, Any] | None:
    user_id = str(st.session_state.get(SESSION_USER_ID, "") or "")
    username = str(st.session_state.get(SESSION_USERNAME, "") or "")
    role = str(st.session_state.get(SESSION_ROLE, "") or "")
    last_activity = _parse_datetime(st.session_state.get(SESSION_LAST_ACTIVITY))

    if not user_id or not username or not role or last_activity is None:
        return None

    if _utc_now() - last_activity > timedelta(minutes=config.session_timeout_minutes):
        clear_auth_session()
        return None

    st.session_state[SESSION_LAST_ACTIVITY] = _iso(_utc_now())

    if role == "admin":
        if username != config.admin_username.casefold():
            clear_auth_session()
            return None
        return {
            "id": "admin",
            "username": config.admin_username.casefold(),
            "full_name": config.admin_name,
            "role": "admin",
            "status": "Active",
        }

    user = _fetch_user_by_id(client, config, user_id)
    if not user or str(user.get("status", "")) != "Active":
        clear_auth_session()
        return None
    user["role"] = "user"
    return user


def _render_setup_notice() -> None:
    st.error("IARS account login is not configured yet.")
    st.markdown(
        "Run `SUPABASE_USER_AUTH_SETUP.sql`, then configure one administrator account "
        "in Streamlit Secrets. SMS and Supabase Phone Auth are not required."
    )
    st.code(
        '[supabase]\n'
        'url = "https://YOUR-PROJECT.supabase.co"\n'
        'service_role_key = "YOUR-SERVICE-ROLE-KEY"\n\n'
        '[iars_admin]\n'
        'username = "jomel"\n'
        'password = "USE-A-STRONG-PASSWORD"\n'
        'full_name = "Jomel Santiago"\n'
        'code_secret = "USE-A-LONG-RANDOM-SECRET"\n'
        'session_timeout_minutes = 30',
        language="toml",
    )


def _process_sign_in_credentials(
    client: Any,
    config: AuthConfig,
    username_input: str,
    password: str,
) -> None:
    username = normalize_username(username_input)
    if username == config.admin_username.casefold():
        if not hmac.compare_digest(password, config.admin_password):
            _log_event(client, config, event_type="admin_sign_in", username=username, success=False)
            raise ValueError("Incorrect username or password.")
        admin_user = {
            "id": "admin",
            "username": username,
            "full_name": config.admin_name,
            "role": "admin",
            "status": "Active",
        }
        _set_session(admin_user)
        _log_event(client, config, event_type="admin_sign_in", username=username, success=True)
        st.success("Administrator signed in successfully.")
        st.rerun()

    user = _fetch_user(client, config, username)
    if not user:
        _log_event(client, config, event_type="user_sign_in", username=username, success=False)
        raise ValueError("Incorrect username or password.")

    status = str(user.get("status", "") or "")
    if status == "Pending":
        raise ValueError("Your registration is waiting for administrator approval.")
    if status == "Code Issued":
        raise ValueError("Your activation code is ready. Open Verify Account to activate your account.")
    if status == "Suspended":
        raise ValueError("Your account is suspended. Contact the administrator.")
    if status == "Deactivated":
        raise ValueError("Your account is deactivated. Contact the administrator.")
    if status != "Active":
        raise ValueError("Your account is not active.")

    locked_until = _parse_datetime(user.get("locked_until"))
    if locked_until and locked_until > _utc_now():
        remaining = max(1, int((locked_until - _utc_now()).total_seconds() // 60) + 1)
        raise ValueError(f"Too many failed attempts. Try again in about {remaining} minute(s).")

    if not _password_matches(
        password, str(user.get("password_salt", "")), str(user.get("password_hash", ""))
    ):
        attempts = int(user.get("failed_login_attempts") or 0) + 1
        update: dict[str, Any] = {"failed_login_attempts": attempts}
        if attempts >= MAX_LOGIN_ATTEMPTS:
            update["locked_until"] = _iso(_utc_now() + timedelta(minutes=LOCKOUT_MINUTES))
            update["failed_login_attempts"] = 0
        _update_user(client, config, str(user["id"]), update)
        _log_event(
            client,
            config,
            event_type="user_sign_in",
            username=username,
            user_id=str(user.get("id")),
            success=False,
        )
        raise ValueError("Incorrect username or password.")

    _update_user(
        client,
        config,
        str(user["id"]),
        {
            "failed_login_attempts": 0,
            "locked_until": None,
            "last_login_at": _iso(_utc_now()),
        },
    )
    _set_session(user)
    _log_event(
        client,
        config,
        event_type="user_sign_in",
        username=username,
        user_id=str(user.get("id")),
        success=True,
    )
    st.success("Signed in successfully.")
    st.rerun()


def _set_auth_view(view: str) -> None:
    """Switch the visible account panel during the button-triggered rerun.

    Using a callback avoids the second explicit st.rerun() that previously caused
    a visible flash between Sign In, Sign Up, Verify, and Forgot Password.
    """
    st.session_state["iars_auth_view"] = view
    try:
        if "auth_view" in st.query_params:
            del st.query_params["auth_view"]
    except Exception:
        pass


def _render_sign_in(client: Any, config: AuthConfig) -> None:
    """Render the approved sign-in interface with stable native controls.

    All typing remains inside the browser until a form button is pressed.
    This avoids per-keystroke reruns and CachedForwardMsg errors.
    """
    with st.form("iars_native_sign_in_form", clear_on_submit=False, border=False):
        username_input = st.text_input(
            "Username",
            placeholder="Enter your username",
            autocomplete="username",
            key="auth_signin_username",
        )
        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
            autocomplete="current-password",
            key="auth_signin_password",
        )

        remember_col, forgot_col = st.columns([1, 1], vertical_alignment="center")
        with remember_col:
            remember = st.checkbox("Remember me", key="auth_remember_me")
        with forgot_col:
            forgot_clicked = st.form_submit_button(
                "Forgot password?",
                key="auth_forgot_submit",
                type="tertiary",
                use_container_width=True,
            )

        submitted = st.form_submit_button(
            "Sign In",
            key="auth_signin_submit",
            type="primary",
            icon=":material/lock:",
            use_container_width=True,
        )

    if forgot_clicked:
        _set_auth_view("forgot")
        st.rerun()

    if not submitted:
        return

    _ = remember
    try:
        _process_sign_in_credentials(client, config, username_input, password)
    except Exception as exc:
        st.error(str(exc) or "Unable to sign in.")

def _render_sign_up(client: Any, config: AuthConfig) -> None:
    st.caption(
        "Create a standard user account. The administrator must approve it and personally provide the activation code."
    )
    with st.form("iars_manual_sign_up_form"):
        full_name = st.text_input("Full Name", placeholder="Sarina Amuraw")
        username_input = st.text_input(
            "Username / Nickname",
            placeholder="sar",
            help="This is your login name. Do not use your contact number.",
        )
        contact_number = st.text_input(
            "Contact Number (optional)",
            placeholder="09171234567",
            help="Stored only as profile information. No SMS will be sent.",
        )
        password = st.text_input(
            "Password",
            type="password",
            autocomplete="new-password",
            help="At least 8 characters with at least one letter and one number.",
        )
        confirmation = st.text_input(
            "Confirm Password", type="password", autocomplete="new-password"
        )
        submitted = st.form_submit_button("Submit Registration", type="primary", use_container_width=True)

    if not submitted:
        return

    try:
        name = clean_full_name(full_name)
        username = normalize_username(username_input)
        if username == config.admin_username.casefold():
            raise ValueError("This username is reserved for the administrator.")
        contact = clean_contact_number(contact_number)
        validate_password(password, confirmation)
        if _fetch_user(client, config, username):
            raise ValueError("That username is already registered. Choose another nickname.")
        salt, password_hash = _new_password_parts(password)
        response = client.table(config.users_table).insert(
            {
                "full_name": name,
                "username": username,
                "contact_number": contact,
                "password_salt": salt,
                "password_hash": password_hash,
                "status": "Pending",
            }
        ).execute()
        rows = _response_rows(response)
        user_id = str(rows[0].get("id", "")) if rows else None
        _log_event(
            client,
            config,
            event_type="registration_submitted",
            username=username,
            user_id=user_id,
            success=True,
        )
        st.success(
            "Registration submitted. Ask the IARS administrator to approve the account and give you the activation code."
        )
    except Exception as exc:
        st.error(str(exc) or "Registration could not be completed.")


def _render_verify_account(client: Any, config: AuthConfig) -> None:
    st.caption("Enter the one-time activation code personally provided by the administrator.")
    with st.form("iars_manual_verify_form"):
        username_input = st.text_input("Username / Nickname", key="verify_username")
        code_input = st.text_input(
            "Activation Code", max_chars=6, placeholder="123456", type="password"
        )
        submitted = st.form_submit_button("Verify Account", type="primary", use_container_width=True)

    if not submitted:
        return

    try:
        username = normalize_username(username_input)
        code = re.sub(r"\D", "", str(code_input or ""))
        if len(code) != 6:
            raise ValueError("Enter the six-digit activation code.")
        user = _fetch_user(client, config, username)
        if not user or str(user.get("status", "")) != "Code Issued":
            raise ValueError("No active verification code is available for this username.")
        expiry = _parse_datetime(user.get("activation_code_expires_at"))
        if expiry is None or expiry < _utc_now():
            raise ValueError("The activation code has expired. Ask the administrator for a new code.")
        attempts = int(user.get("activation_attempts") or 0)
        if attempts >= MAX_CODE_ATTEMPTS:
            raise ValueError("Too many incorrect attempts. Ask the administrator for a new code.")
        expected = str(user.get("activation_code_hash", "") or "")
        actual = _code_hash(config, str(user["id"]), "activate", code)
        if not hmac.compare_digest(actual, expected):
            _update_user(
                client,
                config,
                str(user["id"]),
                {"activation_attempts": attempts + 1},
            )
            _log_event(
                client,
                config,
                event_type="activation_failed",
                username=username,
                user_id=str(user.get("id")),
                success=False,
            )
            raise ValueError("The activation code is incorrect.")
        _update_user(
            client,
            config,
            str(user["id"]),
            {
                "status": "Active",
                "activation_code_hash": "",
                "activation_code_expires_at": None,
                "activation_attempts": 0,
                "activated_at": _iso(_utc_now()),
            },
        )
        _log_event(
            client,
            config,
            event_type="account_activated",
            username=username,
            user_id=str(user.get("id")),
            success=True,
        )
        st.success("Account verified. You may now sign in using your username and password.")
    except Exception as exc:
        st.error(str(exc) or "Account verification failed.")


def _render_forgot_password(client: Any, config: AuthConfig) -> None:
    st.caption(
        "Request a reset, then obtain a one-time reset code directly from the administrator. No SMS is used."
    )

    with st.form("iars_password_reset_request_form"):
        request_username_input = st.text_input(
            "Username / Nickname", key="reset_request_username"
        )
        request_submitted = st.form_submit_button(
            "Request Password Reset", use_container_width=True
        )
    if request_submitted:
        try:
            username = normalize_username(request_username_input)
            user = _fetch_user(client, config, username)
            if user and str(user.get("status", "")) == "Active":
                _update_user(client, config, str(user["id"]), {"reset_requested": True})
                _log_event(
                    client,
                    config,
                    event_type="password_reset_requested",
                    username=username,
                    user_id=str(user.get("id")),
                    success=True,
                )
            st.success(
                "Request submitted. Contact the administrator for the reset code if the username is registered."
            )
        except Exception as exc:
            st.error(str(exc) or "The request could not be submitted.")

    st.divider()
    with st.form("iars_password_reset_complete_form"):
        username_input = st.text_input("Username / Nickname", key="reset_complete_username")
        code_input = st.text_input(
            "Administrator Reset Code", max_chars=6, placeholder="123456", type="password"
        )
        new_password = st.text_input(
            "New Password", type="password", autocomplete="new-password"
        )
        confirmation = st.text_input(
            "Confirm New Password", type="password", autocomplete="new-password"
        )
        submitted = st.form_submit_button(
            "Change Password", type="primary", use_container_width=True
        )

    if not submitted:
        return

    try:
        username = normalize_username(username_input)
        code = re.sub(r"\D", "", str(code_input or ""))
        if len(code) != 6:
            raise ValueError("Enter the six-digit reset code.")
        validate_password(new_password, confirmation)
        user = _fetch_user(client, config, username)
        if not user or str(user.get("status", "")) != "Active":
            raise ValueError("No active password-reset code is available for this username.")
        expiry = _parse_datetime(user.get("reset_code_expires_at"))
        if expiry is None or expiry < _utc_now():
            raise ValueError("The reset code has expired. Ask the administrator for a new code.")
        attempts = int(user.get("reset_attempts") or 0)
        if attempts >= MAX_CODE_ATTEMPTS:
            raise ValueError("Too many incorrect attempts. Ask the administrator for a new code.")
        expected = str(user.get("reset_code_hash", "") or "")
        actual = _code_hash(config, str(user["id"]), "reset", code)
        if not hmac.compare_digest(actual, expected):
            _update_user(
                client,
                config,
                str(user["id"]),
                {"reset_attempts": attempts + 1},
            )
            _log_event(
                client,
                config,
                event_type="password_reset_failed",
                username=username,
                user_id=str(user.get("id")),
                success=False,
            )
            raise ValueError("The reset code is incorrect.")
        salt, password_hash = _new_password_parts(new_password)
        _update_user(
            client,
            config,
            str(user["id"]),
            {
                "password_salt": salt,
                "password_hash": password_hash,
                "reset_requested": False,
                "reset_code_hash": "",
                "reset_code_expires_at": None,
                "reset_attempts": 0,
                "failed_login_attempts": 0,
                "locked_until": None,
            },
        )
        _log_event(
            client,
            config,
            event_type="password_reset_completed",
            username=username,
            user_id=str(user.get("id")),
            success=True,
        )
        st.success("Password changed successfully. Sign in using the new password.")
    except Exception as exc:
        st.error(str(exc) or "Password reset failed.")


def render_auth_gate(config: AuthConfig):
    """Require username/password authentication before rendering IARS."""

    def _render_native_shell(render_right) -> None:
        st.markdown('<div class="iars-login-marker"></div>', unsafe_allow_html=True)
        with st.container(key="iars_login_shell"):
            left, right = st.columns([1, 1], gap="small", vertical_alignment="top")
            with left:
                render_login_hero()
            with right:
                with st.container(key="iars_auth_card"):
                    # Animate only the account panel. The branded left panel stays
                    # visually fixed during account-view changes.
                    st.markdown('<div class="iars-auth-view-marker"></div>', unsafe_allow_html=True)
                    render_right()

    if not auth_is_configured(config):
        def _setup_panel() -> None:
            render_section_header(
                "Account Setup Required",
                "Complete the administrator and Supabase configuration before opening IARS.",
                badge="Configuration",
            )
            _render_setup_notice()
        _render_native_shell(_setup_panel)
        st.stop()

    try:
        client = create_auth_client(config)
        user = restore_auth_session(client, config)
    except Exception as exc:
        def _error_panel() -> None:
            render_section_header(
                "Unable to Start Login",
                "The account service could not be initialized.",
                badge="Connection Error",
            )
            st.error(f"Unable to initialize IARS account login: {exc}")
            st.info("Run SUPABASE_USER_AUTH_SETUP.sql and verify the Streamlit Secrets values.")
        _render_native_shell(_error_panel)
        st.stop()

    if user is not None:
        if st.session_state.pop("iars_show_login_exit_mask", False):
            st.markdown(
                '<div class="iars-login-exit-mask">'
                '<div class="iars-login-exit-card">'
                '<div class="iars-login-exit-spinner"></div>'
                '<strong>Opening IARS</strong><span>Loading your audit workspace…</span>'
                '</div></div>',
                unsafe_allow_html=True,
            )
        return client, user

    requested_view = str(st.query_params.get("auth_view", "") or "").strip()
    if requested_view in {"sign_in", "sign_up", "verify", "forgot"}:
        st.session_state["iars_auth_view"] = requested_view
    view = st.session_state.get("iars_auth_view", "sign_in")

    def _auth_panel() -> None:
        if view == "sign_in":
            st.markdown(
                '<div class="iars-signin-view"></div>'
                '<div class="edl-auth-title"><h1>Sign in to your account</h1>'
                '<p>Access your internal audit workspace</p></div>',
                unsafe_allow_html=True,
            )
            _render_sign_in(client, config)
            st.markdown('<div class="edl-auth-divider">or</div>', unsafe_allow_html=True)
            # Use dedicated HTML actions instead of Streamlit buttons so the
            # approved border, icon, width, and link treatment cannot be changed
            # by Streamlit's generated button markup or older button selectors.
            st.markdown(
                """
                <div class="iars-login-actions" data-iars-build="4.4.1-deployment-fixed">
                  <a class="iars-signup-action" href="?auth_view=sign_up" target="_self" aria-label="Sign Up">
                    <span class="iars-signup-icon" aria-hidden="true"></span>
                    <span class="iars-signup-label">Sign Up</span>
                  </a>
                  <a class="iars-verify-action" href="?auth_view=verify" target="_self" aria-label="Verify Your Account">
                    <span class="iars-verify-icon" aria-hidden="true"></span>
                    <span class="iars-verify-label">Verify Your Account</span>
                  </a>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="edl-login-authorized">Authorized EDL Internal Audit personnel only.</div>',
                unsafe_allow_html=True,
            )
        elif view == "sign_up":
            st.markdown('<div class="iars-signup-view"></div>', unsafe_allow_html=True)
            render_section_header("Sign Up", "Register using only the essential account details.")
            _render_sign_up(client, config)
            st.button(
                "← Back to Sign In",
                key="auth_back_signup",
                use_container_width=True,
                on_click=_set_auth_view,
                args=("sign_in",),
            )
        elif view == "verify":
            st.markdown('<div class="iars-verify-view"></div>', unsafe_allow_html=True)
            render_section_header("Verify Account", "Enter the activation code personally provided by the administrator.")
            _render_verify_account(client, config)
            st.button(
                "← Back to Sign In",
                key="auth_back_verify",
                use_container_width=True,
                on_click=_set_auth_view,
                args=("sign_in",),
            )
        else:
            st.markdown('<div class="iars-forgot-view"></div>', unsafe_allow_html=True)
            render_section_header("Forgot Password", "Request or complete an administrator-approved password reset.")
            _render_forgot_password(client, config)
            st.button(
                "← Back to Sign In",
                key="auth_back_forgot",
                use_container_width=True,
                on_click=_set_auth_view,
                args=("sign_in",),
            )

    _render_native_shell(_auth_panel)
    st.stop()

def _user_label(user: dict[str, Any]) -> str:
    return f"{user.get('full_name', '')} (@{user.get('username', '')})"


def _render_admin_controls(client: Any, config: AuthConfig) -> None:
    try:
        users = _list_users(client, config)
    except Exception as exc:
        st.error(f"Unable to load user accounts: {exc}")
        return

    pending = [u for u in users if str(u.get("status")) == "Pending"]
    code_issued = [u for u in users if str(u.get("status")) == "Code Issued"]
    reset_requests = [u for u in users if bool(u.get("reset_requested"))]
    active = [u for u in users if str(u.get("status")) == "Active"]
    suspended = [u for u in users if str(u.get("status")) == "Suspended"]

    st.caption(
        f"Pending: {len(pending)} · Code issued: {len(code_issued)} · "
        f"Active: {len(active)} · Reset requests: {len(reset_requests)}"
    )

    if pending:
        labels = {_user_label(u): u for u in pending}
        selected_label = st.selectbox(
            "Pending registration", list(labels), key="admin_pending_user"
        )
        if st.button("Approve and Generate Activation Code", use_container_width=True):
            user = labels[selected_label]
            code, code_hash = _new_code(config, str(user["id"]), "activate")
            _update_user(
                client,
                config,
                str(user["id"]),
                {
                    "status": "Code Issued",
                    "activation_code_hash": code_hash,
                    "activation_code_expires_at": _iso(
                        _utc_now() + timedelta(hours=ACTIVATION_CODE_HOURS)
                    ),
                    "activation_attempts": 0,
                    "approved_at": _iso(_utc_now()),
                    "approved_by": config.admin_username,
                },
            )
            st.session_state[ADMIN_LAST_CODE] = {
                "purpose": "Activation",
                "username": user.get("username"),
                "full_name": user.get("full_name"),
                "code": code,
                "expires": f"{ACTIVATION_CODE_HOURS} hours",
            }
            _log_event(
                client,
                config,
                event_type="activation_code_issued",
                username=str(user.get("username", "")),
                user_id=str(user.get("id")),
                success=True,
                details=f"Issued by {config.admin_username}",
            )
            st.rerun()
    else:
        st.caption("No pending registrations.")

    if code_issued:
        labels = {_user_label(u): u for u in code_issued}
        selected_label = st.selectbox(
            "Reissue activation code", list(labels), key="admin_reissue_user"
        )
        if st.button("Generate New Activation Code", use_container_width=True):
            user = labels[selected_label]
            code, code_hash = _new_code(config, str(user["id"]), "activate")
            _update_user(
                client,
                config,
                str(user["id"]),
                {
                    "activation_code_hash": code_hash,
                    "activation_code_expires_at": _iso(
                        _utc_now() + timedelta(hours=ACTIVATION_CODE_HOURS)
                    ),
                    "activation_attempts": 0,
                },
            )
            st.session_state[ADMIN_LAST_CODE] = {
                "purpose": "Activation",
                "username": user.get("username"),
                "full_name": user.get("full_name"),
                "code": code,
                "expires": f"{ACTIVATION_CODE_HOURS} hours",
            }
            st.rerun()

    if reset_requests:
        labels = {_user_label(u): u for u in reset_requests}
        selected_label = st.selectbox(
            "Password-reset request", list(labels), key="admin_reset_user"
        )
        if st.button("Generate Password Reset Code", use_container_width=True):
            user = labels[selected_label]
            code, code_hash = _new_code(config, str(user["id"]), "reset")
            _update_user(
                client,
                config,
                str(user["id"]),
                {
                    "reset_code_hash": code_hash,
                    "reset_code_expires_at": _iso(
                        _utc_now() + timedelta(minutes=RESET_CODE_MINUTES)
                    ),
                    "reset_attempts": 0,
                },
            )
            st.session_state[ADMIN_LAST_CODE] = {
                "purpose": "Password Reset",
                "username": user.get("username"),
                "full_name": user.get("full_name"),
                "code": code,
                "expires": f"{RESET_CODE_MINUTES} minutes",
            }
            _log_event(
                client,
                config,
                event_type="reset_code_issued",
                username=str(user.get("username", "")),
                user_id=str(user.get("id")),
                success=True,
                details=f"Issued by {config.admin_username}",
            )
            st.rerun()
    else:
        st.caption("No password-reset requests.")

    last_code = st.session_state.get(ADMIN_LAST_CODE)
    if isinstance(last_code, dict) and last_code.get("code"):
        st.success(
            f"{last_code.get('purpose')} code for {last_code.get('full_name')} "
            f"(@{last_code.get('username')})"
        )
        st.code(str(last_code.get("code")))
        st.caption(f"Valid for {last_code.get('expires')}. Give it directly to the user.")
        if st.button("Hide Code", key="admin_hide_code", use_container_width=True):
            st.session_state.pop(ADMIN_LAST_CODE, None)
            st.rerun()

    manage_candidates = active + suspended
    if manage_candidates:
        st.divider()
        labels = {_user_label(u): u for u in manage_candidates}
        selected_label = st.selectbox(
            "Manage existing account", list(labels), key="admin_manage_user"
        )
        user = labels[selected_label]
        current_status = str(user.get("status", ""))
        st.caption(f"Current status: {current_status}")
        left, right = st.columns(2)
        with left:
            if current_status == "Active" and st.button(
                "Suspend", key="admin_suspend", use_container_width=True
            ):
                _update_user(client, config, str(user["id"]), {"status": "Suspended"})
                clear = st.session_state.pop(ADMIN_LAST_CODE, None)
                _ = clear
                st.rerun()
            if current_status == "Suspended" and st.button(
                "Reactivate", key="admin_reactivate", use_container_width=True
            ):
                _update_user(client, config, str(user["id"]), {"status": "Active"})
                st.rerun()
        with right:
            if st.button("Deactivate", key="admin_deactivate", use_container_width=True):
                _update_user(client, config, str(user["id"]), {"status": "Deactivated"})
                st.rerun()


def render_account_admin_page(client: Any, config: AuthConfig) -> None:
    """Render administrator account controls as a full application page."""
    try:
        users = _list_users(client, config)
    except Exception as exc:
        st.error(f"Unable to load user accounts: {exc}")
        return

    pending = [u for u in users if str(u.get("status")) == "Pending"]
    active = [u for u in users if str(u.get("status")) == "Active"]
    suspended = [u for u in users if str(u.get("status")) == "Suspended"]
    reset_requests = [u for u in users if bool(u.get("reset_requested"))]
    render_metric_cards([
        {"label": "Pending Approval", "value": len(pending), "note": "New registrations", "icon": "⏳", "accent": "#C78B12"},
        {"label": "Active Users", "value": len(active), "note": "Approved accounts", "icon": "👥", "accent": "#178A52"},
        {"label": "Suspended", "value": len(suspended), "note": "Restricted accounts", "icon": "⛔", "accent": "#D92D20"},
        {"label": "Reset Requests", "value": len(reset_requests), "note": "Awaiting admin action", "icon": "🔑", "accent": "#2563EB"},
    ])
    with st.container(border=True):
        _render_admin_controls(client, config)


def render_account_sidebar(
    client: Any, user: dict[str, Any], config: AuthConfig
) -> None:
    """Render a compact signed-in user card and sign-out action."""
    render_sidebar_user(user)
    username = user_username(user)
    if st.button("Sign Out", key="iars_sign_out", use_container_width=True):
        _log_event(
            client,
            config,
            event_type="sign_out",
            username=username,
            user_id=None if is_admin_user(user) else str(user.get("id", "")),
            success=True,
        )
        clear_auth_session()
        st.rerun()
