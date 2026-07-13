from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import re
import secrets
from typing import Any
from io import BytesIO

import streamlit as st

# V4.4.39: Avatar drag editor using Streamlit Components v2, same pattern as PDF Tagging.
st_cropper = None

from iars_theme import render_brand_stripe, render_login_hero, render_section_header, render_sidebar_user, render_metric_cards, render_transition_guard


DEFAULT_USERS_TABLE = "iars_users"
DEFAULT_LOG_TABLE = "iars_auth_log"
DEFAULT_PROFILE_TABLE = "iars_profiles"
DEFAULT_PROFILE_BUCKET = "iars-profile-pictures"

SESSION_USER_ID = "iars_session_user_id"
SESSION_USERNAME = "iars_session_username"
SESSION_ROLE = "iars_session_role"
SESSION_LAST_ACTIVITY = "iars_session_last_activity"
SESSION_USER_CACHE = "iars_session_user_cache"
SESSION_CACHE_LOADED_AT = "iars_session_cache_loaded_at"
PERSISTENT_AUTH_PARAM = "iars_session"
SIGN_OUT_PARAM = "iars_sign_out"
PERSISTENT_AUTH_REMEMBER_DAYS = 7
AUTH_CACHE_SECONDS = 300
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
    profile_table: str = DEFAULT_PROFILE_TABLE
    profile_bucket: str = DEFAULT_PROFILE_BUCKET
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
        profile_table=(
            _secret_value(admin_section, "profile_table") or DEFAULT_PROFILE_TABLE
        ),
        profile_bucket=(
            _secret_value(admin_section, "profile_bucket") or DEFAULT_PROFILE_BUCKET
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


def _profile_error_text(exc: Exception) -> str:
    text = " ".join(str(exc or "").split()).strip()
    return text[:500] or exc.__class__.__name__


def _fetch_profile(client: Any, config: AuthConfig, user_id: str) -> dict[str, Any]:
    """Return optional editable-profile overrides without blocking login if setup is pending."""
    try:
        response = (
            client.table(config.profile_table)
            .select("*")
            .eq("user_id", str(user_id))
            .limit(1)
            .execute()
        )
        rows = _response_rows(response)
        return rows[0] if rows else {}
    except Exception:
        return {}


def _upsert_profile(client: Any, config: AuthConfig, user_id: str, values: dict[str, Any]) -> None:
    payload = {"user_id": str(user_id), **values, "updated_at": _iso(_utc_now())}
    try:
        client.table(config.profile_table).upsert(payload, on_conflict="user_id").execute()
    except Exception as exc:
        detail = _profile_error_text(exc)
        raise ValueError(
            f"Unable to save profile settings in '{config.profile_table}': {detail}. "
            "Run the updated SUPABASE_PROFILE_SETUP.sql, then refresh the app."
        ) from exc


def _profile_storage_diagnostics(client: Any, config: AuthConfig) -> dict[str, Any]:
    result = {
        "table_ready": False,
        "bucket_ready": False,
        "table_error": "",
        "bucket_error": "",
    }
    try:
        client.table(config.profile_table).select("user_id,profile_picture_path").limit(1).execute()
        result["table_ready"] = True
    except Exception as exc:
        result["table_error"] = _profile_error_text(exc)

    try:
        storage = client.storage
        if hasattr(storage, "get_bucket"):
            storage.get_bucket(config.profile_bucket)
        else:
            buckets = storage.list_buckets()
            names = {
                str(getattr(bucket, "name", "") or (bucket.get("name") if isinstance(bucket, dict) else ""))
                for bucket in (buckets or [])
            }
            if config.profile_bucket not in names:
                raise RuntimeError(f"Bucket '{config.profile_bucket}' was not found")
        result["bucket_ready"] = True
    except Exception as exc:
        result["bucket_error"] = _profile_error_text(exc)
    return result


def _profile_picture_image(uploaded_file: Any) -> Any:
    if uploaded_file is None:
        raise ValueError("Select a JPG or PNG image first.")
    if int(getattr(uploaded_file, "size", 0) or 0) > 5 * 1024 * 1024:
        raise ValueError("Profile picture must not exceed 5 MB.")
    mime = str(getattr(uploaded_file, "type", "") or "").lower()
    if mime not in {"image/jpeg", "image/jpg", "image/png"}:
        raise ValueError("Upload a JPG or PNG image.")
    try:
        from PIL import Image, ImageOps

        image = Image.open(BytesIO(uploaded_file.getvalue()))
        return ImageOps.exif_transpose(image).convert("RGB")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The selected image could not be processed.") from exc


def _profile_picture_jpeg(uploaded_file: Any = None, *, image: Any | None = None) -> bytes:
    try:
        from PIL import Image

        working = image.copy() if image is not None else _profile_picture_image(uploaded_file)
        if not isinstance(working, Image.Image):
            raise ValueError("The selected image could not be processed.")
        side = min(working.size)
        left = max(0, (working.width - side) // 2)
        top = max(0, (working.height - side) // 2)
        working = working.crop((left, top, left + side, top + side)).resize(
            (320, 320), Image.Resampling.LANCZOS
        )
        output = BytesIO()
        working.save(output, format="JPEG", quality=88, optimize=True)
        return output.getvalue()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The selected image could not be processed.") from exc


def _profile_picture_data_uri(jpeg_bytes: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes).decode("ascii")


def _profile_picture_positioned_jpeg(
    uploaded_file: Any = None,
    *,
    image: Any | None = None,
    zoom: float = 1.0,
    x_position: int = 0,
    y_position: int = 0,
) -> bytes:
    """Create the actual circular-avatar source based on user positioning controls.

    The saved image remains a 320x320 optimized JPEG.  Instead of showing the tall
    default cropper, this function gives the user smooth position/zoom controls and
    immediately reflects the output in the custom circular preview card.
    """
    try:
        from PIL import Image

        source = image.copy() if image is not None else _profile_picture_image(uploaded_file)
        if not isinstance(source, Image.Image):
            raise ValueError("The selected image could not be processed.")
        source = source.convert("RGB")
        canvas = 720
        zoom = max(1.0, min(2.5, float(zoom or 1.0)))
        x_position = max(-100, min(100, int(x_position or 0)))
        y_position = max(-100, min(100, int(y_position or 0)))

        base_scale = max(canvas / source.width, canvas / source.height)
        scale = base_scale * zoom
        new_size = (
            max(1, int(round(source.width * scale))),
            max(1, int(round(source.height * scale))),
        )
        resized = source.resize(new_size, Image.Resampling.LANCZOS)

        extra_x = max(0, resized.width - canvas)
        extra_y = max(0, resized.height - canvas)
        left = int(round((extra_x / 2) + (x_position / 100) * (extra_x / 2)))
        top = int(round((extra_y / 2) + (y_position / 100) * (extra_y / 2)))
        left = max(0, min(extra_x, left))
        top = max(0, min(extra_y, top))
        cropped = resized.crop((left, top, left + canvas, top + canvas)).resize(
            (320, 320), Image.Resampling.LANCZOS
        )
        output = BytesIO()
        cropped.save(output, format="JPEG", quality=88, optimize=True)
        return output.getvalue()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The selected image could not be processed.") from exc


def _profile_picture_zoomed_image(source_image: Any, zoom: float = 1.0) -> Any:
    try:
        from PIL import Image
        if not isinstance(source_image, Image.Image):
            raise ValueError("The selected image could not be processed.")
        zoom = max(1.0, min(2.5, float(zoom or 1.0)))
        if abs(zoom - 1.0) < 1e-9:
            return source_image.copy()
        new_size = (max(1, int(round(source_image.width * zoom))), max(1, int(round(source_image.height * zoom))))
        return source_image.resize(new_size, Image.Resampling.LANCZOS)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The selected image could not be processed.") from exc


def _avatar_circle_box_algorithm(img: Any, *args: Any, **kwargs: Any) -> dict[str, int]:
    try:
        width, height = img.size
    except Exception:
        return {"left": 0, "top": 0, "width": 320, "height": 320}
    side = max(120, int(min(width, height) * 0.72))
    side = min(side, width, height)
    left = max(0, int((width - side) / 2))
    top = max(0, int((height - side) / 2))
    return {"left": left, "top": top, "width": int(side), "height": int(side)}





AVATAR_DRAG_EDITOR_HTML = r"""
<div class="iars-avatar-editor">
  <div class="avatar-stage" id="avatar-stage">
    <img id="avatar-image" class="avatar-image" draggable="false" />
    <div class="avatar-ring"></div>
  </div>
  <div class="avatar-controls">
    <button type="button" id="zoom-out" title="Zoom out">−</button>
    <input id="zoom-slider" type="range" min="1" max="2.5" step="0.01" value="1" />
    <button type="button" id="zoom-in" title="Zoom in">+</button>
  </div>
  <div class="avatar-hint">Drag the picture inside the fixed circle. Use − / + to zoom.</div>
</div>
"""

AVATAR_DRAG_EDITOR_CSS = r"""
.iars-avatar-editor {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 4px 0 0 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.avatar-stage {
  width: 260px;
  height: 260px;
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  background: #eef4ff;
  border: 4px solid #F3C247;
  box-shadow: 0 10px 24px rgba(6, 26, 54, .22);
  touch-action: none;
  cursor: grab;
  user-select: none;
}
.avatar-stage:active { cursor: grabbing; }
.avatar-image {
  position: absolute;
  left: 0;
  top: 0;
  transform-origin: center center;
  user-select: none;
  -webkit-user-drag: none;
  pointer-events: none;
  max-width: none;
}
.avatar-ring {
  pointer-events: none;
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  box-shadow: 0 0 0 999px rgba(6, 26, 54, .16);
}
.avatar-controls {
  width: 260px;
  display: grid;
  grid-template-columns: 42px 1fr 42px;
  gap: 10px;
  align-items: center;
}
.avatar-controls button {
  width: 42px;
  height: 38px;
  border: 1px solid #cfd9e7;
  border-radius: 10px;
  background: #fff;
  color: #061A36;
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(6,26,54,.08);
}
.avatar-controls button:active { transform: translateY(1px); }
.avatar-controls input[type=range] {
  width: 100%;
  accent-color: #F3C247;
}
.avatar-hint {
  font-size: 12px;
  color: #526579;
  text-align: center;
  margin-top: -2px;
}
"""

AVATAR_DRAG_EDITOR_JS = r"""
export default function(component) {
  const { parentElement, data, setStateValue } = component;
  const stage = parentElement.querySelector('#avatar-stage');
  const image = parentElement.querySelector('#avatar-image');
  const zoomSlider = parentElement.querySelector('#zoom-slider');
  const zoomIn = parentElement.querySelector('#zoom-in');
  const zoomOut = parentElement.querySelector('#zoom-out');

  const stageSize = 260;
  const imageData = String(data?.image_data ?? '');
  const signature = String(data?.upload_signature ?? '');
  const editor = data?.editor && typeof data.editor === 'object' ? data.editor : {};

  let naturalW = 1;
  let naturalH = 1;
  let zoom = clamp(Number(editor.zoom ?? 1), 1, 2.5);
  let xPct = clamp(Number(editor.x_position ?? 0), -100, 100);
  let yPct = clamp(Number(editor.y_position ?? 0), -100, 100);
  let scale = 1;
  let minScale = 1;
  let x = 0;
  let y = 0;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  let syncTimer = null;
  let lastSnapshot = '';

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function computeMinScale() {
    minScale = Math.max(stageSize / naturalW, stageSize / naturalH);
    scale = minScale * zoom;
  }

  function clampXY() {
    const w = naturalW * scale;
    const h = naturalH * scale;
    const minX = Math.min(0, stageSize - w);
    const minY = Math.min(0, stageSize - h);
    x = clamp(x, minX, 0);
    y = clamp(y, minY, 0);
    if (w <= stageSize) x = (stageSize - w) / 2;
    if (h <= stageSize) y = (stageSize - h) / 2;
  }

  function pctToXY() {
    computeMinScale();
    const w = naturalW * scale;
    const h = naturalH * scale;
    const extraX = Math.max(0, w - stageSize);
    const extraY = Math.max(0, h - stageSize);
    x = -extraX / 2 - (xPct / 100) * (extraX / 2);
    y = -extraY / 2 - (yPct / 100) * (extraY / 2);
    clampXY();
  }

  function xyToPct() {
    const w = naturalW * scale;
    const h = naturalH * scale;
    const extraX = Math.max(0, w - stageSize);
    const extraY = Math.max(0, h - stageSize);
    xPct = extraX > 0 ? clamp(Math.round(((-x - extraX / 2) / (extraX / 2)) * 100), -100, 100) : 0;
    yPct = extraY > 0 ? clamp(Math.round(((-y - extraY / 2) / (extraY / 2)) * 100), -100, 100) : 0;
  }

  function apply() {
    computeMinScale();
    clampXY();
    image.style.width = `${naturalW * scale}px`;
    image.style.height = `${naturalH * scale}px`;
    image.style.transform = `translate(${x}px, ${y}px)`;
  }

  function currentValue() {
    xyToPct();
    return {
      avatar: {
        upload_signature: signature,
        x_position: Number(xPct),
        y_position: Number(yPct),
        zoom: Number(Math.round(zoom * 100) / 100),
        updated_at: Date.now(),
      }
    };
  }

  function syncNow() {
    const value = currentValue();
    const snapshot = JSON.stringify(value.avatar);
    if (snapshot !== lastSnapshot) {
      lastSnapshot = snapshot;
      setStateValue('avatar', value.avatar);
    }
  }

  function scheduleSync(wait = 180) {
    if (syncTimer) window.clearTimeout(syncTimer);
    syncTimer = window.setTimeout(syncNow, wait);
  }

  function setZoom(nextZoom, shouldSync = true) {
    const oldScale = scale || minScale;
    const centerX = stageSize / 2;
    const centerY = stageSize / 2;
    const imgPointX = (centerX - x) / oldScale;
    const imgPointY = (centerY - y) / oldScale;

    zoom = clamp(Number(nextZoom || 1), 1, 2.5);
    zoomSlider.value = String(zoom);
    computeMinScale();

    x = centerX - imgPointX * scale;
    y = centerY - imgPointY * scale;
    apply();
    if (shouldSync) scheduleSync(80);
  }

  function init() {
    if (!imageData) return;
    image.onload = () => {
      naturalW = image.naturalWidth || 1;
      naturalH = image.naturalHeight || 1;
      zoomSlider.value = String(zoom);
      pctToXY();
      apply();
      syncNow();
    };
    image.src = imageData;
  }

  stage.addEventListener('pointerdown', (event) => {
    dragging = true;
    lastX = event.clientX;
    lastY = event.clientY;
    stage.setPointerCapture(event.pointerId);
  });

  stage.addEventListener('pointermove', (event) => {
    if (!dragging) return;
    x += event.clientX - lastX;
    y += event.clientY - lastY;
    lastX = event.clientX;
    lastY = event.clientY;
    apply();
    scheduleSync(240);
  });

  stage.addEventListener('pointerup', (event) => {
    dragging = false;
    try { stage.releasePointerCapture(event.pointerId); } catch (_) {}
    syncNow();
  });

  stage.addEventListener('pointercancel', () => {
    dragging = false;
    syncNow();
  });

  zoomSlider.addEventListener('input', () => setZoom(zoomSlider.value, false));
  zoomSlider.addEventListener('change', () => setZoom(zoomSlider.value, true));
  zoomIn.addEventListener('click', () => setZoom(zoom + 0.05, true));
  zoomOut.addEventListener('click', () => setZoom(zoom - 0.05, true));

  init();
}
"""


def _register_avatar_drag_component_v2():
    return st.components.v2.component(
        name="iars_avatar_drag_editor_v1",
        html=AVATAR_DRAG_EDITOR_HTML,
        css=AVATAR_DRAG_EDITOR_CSS,
        js=AVATAR_DRAG_EDITOR_JS,
        isolate_styles=True,
    )


def _read_avatar_drag_state(component_state: Any, default: dict[str, Any]) -> dict[str, Any]:
    if component_state is None:
        return default
    if isinstance(component_state, dict):
        value = component_state.get("avatar", component_state)
    else:
        value = getattr(component_state, "avatar", default)
    if not isinstance(value, dict):
        return default
    result = dict(default)
    result.update(value)
    return result


def _avatar_drag_editor_v2(
    *,
    image_data: str,
    upload_signature: str,
    key: str,
    default_state: dict[str, Any],
    height: int = 342,
) -> dict[str, Any]:
    current_state = _read_avatar_drag_state(st.session_state.get(key), default_state)
    if str(current_state.get("upload_signature") or "") != str(upload_signature or ""):
        current_state = dict(default_state)

    component = _register_avatar_drag_component_v2()
    value = component(
        data={
            "image_data": image_data,
            "upload_signature": upload_signature,
            "editor": current_state,
        },
        default={"avatar": current_state},
        key=key,
        width="stretch",
        height=height,
    )
    return _read_avatar_drag_state(value, current_state)


def _avatar_adjust_number(value: Any, delta: int, *, min_value: int = -100, max_value: int = 100) -> int:
    try:
        current = int(round(float(value)))
    except Exception:
        current = 0
    return max(min_value, min(max_value, current + int(delta)))


def _render_avatar_native_move_controls(x_key: str, y_key: str, zoom_key: str) -> None:
    """Native Streamlit movement controls that simulate drag without HTML/components."""
    st.caption("Move the photo inside the circle using the arrows. Use Fine/Normal/Coarse for movement speed.")

    step_key = "profile_picture_move_step_dialog"
    st.session_state.setdefault(step_key, "Normal")
    speed = st.radio(
        "Movement speed",
        ["Fine", "Normal", "Coarse"],
        horizontal=True,
        key=step_key,
        label_visibility="collapsed",
    )
    step = 2 if speed == "Fine" else 5 if speed == "Normal" else 12

    up_l, up_c, up_r = st.columns([0.34, 0.32, 0.34])
    with up_c:
        if st.button("▲", key="profile_move_up_dialog", use_container_width=True):
            st.session_state[y_key] = _avatar_adjust_number(st.session_state.get(y_key, 0), -step)
            st.rerun()

    left_c, center_c, right_c = st.columns(3)
    with left_c:
        if st.button("◀", key="profile_move_left_dialog", use_container_width=True):
            st.session_state[x_key] = _avatar_adjust_number(st.session_state.get(x_key, 0), -step)
            st.rerun()
    with center_c:
        if st.button("Center", key="profile_move_center_dialog", use_container_width=True):
            st.session_state[x_key] = 0
            st.session_state[y_key] = 0
            st.session_state[zoom_key] = max(1.0, float(st.session_state.get(zoom_key, 1.0)))
            st.rerun()
    with right_c:
        if st.button("▶", key="profile_move_right_dialog", use_container_width=True):
            st.session_state[x_key] = _avatar_adjust_number(st.session_state.get(x_key, 0), step)
            st.rerun()

    down_l, down_c, down_r = st.columns([0.34, 0.32, 0.34])
    with down_c:
        if st.button("▼", key="profile_move_down_dialog", use_container_width=True):
            st.session_state[y_key] = _avatar_adjust_number(st.session_state.get(y_key, 0), step)
            st.rerun()


def _render_avatar_editor_preview(jpeg_bytes: bytes) -> None:
    if not jpeg_bytes:
        return
    data_uri = _profile_picture_data_uri(jpeg_bytes)
    safe_uri = data_uri.replace("'", "%27").replace('"', "%22")
    st.markdown(
        f"""
        <div style="display:flex;justify-content:center;align-items:center;margin:.55rem 0 .65rem 0;">
            <div style="width:220px;height:220px;border-radius:50%;overflow:hidden;border:4px solid #F3C247;
                        box-shadow:0 10px 26px rgba(6,26,54,.18);background:#EEF4FF;">
                <img src="{safe_uri}" alt="Avatar preview" style="width:100%;height:100%;object-fit:cover;display:block;">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _profile_picture_positioned_jpeg_from_image(
    image: Any,
    *,
    zoom: float = 1.0,
    x_position: int = 0,
    y_position: int = 0,
) -> bytes:
    try:
        from PIL import Image

        if not isinstance(image, Image.Image):
            raise ValueError("The selected image could not be processed.")
        source = image.convert("RGB")
        canvas = 720
        zoom = max(1.0, min(2.5, float(zoom or 1.0)))
        x_position = max(-100, min(100, int(x_position or 0)))
        y_position = max(-100, min(100, int(y_position or 0)))

        base_scale = max(canvas / source.width, canvas / source.height)
        scale = base_scale * zoom
        resized = source.resize(
            (
                max(1, int(round(source.width * scale))),
                max(1, int(round(source.height * scale))),
            ),
            Image.Resampling.LANCZOS,
        )

        extra_x = max(0, resized.width - canvas)
        extra_y = max(0, resized.height - canvas)
        left = int(round((extra_x / 2) + (x_position / 100) * (extra_x / 2)))
        top = int(round((extra_y / 2) + (y_position / 100) * (extra_y / 2)))
        left = max(0, min(extra_x, left))
        top = max(0, min(extra_y, top))

        cropped = resized.crop((left, top, left + canvas, top + canvas)).resize(
            (320, 320), Image.Resampling.LANCZOS
        )
        output = BytesIO()
        cropped.save(output, format="JPEG", quality=88, optimize=True)
        return output.getvalue()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The selected image could not be processed.") from exc


def _profile_picture_path(user_id: str) -> str:
    safe_id = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(user_id or "user")).strip("_") or "user"
    return f"profiles/{safe_id}/avatar.jpg"


def _upload_profile_picture(
    client: Any,
    config: AuthConfig,
    user_id: str,
    jpeg_bytes: bytes,
) -> str:
    path = _profile_picture_path(user_id)
    options = {"content-type": "image/jpeg", "cache-control": "3600", "upsert": "true"}
    try:
        bucket = client.storage.from_(config.profile_bucket)
        try:
            bucket.upload(path, jpeg_bytes, file_options=options)
        except TypeError:
            bucket.upload(path, jpeg_bytes, options)
        except Exception as first_exc:
            # Older storage clients may reject upsert on upload. Update is the safe fallback.
            try:
                try:
                    bucket.update(path, jpeg_bytes, file_options={"content-type": "image/jpeg", "cache-control": "3600"})
                except TypeError:
                    bucket.update(path, jpeg_bytes, {"content-type": "image/jpeg", "cache-control": "3600"})
            except Exception:
                raise first_exc
    except Exception as exc:
        detail = _profile_error_text(exc)
        raise ValueError(
            f"Unable to upload the picture to Storage bucket '{config.profile_bucket}': {detail}. "
            "Run the updated SUPABASE_PROFILE_SETUP.sql and verify the service-role key."
        ) from exc
    return path


def _download_profile_picture(client: Any, config: AuthConfig, path: str) -> str:
    if not path:
        return ""
    try:
        data = client.storage.from_(config.profile_bucket).download(path)
        if hasattr(data, "content"):
            data = data.content
        if not isinstance(data, (bytes, bytearray)):
            return ""
        encoded = base64.b64encode(bytes(data)).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return ""


def _remove_profile_picture(client: Any, config: AuthConfig, user_id: str, current_path: str = "") -> None:
    path = current_path or _profile_picture_path(user_id)
    try:
        client.storage.from_(config.profile_bucket).remove([path])
    except Exception:
        # Removing a missing object should not block clearing the profile record.
        pass
    _upsert_profile(
        client,
        config,
        user_id,
        {"profile_picture_path": None, "profile_picture_data": None},
    )


def _effective_admin_profile(client: Any, config: AuthConfig) -> dict[str, Any]:
    profile = _fetch_profile(client, config, "admin")
    username = str(profile.get("username_override") or config.admin_username).strip().casefold()
    picture = _download_profile_picture(client, config, str(profile.get("profile_picture_path") or ""))
    if not picture:
        picture = str(profile.get("profile_picture_data") or "").strip()
    return {
        **profile,
        "profile_picture_data": picture,
        "username": username,
        "full_name": config.admin_name,
        "role": "admin",
        "status": "Active",
        "id": "admin",
    }


def _merge_profile(
    user: dict[str, Any],
    profile: dict[str, Any],
    client: Any | None = None,
    config: AuthConfig | None = None,
) -> dict[str, Any]:
    merged = dict(user)
    picture = ""
    if client is not None and config is not None:
        picture = _download_profile_picture(
            client,
            config,
            str(profile.get("profile_picture_path") or ""),
        )
    if not picture:
        picture = str(profile.get("profile_picture_data") or "").strip()
    if picture:
        merged["profile_picture_data"] = picture
    if profile.get("profile_picture_path"):
        merged["profile_picture_path"] = profile.get("profile_picture_path")
    return merged


def _verify_current_password(client: Any, config: AuthConfig, user: dict[str, Any], password: str) -> bool:
    if is_admin_user(user):
        profile = _effective_admin_profile(client, config)
        salt = str(profile.get("admin_password_salt") or "")
        digest = str(profile.get("admin_password_hash") or "")
        if salt and digest:
            return _password_matches(password, salt, digest)
        return hmac.compare_digest(str(password or ""), config.admin_password)

    fresh = _fetch_user_by_id(client, config, str(user.get("id", "")))
    if not fresh:
        return False
    return _password_matches(
        password,
        str(fresh.get("password_salt", "")),
        str(fresh.get("password_hash", "")),
    )


def _username_is_available(client: Any, config: AuthConfig, username: str, user: dict[str, Any]) -> bool:
    existing = _fetch_user(client, config, username)
    if existing and str(existing.get("id")) != str(user.get("id")):
        return False
    admin_username = _effective_admin_profile(client, config).get("username", "")
    if not is_admin_user(user) and username == admin_username:
        return False
    return True


def _profile_picture_data(uploaded_file: Any) -> str:
    return _profile_picture_data_uri(_profile_picture_jpeg(uploaded_file))


def _render_profile_picture_editor_styles() -> None:
    st.markdown(
        """
        <style>
        .iars-photo-editor-shell {border:1px solid rgba(243,194,71,.58);border-radius:20px;padding:12px;background:linear-gradient(180deg,#FFFFFF 0%,#F7FAFF 100%);box-shadow:0 14px 34px rgba(7,32,72,.10);margin:.2rem 0 .45rem 0;}
        .iars-photo-editor-title {font-weight:900;color:#082C63;margin:0 0 2px 0;font-size:1rem;}
        .iars-photo-editor-sub {color:#506174;margin:0 0 8px 0;font-size:.88rem;line-height:1.3;}
        .iars-card-avatar-preview {display:flex;align-items:center;gap:12px;border-radius:20px;border:1.6px solid #F3C247;background:linear-gradient(135deg,#07386C 0%,#0F4E8D 58%,#0A3569 100%);padding:12px 14px;box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 8px 18px rgba(8,39,81,.16);position:relative;overflow:hidden;min-height:86px;}
        .iars-card-avatar-preview:after {content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,#12A150 0 22%,#EF3340 22% 100%);}
        .iars-card-avatar-circle-wrap {position:relative;width:76px;height:76px;flex:0 0 76px;}
        .iars-card-avatar-circle {width:76px;height:76px;border-radius:50%;overflow:hidden;border:3px solid #F3C247;background:#EAF1FF;box-shadow:0 6px 16px rgba(0,0,0,.24);position:relative;}
        .iars-card-avatar-circle img {display:block;width:100%;height:100%;object-fit:cover;}
        .iars-card-avatar-camera {position:absolute;right:-5px;bottom:-4px;width:28px;height:28px;border-radius:50%;background:#1E78D7;color:#fff;border:2px solid #fff;display:flex;align-items:center;justify-content:center;font-size:.9rem;font-weight:900;box-shadow:0 5px 12px rgba(0,0,0,.23);}
        .iars-card-avatar-name {font-weight:900;color:#FFF;margin:0;font-size:1.02rem;line-height:1.1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
        .iars-card-avatar-role {font-weight:900;color:#F3C247;margin:4px 0 0 0;font-size:.8rem;}
        .st-key-avatar_camera_trigger {position:fixed!important;right:191px!important;top:49px!important;z-index:100061!important;width:30px!important;height:30px!important;margin:0!important;padding:0!important;}
        .st-key-avatar_camera_trigger [data-testid="stPopover"] {width:30px!important;height:30px!important;margin:0!important;padding:0!important;}
        .st-key-avatar_camera_trigger [data-testid="stPopover"] > button, .st-key-avatar_camera_trigger button[kind="secondary"], .st-key-avatar_camera_trigger > div > button {width:30px!important;height:30px!important;min-height:30px!important;margin:0!important;padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important;color:transparent!important;font-size:0!important;line-height:0!important;opacity:0!important;cursor:pointer!important;overflow:hidden!important;}
        .st-key-avatar_camera_trigger [data-testid="stPopover"] > button::before, .st-key-avatar_camera_trigger button[kind="secondary"]::before, .st-key-avatar_camera_trigger > div > button::before {content:""!important;display:none!important;}
        .st-key-avatar_camera_trigger [data-testid="stPopover"] > button [data-testid="stMarkdownContainer"], .st-key-avatar_camera_trigger button[kind="secondary"] [data-testid="stMarkdownContainer"], .st-key-avatar_camera_trigger > div > button [data-testid="stMarkdownContainer"] {display:none!important;}
        .st-key-avatar_camera_trigger button:hover, .st-key-avatar_camera_trigger button:focus, .st-key-avatar_camera_trigger button:active {background:transparent!important;box-shadow:none!important;transform:none!important;outline:none!important;opacity:0!important;}
        .st-key-avatar_camera_menu {min-width:178px!important;padding:.25rem!important;}
        .st-key-avatar_camera_menu .stButton>button {min-height:38px!important;border-radius:10px!important;justify-content:center!important;text-align:center!important;padding-left:.85rem!important;padding-right:.85rem!important;}
        [data-testid="stDialog"] {max-width:min(36vw,460px)!important;}
        [data-testid="stDialog"] [data-testid="stFileUploaderDropzone"], [role="dialog"] [data-testid="stFileUploaderDropzone"] {min-height:60px!important;padding:.4rem!important;border-radius:12px!important;background:#F8FBFF!important;border-color:#B9CAE0!important;}
        [data-testid="stDialog"] [data-testid="stFileUploaderDropzoneInstructions"] p, [role="dialog"] [data-testid="stFileUploaderDropzoneInstructions"] p {font-size:.84rem!important;}
        [data-testid="stDialog"] .stButton>button, [role="dialog"] .stButton>button {min-height:40px!important;border-radius:10px!important;}
        [data-testid="stDialog"] .stSlider [data-baseweb="slider"], [role="dialog"] .stSlider [data-baseweb="slider"] {margin-top:.2rem!important;margin-bottom:.1rem!important;}
        [data-testid="stDialog"] .cropper-container, [role="dialog"] .cropper-container {max-height:300px!important;width:100%!important;}
        [data-testid="stDialog"] .cropper-crop-box, [role="dialog"] .cropper-crop-box, [data-testid="stDialog"] .cropper-view-box, [role="dialog"] .cropper-view-box {border-radius:50%!important;}
        [data-testid="stDialog"] .cropper-view-box, [role="dialog"] .cropper-view-box {outline:0!important;box-shadow:0 0 0 9999em rgba(6,26,54,.52)!important;border:2px solid #FFFFFF!important;}
        [data-testid="stDialog"] .cropper-face, [role="dialog"] .cropper-face {border-radius:50%!important;background-color:transparent!important;}
        [data-testid="stDialog"] .cropper-dashed, [role="dialog"] .cropper-dashed, [data-testid="stDialog"] .cropper-line, [role="dialog"] .cropper-line, [data-testid="stDialog"] .cropper-point, [role="dialog"] .cropper-point, [data-testid="stDialog"] .cropper-center, [role="dialog"] .cropper-center {display:none!important;}
        [data-testid="stDialog"] .cropper-modal, [role="dialog"] .cropper-modal {background:rgba(6,26,54,.42)!important;}
        [data-testid="stDialog"] .cropper-crop-box, [role="dialog"] .cropper-crop-box, [data-testid="stDialog"] .cropper-view-box, [role="dialog"] .cropper-view-box {pointer-events:none!important;}

        [data-testid="stDialog"] section, [role="dialog"] section {padding-top:.8rem!important;}
        [data-testid="stDialog"] .cropper-container, [role="dialog"] .cropper-container {margin-left:auto!important;margin-right:auto!important;}
        @media(max-width:900px) { .st-key-avatar_camera_trigger {right:127px!important;top:45px!important;} [data-testid="stDialog"] {max-width:min(92vw,420px)!important;} }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_profile_picture_card_preview(data_uri: str, display_name: str, role_label: str) -> None:
    if not data_uri:
        return
    safe_uri = data_uri.replace("'", "%27").replace('"', "%22")
    safe_name = str(display_name or "User").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_role = str(role_label or "User").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(
        f"""
        <div class="iars-photo-editor-shell">
            <p class="iars-photo-editor-title">Profile picture preview</p>
            <p class="iars-photo-editor-sub">Ito ang actual na lalabas sa bilog ng top-right user card bago i-save.</p>
            <div class="iars-card-avatar-preview">
                <div class="iars-card-avatar-circle-wrap">
                    <div class="iars-card-avatar-circle"><img src="{safe_uri}" alt="Avatar preview"></div>
                    <div class="iars-card-avatar-camera">📷</div>
                </div>
                <div class="iars-card-avatar-text">
                    <p class="iars-card-avatar-name">{safe_name}</p>
                    <p class="iars-card-avatar-role">{safe_role}</p>
                </div>
            </div>
            <div class="iars-avatar-guide"><div class="iars-avatar-guide-badge">↔</div><div>Use the controls below to position the photo. The circular preview updates before saving.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_avatar_full_view(data_uri: str) -> None:
    if not data_uri:
        st.info("No avatar")
        return
    safe_uri = data_uri.replace("'", "%27").replace('"', '%22')
    st.markdown(
        f"""
        <div class="iars-photo-editor-shell" style="padding:16px;">
            <div style="display:flex;justify-content:center;align-items:center;">
                <img src="{safe_uri}" alt="Avatar" style="width:280px;height:280px;object-fit:cover;border-radius:18px;border:3px solid #F3C247;box-shadow:0 12px 30px rgba(0,0,0,.18);background:#fff;">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_profile_picture_circle_preview(data_uri: str) -> None:
    _render_profile_picture_card_preview(data_uri, "Profile Preview", "Live circular crop")



PROFILE_MENU_OPEN = "iars_profile_menu_open"


AVATAR_VIEW_DIALOG_OPEN = "iars_avatar_view_dialog_open"
AVATAR_EDIT_DIALOG_OPEN = "iars_avatar_edit_dialog_open"
AVATAR_UPLOAD_VERSION = "iars_avatar_upload_version"
AVATAR_DIALOG_MODE = "iars_avatar_dialog_mode"


def _profile_diagnostics_cached(client: Any, config: AuthConfig) -> dict[str, Any]:
    """Cache profile diagnostics per browser session to avoid menu-open lag."""
    cache_key = "iars_profile_storage_diagnostics"
    cached = st.session_state.get(cache_key)
    if isinstance(cached, dict):
        return cached
    diagnostics = _profile_storage_diagnostics(client, config)
    st.session_state[cache_key] = diagnostics
    return diagnostics


def _refresh_profile_diagnostics(client: Any, config: AuthConfig) -> dict[str, Any]:
    diagnostics = _profile_storage_diagnostics(client, config)
    st.session_state["iars_profile_storage_diagnostics"] = diagnostics
    return diagnostics


def _profile_save_picture(
    client: Any,
    config: AuthConfig,
    *,
    user: dict[str, Any],
    user_id: str,
    current_username: str,
    uploaded_picture: Any,
    prepared_jpeg_bytes: bytes | None = None,
) -> str:
    if uploaded_picture is None:
        raise ValueError("Please choose a JPG or PNG picture first.")

    diagnostics = _profile_diagnostics_cached(client, config)
    if not diagnostics.get("table_ready"):
        diagnostics = _refresh_profile_diagnostics(client, config)
    if not diagnostics.get("table_ready"):
        raise ValueError(
            "The profile table is not accessible. Run the updated "
            "SUPABASE_PROFILE_SETUP.sql, then refresh the app."
        )

    jpeg_bytes = prepared_jpeg_bytes or _profile_picture_jpeg(uploaded_picture)
    picture_data = _profile_picture_data_uri(jpeg_bytes)
    picture_path = ""
    storage_error = ""

    if diagnostics.get("bucket_ready"):
        try:
            picture_path = _upload_profile_picture(client, config, user_id, jpeg_bytes)
        except Exception as exc:
            storage_error = _profile_error_text(exc)

    if picture_path:
        _upsert_profile(
            client,
            config,
            user_id,
            {"profile_picture_path": picture_path, "profile_picture_data": None},
        )
    else:
        _upsert_profile(
            client,
            config,
            user_id,
            {"profile_picture_path": None, "profile_picture_data": picture_data},
        )
        if storage_error:
            st.caption(f"Storage fallback used: {storage_error}")

    _log_event(
        client,
        config,
        event_type="profile_picture_changed",
        username=current_username,
        user_id=None if is_admin_user(user) else user_id,
        success=True,
    )
    updated_user = dict(user)
    updated_user["profile_picture_data"] = picture_data
    updated_user["profile_picture_path"] = picture_path
    _cache_session_user(updated_user)
    st.success("Profile picture updated successfully.")
    return picture_data


def _close_avatar_dialogs(clear_upload: bool = False) -> None:
    st.session_state[AVATAR_VIEW_DIALOG_OPEN] = False
    st.session_state[AVATAR_EDIT_DIALOG_OPEN] = False
    st.session_state[AVATAR_DIALOG_MODE] = ""
    if clear_upload:
        st.session_state[AVATAR_UPLOAD_VERSION] = int(st.session_state.get(AVATAR_UPLOAD_VERSION, 0)) + 1
        st.session_state.pop("profile_picture_zoom_dialog", None)


def _open_avatar_mode(mode: str) -> None:
    st.session_state[AVATAR_DIALOG_MODE] = mode
    st.session_state[AVATAR_VIEW_DIALOG_OPEN] = mode == "see"
    st.session_state[AVATAR_EDIT_DIALOG_OPEN] = mode == "change"


def _render_avatar_dialogs(client: Any, user: dict[str, Any], config: AuthConfig, *, current_username: str, role_label: str, user_id: str) -> None:
    current_picture = str(user.get("profile_picture_data") or "").strip()

    @st.dialog("See Avatar", width="small")
    def _see_avatar_dialog() -> None:
        _render_avatar_full_view(current_picture)
        if st.button("Close", key="profile_avatar_dialog_close", use_container_width=True):
            _close_avatar_dialogs()
            st.rerun()

    @st.dialog("Change Avatar", width="small")
    def _change_avatar_dialog() -> None:
        if AVATAR_UPLOAD_VERSION not in st.session_state:
            st.session_state[AVATAR_UPLOAD_VERSION] = 0
        uploader_key = f"profile_picture_upload_dialog_{st.session_state.get(AVATAR_UPLOAD_VERSION, 0)}"
        uploaded_picture = st.file_uploader(
            "Upload photo",
            type=["jpg", "jpeg", "png"],
            key=uploader_key,
            label_visibility="collapsed",
        )

        prepared_preview_bytes = None
        if uploaded_picture is not None:
            try:
                source_image = _profile_picture_image(uploaded_picture)
                st.caption("Drag the picture inside the fixed circle. This uses the same Components v2 pattern as PDF Tagging, not the old HTML/component path that crashed.")
                upload_signature = _avatar_upload_signature(uploaded_picture)
                default_drag_state = {
                    "upload_signature": upload_signature,
                    "x_position": 0,
                    "y_position": 0,
                    "zoom": 1.0,
                    "updated_at": 0,
                }
                upload_data_uri = _profile_picture_data_uri(_profile_picture_jpeg(image=source_image))
                drag_state = _avatar_drag_editor_v2(
                    image_data=upload_data_uri,
                    upload_signature=upload_signature,
                    key=f"profile_avatar_drag_v2_{st.session_state.get(AVATAR_UPLOAD_VERSION, 0)}",
                    default_state=default_drag_state,
                )

                prepared_preview_bytes = _profile_picture_positioned_jpeg_from_image(
                    source_image,
                    zoom=float(drag_state.get("zoom", 1.0)),
                    x_position=int(float(drag_state.get("x_position", 0))),
                    y_position=int(float(drag_state.get("y_position", 0))),
                )

                with st.expander("Fallback controls if drag does not update", expanded=False):
                    zoom_key = "profile_picture_zoom_dialog"
                    x_key = "profile_picture_x_dialog"
                    y_key = "profile_picture_y_dialog"
                    st.session_state.setdefault(zoom_key, float(drag_state.get("zoom", 1.0)))
                    st.session_state.setdefault(x_key, int(float(drag_state.get("x_position", 0))))
                    st.session_state.setdefault(y_key, int(float(drag_state.get("y_position", 0))))
                    minus_col, zoom_col, plus_col = st.columns([0.18, 0.64, 0.18])
                    with minus_col:
                        if st.button("−", key="profile_zoom_minus_dialog", use_container_width=True):
                            st.session_state[zoom_key] = max(1.00, round(float(st.session_state.get(zoom_key, 1.00)) - 0.05, 2))
                    with zoom_col:
                        st.slider("Zoom", min_value=1.00, max_value=2.50, value=float(st.session_state.get(zoom_key, 1.00)), step=0.05, key=zoom_key, label_visibility="collapsed")
                    with plus_col:
                        if st.button("+", key="profile_zoom_plus_dialog", use_container_width=True):
                            st.session_state[zoom_key] = min(2.50, round(float(st.session_state.get(zoom_key, 1.00)) + 0.05, 2))
                    _render_avatar_native_move_controls(x_key, y_key, zoom_key)
                    st.slider("Move photo left / right", -100, 100, int(st.session_state.get(x_key, 0)), 5, key=x_key)
                    st.slider("Move photo up / down", -100, 100, int(st.session_state.get(y_key, 0)), 5, key=y_key)
                    fallback_preview_bytes = _profile_picture_positioned_jpeg_from_image(
                        source_image,
                        zoom=float(st.session_state.get(zoom_key, 1.0)),
                        x_position=int(st.session_state.get(x_key, 0)),
                        y_position=int(st.session_state.get(y_key, 0)),
                    )
                    if st.button("Use fallback controls for save", key="profile_use_fallback_avatar", use_container_width=True):
                        prepared_preview_bytes = fallback_preview_bytes
                    _render_avatar_editor_preview(fallback_preview_bytes)
            except ValueError as exc:
                st.error(str(exc))

        save_col, cancel_col = st.columns(2)
        with save_col:
            if st.button("Save", key="profile_picture_save_dialog", type="primary", use_container_width=True):
                try:
                    _profile_save_picture(
                        client,
                        config,
                        user=user,
                        user_id=user_id,
                        current_username=current_username,
                        uploaded_picture=uploaded_picture,
                        prepared_jpeg_bytes=prepared_preview_bytes,
                    )
                    st.session_state.pop(SESSION_USER_CACHE, None)
                    st.session_state.pop(SESSION_CACHE_LOADED_AT, None)
                    _close_avatar_dialogs(clear_upload=True)
                    st.session_state.pop("profile_picture_x_dialog", None)
                    st.session_state.pop("profile_picture_y_dialog", None)
                    st.session_state.pop("profile_picture_move_step_dialog", None)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"Unable to save profile picture: {_profile_error_text(exc)}")
        with cancel_col:
            if st.button("Cancel", key="profile_picture_cancel_dialog", use_container_width=True):
                _close_avatar_dialogs(clear_upload=True)
                st.session_state.pop("profile_picture_x_dialog", None)
                st.session_state.pop("profile_picture_y_dialog", None)
                st.session_state.pop("profile_picture_move_step_dialog", None)
                st.rerun()

    if st.session_state.get(AVATAR_EDIT_DIALOG_OPEN):
        st.session_state[AVATAR_VIEW_DIALOG_OPEN] = False
        _change_avatar_dialog()
    elif st.session_state.get(AVATAR_VIEW_DIALOG_OPEN):
        st.session_state[AVATAR_EDIT_DIALOG_OPEN] = False
        _see_avatar_dialog()


def render_profile_menu(client: Any, user: dict[str, Any], config: AuthConfig) -> None:
    """Render the top-right profile menu with a front-end popover.

    The user-card open/close action uses Streamlit's popover with on_change="ignore",
    so opening and closing the menu no longer triggers a full app rerun.  Database
    and Storage checks are performed only when the user saves/removes data.
    """
    current_username = user_username(user)
    role_label = "Administrator" if is_admin_user(user) else "Auditor"
    user_id = "admin" if is_admin_user(user) else str(user.get("id", ""))

    _render_profile_picture_editor_styles()
    _render_avatar_dialogs(client, user, config, current_username=current_username, role_label=role_label, user_id=user_id)

    with st.popover(
        "📷",
        key="avatar_camera_trigger",
        help=None,
        use_container_width=False,
        width="content",
        on_change="ignore",
    ):
        with st.container(key="avatar_camera_menu"):
            if st.button("See Avatar", key="avatar_camera_open_view", use_container_width=True):
                _open_avatar_mode("see")
                st.rerun()
            if st.button("Change Avatar", key="avatar_camera_open_change", type="primary", use_container_width=True):
                _open_avatar_mode("change")
                st.rerun()

    with st.popover(
        "​",
        key="profile_menu_trigger",
        help=None,
        use_container_width=True,
        width="content",
        on_change="ignore",
    ):
        with st.container(key="iars_profile_menu"):
            st.markdown("## Edit Profile")
            st.caption(f"@{current_username} · {role_label}")
            st.caption("Close this panel by clicking the top-right user card again or anywhere outside the menu.")

            with st.expander("Change Username", expanded=False):
                with st.container(key="profile_username_panel"):
                    with st.form("profile_change_username_form"):
                        st.text_input("Current Username", value=current_username, disabled=True)
                        new_username_input = st.text_input("New Username", placeholder="Enter a new username")
                        current_password = st.text_input("Current Password", type="password")
                        submitted = st.form_submit_button("Update Username", type="primary", use_container_width=True)
                    if submitted:
                        try:
                            new_username = normalize_username(new_username_input)
                            if new_username == current_username:
                                raise ValueError("Enter a different username.")
                            if not _verify_current_password(client, config, user, current_password):
                                raise ValueError("Current password is incorrect.")
                            if not _username_is_available(client, config, new_username, user):
                                raise ValueError("That username is already in use.")
                            if is_admin_user(user):
                                _upsert_profile(client, config, "admin", {"username_override": new_username})
                            else:
                                _update_user(client, config, user_id, {"username": new_username})
                            st.session_state[SESSION_USERNAME] = new_username
                            cached_user = dict(user)
                            cached_user["username"] = new_username
                            _cache_session_user(cached_user)
                            if _has_persistent_auth_token():
                                refreshed_user = {**user, "username": new_username}
                                _store_persistent_auth_token(config, refreshed_user, True)
                            _log_event(client, config, event_type="username_changed", username=new_username, user_id=None if is_admin_user(user) else user_id, success=True)
                            st.success("Username updated successfully.")
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
                        except Exception as exc:
                            st.error(f"Unable to update username: {_profile_error_text(exc)}")

            with st.expander("Change Password", expanded=False):
                with st.container(key="profile_password_panel"):
                    with st.form("profile_change_password_form"):
                        current_password = st.text_input("Current Password", type="password", key="profile_current_password")
                        new_password = st.text_input("New Password", type="password", key="profile_new_password")
                        confirm_password = st.text_input("Confirm New Password", type="password", key="profile_confirm_password")
                        submitted = st.form_submit_button("Update Password", type="primary", use_container_width=True)
                    if submitted:
                        try:
                            if not _verify_current_password(client, config, user, current_password):
                                raise ValueError("Current password is incorrect.")
                            validated = validate_password(new_password, confirm_password)
                            if _verify_current_password(client, config, user, validated):
                                raise ValueError("New password must be different from the current password.")
                            salt, digest = _new_password_parts(validated)
                            if is_admin_user(user):
                                _upsert_profile(client, config, "admin", {"admin_password_salt": salt, "admin_password_hash": digest})
                            else:
                                _update_user(client, config, user_id, {"password_salt": salt, "password_hash": digest, "failed_login_attempts": 0, "locked_until": None})
                            _log_event(client, config, event_type="password_changed", username=current_username, user_id=None if is_admin_user(user) else user_id, success=True)
                            st.success("Password updated successfully.")
                        except ValueError as exc:
                            st.error(str(exc))
                        except Exception as exc:
                            st.error(f"Unable to update password: {_profile_error_text(exc)}")

            st.divider()
            st.markdown(
                '<a class="iars-profile-signout-action" href="?iars_sign_out=1" target="_self" '
                'aria-label="Sign Out">Sign Out</a>',
                unsafe_allow_html=True,
            )


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


def _session_secret(config: AuthConfig) -> bytes:
    seed = config.code_secret or config.admin_password or config.service_role_key or config.url
    return hashlib.sha256(str(seed or "iars-local-session").encode("utf-8")).digest()


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    padded = text + "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _create_persistent_auth_token(config: AuthConfig, user: dict[str, Any], remember: bool) -> str:
    now = _utc_now()
    lifetime = timedelta(days=PERSISTENT_AUTH_REMEMBER_DAYS) if remember else timedelta(minutes=config.session_timeout_minutes)
    payload = {
        "uid": str(user.get("id", "")),
        "username": str(user.get("username", "")),
        "role": str(user.get("role", "user")),
        "iat": int(now.timestamp()),
        "exp": int((now + lifetime).timestamp()),
        "remember": bool(remember),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_part = _b64url_encode(payload_bytes)
    sig = hmac.new(_session_secret(config), payload_part.encode("ascii"), hashlib.sha256).digest()
    return f"{payload_part}.{_b64url_encode(sig)}"


def _read_persistent_auth_token(config: AuthConfig) -> dict[str, Any] | None:
    try:
        raw = str(st.query_params.get(PERSISTENT_AUTH_PARAM, "") or "").strip()
    except Exception:
        raw = ""
    if not raw or "." not in raw:
        return None
    payload_part, sig_part = raw.split(".", 1)
    expected = hmac.new(_session_secret(config), payload_part.encode("ascii"), hashlib.sha256).digest()
    try:
        actual = _b64url_decode(sig_part)
    except Exception:
        return None
    if not hmac.compare_digest(actual, expected):
        return None
    try:
        payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    except Exception:
        return None
    exp = int(payload.get("exp") or 0)
    if exp <= int(_utc_now().timestamp()):
        _clear_persistent_auth_token()
        return None
    return payload if isinstance(payload, dict) else None


def _store_persistent_auth_token(config: AuthConfig, user: dict[str, Any], remember: bool) -> None:
    try:
        st.query_params[PERSISTENT_AUTH_PARAM] = _create_persistent_auth_token(config, user, remember)
        if "auth_view" in st.query_params:
            del st.query_params["auth_view"]
    except Exception:
        pass


def _clear_persistent_auth_token() -> None:
    try:
        if PERSISTENT_AUTH_PARAM in st.query_params:
            del st.query_params[PERSISTENT_AUTH_PARAM]
        if "auth_view" in st.query_params:
            del st.query_params["auth_view"]
        if SIGN_OUT_PARAM in st.query_params:
            del st.query_params[SIGN_OUT_PARAM]
    except Exception:
        pass


def _has_persistent_auth_token() -> bool:
    try:
        return bool(str(st.query_params.get(PERSISTENT_AUTH_PARAM, "") or "").strip())
    except Exception:
        return False


def _cache_session_user(user: dict[str, Any]) -> None:
    """Keep the hydrated user/profile in Streamlit session state.

    This prevents every dashboard/sidebar click from calling Supabase again just
    to re-read the same user and profile picture.  Profile-changing actions
    update this cache before rerun.
    """
    st.session_state[SESSION_USER_CACHE] = dict(user or {})
    st.session_state[SESSION_CACHE_LOADED_AT] = _iso(_utc_now())


def _get_cached_session_user(user_id: str, username: str, role: str) -> dict[str, Any] | None:
    cached = st.session_state.get(SESSION_USER_CACHE)
    loaded_at = _parse_datetime(st.session_state.get(SESSION_CACHE_LOADED_AT))
    if not isinstance(cached, dict) or loaded_at is None:
        return None
    if _utc_now() - loaded_at > timedelta(seconds=AUTH_CACHE_SECONDS):
        return None
    if str(cached.get("id", "")) != str(user_id):
        return None
    if str(cached.get("username", "")).casefold() != str(username).casefold():
        return None
    if str(cached.get("role", "user")) != str(role):
        return None
    return dict(cached)


def _set_session_state(user: dict[str, Any], *, show_mask: bool = False) -> None:
    st.session_state[SESSION_USER_ID] = str(user.get("id", ""))
    st.session_state[SESSION_USERNAME] = str(user.get("username", ""))
    st.session_state[SESSION_ROLE] = str(user.get("role", "user"))
    st.session_state[SESSION_LAST_ACTIVITY] = _iso(_utc_now())
    _cache_session_user(user)
    if show_mask:
        st.session_state["iars_show_login_exit_mask"] = True


def _set_session(user: dict[str, Any], config: AuthConfig | None = None, remember: bool = False) -> None:
    _set_session_state(user, show_mask=False)
    if config is not None:
        _store_persistent_auth_token(config, user, remember)


def clear_auth_session() -> None:
    for key in (
        SESSION_USER_ID,
        SESSION_USERNAME,
        SESSION_ROLE,
        SESSION_LAST_ACTIVITY,
        SESSION_USER_CACHE,
        SESSION_CACHE_LOADED_AT,
        ADMIN_LAST_CODE,
        PROFILE_MENU_OPEN,
        "iars_show_login_exit_mask",
    ):
        st.session_state.pop(key, None)
    _clear_persistent_auth_token()


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


def _restore_from_persistent_auth_token(client: Any, config: AuthConfig) -> dict[str, Any] | None:
    payload = _read_persistent_auth_token(config)
    if not payload:
        return None

    user_id = str(payload.get("uid") or "")
    username = str(payload.get("username") or "")
    role = str(payload.get("role") or "")
    if not user_id or not username or not role:
        _clear_persistent_auth_token()
        return None

    if role == "admin" and user_id == "admin":
        admin_user = _effective_admin_profile(client, config)
        if username != str(admin_user.get("username", "")).casefold():
            _clear_persistent_auth_token()
            return None
        _set_session_state(admin_user, show_mask=False)
        return admin_user

    user = _fetch_user_by_id(client, config, user_id)
    if not user or str(user.get("status", "")) != "Active":
        _clear_persistent_auth_token()
        return None
    if username != str(user.get("username", "")).casefold():
        _clear_persistent_auth_token()
        return None
    user["role"] = "user"
    merged = _merge_profile(user, _fetch_profile(client, config, str(user.get("id", ""))), client, config)
    _set_session_state(merged, show_mask=False)
    return merged


def restore_auth_session(client: Any, config: AuthConfig) -> dict[str, Any] | None:
    if not st.session_state.get(SESSION_USER_ID):
        token_user = _restore_from_persistent_auth_token(client, config)
        if token_user is not None:
            return token_user

    user_id = str(st.session_state.get(SESSION_USER_ID, "") or "")
    username = str(st.session_state.get(SESSION_USERNAME, "") or "")
    role = str(st.session_state.get(SESSION_ROLE, "") or "")
    last_activity = _parse_datetime(st.session_state.get(SESSION_LAST_ACTIVITY))

    if not user_id or not username or not role or last_activity is None:
        return None

    if _utc_now() - last_activity > timedelta(minutes=config.session_timeout_minutes):
        for key in (SESSION_USER_ID, SESSION_USERNAME, SESSION_ROLE, SESSION_LAST_ACTIVITY):
            st.session_state.pop(key, None)
        token_user = _restore_from_persistent_auth_token(client, config)
        if token_user is not None:
            return token_user
        clear_auth_session()
        return None

    st.session_state[SESSION_LAST_ACTIVITY] = _iso(_utc_now())
    cached_user = _get_cached_session_user(user_id, username, role)
    if cached_user is not None:
        return cached_user

    if role == "admin":
        admin_user = _effective_admin_profile(client, config)
        if username != str(admin_user.get("username", "")).casefold():
            clear_auth_session()
            return None
        _cache_session_user(admin_user)
        return admin_user

    user = _fetch_user_by_id(client, config, user_id)
    if not user or str(user.get("status", "")) != "Active":
        clear_auth_session()
        return None
    user["role"] = "user"
    merged = _merge_profile(user, _fetch_profile(client, config, str(user.get("id", ""))), client, config)
    _cache_session_user(merged)
    return merged


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
    remember: bool = False,
) -> None:
    username = normalize_username(username_input)
    admin_user = _effective_admin_profile(client, config)
    if username == str(admin_user.get("username", "")).casefold():
        salt = str(admin_user.get("admin_password_salt") or "")
        digest = str(admin_user.get("admin_password_hash") or "")
        password_ok = _password_matches(password, salt, digest) if salt and digest else hmac.compare_digest(password, config.admin_password)
        if not password_ok:
            _log_event(client, config, event_type="admin_sign_in", username=username, success=False)
            raise ValueError("Incorrect username or password.")
        _set_session(admin_user, config, remember)
        _log_event(client, config, event_type="admin_sign_in", username=username, success=True)
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
    _set_session(user, config, remember)
    _log_event(
        client,
        config,
        event_type="user_sign_in",
        username=username,
        user_id=str(user.get("id")),
        success=True,
    )
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
        _process_sign_in_credentials(client, config, username_input, password, remember=remember)
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
    render_transition_guard()

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
        sign_out_requested = str(st.query_params.get(SIGN_OUT_PARAM, "") or "").strip() == "1"
        if sign_out_requested:
            _log_event(
                client,
                config,
                event_type="sign_out",
                username=str(st.session_state.get(SESSION_USERNAME, "") or ""),
                user_id=None if str(st.session_state.get(SESSION_ROLE, "")) == "admin" else str(st.session_state.get(SESSION_USER_ID, "") or ""),
                success=True,
            )
            clear_auth_session()
            user = None
        else:
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
    """Backward-compatible no-op; account actions now live in the top-right profile menu."""
    return None
