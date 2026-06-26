from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any, Iterable

import streamlit as st


EDL_NAVY = "#071C3A"
EDL_NAVY_2 = "#0B2D57"
EDL_NAVY_3 = "#123D70"
EDL_GOLD = "#C78B12"
EDL_GOLD_LIGHT = "#E5B13C"
EDL_RED = "#D92D20"
EDL_GREEN = "#178A52"
EDL_BLUE = "#2563EB"
EDL_PURPLE = "#6941C6"
EDL_TEAL = "#087E8B"
EDL_BG = "#F4F7FB"
EDL_TEXT = "#16213A"
EDL_MUTED = "#667085"
EDL_BORDER = "#DCE3EC"


def _asset_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / "assets" / filename


def _asset_data_uri(filename: str) -> str:
    path = _asset_path(filename)
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _logo_data_uri() -> str:
    return _asset_data_uri("edl_logo.png")


def _audit_image_data_uri() -> str:
    return _asset_data_uri("internal_audit_workspace.png")


def _render_html(fragment: str) -> None:
    """Render controlled local HTML without Markdown code-block interpretation."""
    if hasattr(st, "html"):
        st.html(fragment)
    else:  # pragma: no cover - compatibility fallback
        st.markdown(fragment, unsafe_allow_html=True)


def apply_iars_theme() -> None:
    """Apply the EDL Internal Audit professional visual system."""
    css = f"""
<style>
:root {{
  --edl-navy:{EDL_NAVY}; --edl-navy-2:{EDL_NAVY_2}; --edl-navy-3:{EDL_NAVY_3};
  --edl-gold:{EDL_GOLD}; --edl-gold-light:{EDL_GOLD_LIGHT}; --edl-red:{EDL_RED};
  --edl-green:{EDL_GREEN}; --edl-blue:{EDL_BLUE}; --edl-purple:{EDL_PURPLE};
  --edl-teal:{EDL_TEAL}; --edl-bg:{EDL_BG}; --edl-text:{EDL_TEXT};
  --edl-muted:{EDL_MUTED}; --edl-border:{EDL_BORDER};
}}
html,body,[class*="css"],.stApp {{
  font-family:Inter,"Segoe UI",Roboto,Arial,sans-serif;
}}
.stApp {{
  background:
    radial-gradient(circle at 90% 0%,rgba(199,139,18,.07),transparent 24rem),
    linear-gradient(180deg,#F9FBFE 0%,var(--edl-bg) 100%);
  color:var(--edl-text);
}}
.block-container {{max-width:1500px;padding-top:1.25rem;padding-bottom:3rem;}}
header[data-testid="stHeader"] {{background:rgba(249,251,254,.86);backdrop-filter:blur(14px);}}
#MainMenu {{visibility:hidden;}}
footer {{visibility:hidden;}}

section[data-testid="stSidebar"] {{
  background:linear-gradient(180deg,#06182F 0%,#08254A 55%,#061A35 100%);
  border-right:1px solid rgba(255,255,255,.08);
}}
section[data-testid="stSidebar"] > div {{padding-top:.55rem;}}
section[data-testid="stSidebar"] * {{color:#F8FAFC;}}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] .stCaption {{color:rgba(255,255,255,.62)!important;}}
section[data-testid="stSidebar"] hr {{border-color:rgba(255,255,255,.11);}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
  border-radius:10px;padding:.38rem .55rem;margin:.08rem 0;transition:.15s ease;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
  background:rgba(255,255,255,.08);
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
  background:linear-gradient(135deg,#B97808,#D89F22);
  box-shadow:0 7px 18px rgba(199,139,18,.25);
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {{color:#FFFFFF!important;font-weight:760;}}
section[data-testid="stSidebar"] .stButton>button {{
  border-radius:10px;border-color:rgba(255,255,255,.18);background:rgba(255,255,255,.07);color:white;
}}
section[data-testid="stSidebar"] .stButton>button:hover {{
  background:rgba(199,139,18,.22);border-color:rgba(229,177,60,.58);
}}

.edl-brand-stripe {{height:4px;border-radius:99px;background:linear-gradient(90deg,#1665D8 0 24%,#169B45 24% 49%,#E8B629 49% 74%,#E3282C 74% 100%);}}
.edl-sidebar-brand {{text-align:center;padding:.35rem .2rem .8rem;}}
.edl-sidebar-brand img {{width:132px;max-width:78%;object-fit:contain;filter:drop-shadow(0 10px 22px rgba(0,0,0,.25));}}
.edl-sidebar-brand h3 {{margin:.55rem 0 .05rem;font-size:1rem;letter-spacing:.03em;color:#FFF;}}
.edl-sidebar-brand p {{margin:0;color:rgba(255,255,255,.64)!important;font-size:.73rem;letter-spacing:.035em;text-transform:uppercase;}}

.edl-app-header {{
  display:flex;align-items:center;gap:1rem;padding:.88rem 1.05rem;background:rgba(255,255,255,.96);
  border:1px solid var(--edl-border);border-radius:16px;box-shadow:0 8px 26px rgba(7,28,58,.06);margin-bottom:.9rem;
}}
.edl-app-logo {{width:70px;height:70px;object-fit:contain;flex:0 0 auto;}}
.edl-app-kicker {{color:var(--edl-gold);font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;}}
.edl-app-title {{margin:.18rem 0 0;color:var(--edl-navy);font-size:clamp(1.45rem,2.6vw,2.15rem);line-height:1.08;font-weight:820;letter-spacing:-.03em;}}
.edl-app-subtitle {{color:var(--edl-muted);margin-top:.28rem;font-size:.88rem;}}
.edl-user-chip {{margin-left:auto;background:#F8FAFC;border:1px solid var(--edl-border);border-radius:12px;padding:.55rem .75rem;min-width:170px;text-align:right;}}
.edl-user-chip strong {{color:var(--edl-navy);font-size:.9rem;}}
.edl-user-chip span {{color:var(--edl-muted);font-size:.74rem;}}

.edl-section-head {{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;margin:.55rem 0 .85rem;}}
.edl-section-head h2 {{margin:0;color:var(--edl-navy);font-size:1.45rem;letter-spacing:-.02em;}}
.edl-section-head p {{margin:.22rem 0 0;color:var(--edl-muted);font-size:.9rem;}}
.edl-section-badge {{white-space:nowrap;border:1px solid rgba(199,139,18,.28);background:rgba(199,139,18,.09);color:#80590B;border-radius:999px;padding:.38rem .62rem;font-size:.72rem;font-weight:760;}}

.edl-metric-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:.72rem;margin:.15rem 0 1rem;}}
.edl-metric-card {{position:relative;overflow:hidden;background:#FFF;border:1px solid var(--edl-border);border-radius:14px;padding:.9rem 1rem;box-shadow:0 6px 18px rgba(7,28,58,.045);}}
.edl-metric-card:before {{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--accent,var(--edl-gold));}}
.edl-metric-icon {{position:absolute;right:.8rem;top:.7rem;font-size:1.25rem;opacity:.86;}}
.edl-metric-label {{color:var(--edl-muted);font-size:.7rem;font-weight:760;text-transform:uppercase;letter-spacing:.045em;}}
.edl-metric-value {{color:var(--edl-navy);font-size:1.55rem;font-weight:830;line-height:1.15;margin:.28rem 0 .16rem;}}
.edl-metric-note {{color:var(--edl-muted);font-size:.73rem;}}

.edl-feature-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.75rem;margin:.15rem 0 1rem;}}
.edl-feature-card {{min-height:128px;background:linear-gradient(145deg,#FFF,#FBFCFE);border:1px solid var(--edl-border);border-radius:14px;padding:.9rem;box-shadow:0 6px 18px rgba(7,28,58,.04);}}
.edl-feature-icon {{font-size:1.35rem;margin-bottom:.45rem;}}
.edl-feature-card h4 {{margin:0 0 .25rem;color:var(--edl-navy);font-size:.96rem;}}
.edl-feature-card p {{margin:0;color:var(--edl-muted);font-size:.79rem;line-height:1.48;}}

.edl-dashboard-hero {{
  position:relative;overflow:hidden;min-height:245px;border-radius:18px;border:1px solid var(--edl-border);
  background:linear-gradient(90deg,rgba(255,255,255,.99) 0%,rgba(255,255,255,.94) 44%,rgba(255,255,255,.18) 72%),var(--hero-image) center right/cover no-repeat;
  box-shadow:0 10px 28px rgba(7,28,58,.07);padding:2rem 2.15rem;margin:.3rem 0 1rem;
}}
.edl-dashboard-hero h1 {{max-width:560px;color:var(--edl-navy);font-size:clamp(2rem,4vw,3.1rem);line-height:1.04;letter-spacing:-.045em;margin:0 0 .65rem;font-weight:850;}}
.edl-dashboard-hero h1 em {{color:var(--edl-gold);font-style:normal;}}
.edl-dashboard-hero p {{max-width:570px;color:#526077;font-size:.98rem;line-height:1.58;margin:0;}}
.edl-hero-tag {{display:inline-flex;align-items:center;gap:.38rem;background:rgba(7,28,58,.06);color:var(--edl-navy);border:1px solid rgba(7,28,58,.1);border-radius:999px;padding:.36rem .62rem;font-size:.72rem;font-weight:750;margin-bottom:.75rem;}}

.edl-login-wrap {{min-height:calc(100vh - 3rem);display:flex;align-items:center;}}
.edl-login-hero {{position:relative;overflow:hidden;min-height:620px;border-radius:22px;padding:2.2rem;color:white;background:linear-gradient(180deg,rgba(5,23,48,.90),rgba(5,26,55,.96)),var(--audit-image) center/cover no-repeat;box-shadow:0 20px 50px rgba(7,28,58,.17);}}
.edl-login-hero img {{width:170px;max-width:58%;height:auto;object-fit:contain;margin-bottom:1.4rem;filter:drop-shadow(0 9px 22px rgba(0,0,0,.28));}}
.edl-login-hero .eyebrow {{color:#F0C65A;font-size:.73rem;font-weight:820;letter-spacing:.14em;text-transform:uppercase;}}
.edl-login-hero h1 {{color:white;font-size:clamp(2.25rem,4vw,3.5rem);letter-spacing:-.045em;line-height:1.02;margin:.48rem 0 .75rem;font-weight:850;}}
.edl-login-hero h1 em {{color:#F0C65A;font-style:normal;}}
.edl-login-hero p {{color:rgba(255,255,255,.78);max-width:580px;font-size:.97rem;line-height:1.62;}}
.edl-login-points {{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.55rem;margin-top:1.2rem;}}
.edl-login-point {{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:12px;padding:.72rem .8rem;color:white;font-size:.8rem;backdrop-filter:blur(6px);}}
.edl-login-foot {{position:absolute;left:2.2rem;right:2.2rem;bottom:1.4rem;color:rgba(255,255,255,.58);font-size:.72rem;border-top:1px solid rgba(255,255,255,.12);padding-top:.8rem;}}

.edl-user-card {{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:13px;padding:.75rem .8rem;margin:.35rem 0 .6rem;}}
.edl-user-card strong {{display:block;color:#FFF;font-size:.9rem;}}
.edl-user-card span {{color:rgba(255,255,255,.64);font-size:.73rem;}}
.edl-status-card {{border-radius:12px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.07);padding:.68rem .76rem;margin:.3rem 0 .55rem;color:#FFF;}}
.edl-status-card strong {{color:#FFF;display:block;margin-bottom:.12rem;font-size:.82rem;}}
.edl-status-card span {{color:rgba(255,255,255,.68);font-size:.72rem;}}
.edl-status-dot {{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:.38rem;background:var(--dot,var(--edl-green));box-shadow:0 0 0 3px rgba(23,138,82,.16);}}

.edl-library-note {{display:flex;gap:.7rem;align-items:flex-start;padding:.85rem .95rem;border:1px solid #CFE0F5;background:#F4F8FE;border-radius:12px;margin:.25rem 0 .8rem;}}
.edl-library-note strong {{color:var(--edl-navy);}}
.edl-library-note span {{color:var(--edl-muted);font-size:.8rem;}}

.stButton>button,.stDownloadButton>button,button[kind="primary"] {{border-radius:9px;font-weight:730;transition:.12s ease;}}
.stButton>button:hover,.stDownloadButton>button:hover {{transform:translateY(-1px);box-shadow:0 7px 16px rgba(7,28,58,.10);}}
button[kind="primary"] {{background:linear-gradient(135deg,#B77908,#DDAA2E)!important;color:white!important;border:1px solid #A96E06!important;}}
[data-testid="stFileUploaderDropzone"] {{border:1.5px dashed rgba(37,99,235,.38);background:linear-gradient(145deg,rgba(37,99,235,.025),rgba(199,139,18,.035));border-radius:14px;padding:1rem;}}
[data-testid="stMetric"] {{background:#FFF;border:1px solid var(--edl-border);border-radius:13px;padding:.78rem .9rem;box-shadow:0 5px 16px rgba(7,28,58,.04);}}
[data-testid="stDataFrame"],[data-testid="stDataEditor"] {{border:1px solid var(--edl-border);border-radius:12px;overflow:hidden;box-shadow:0 5px 18px rgba(7,28,58,.04);}}
[data-testid="stAlert"] {{border-radius:11px;border-width:1px;}}
div[data-testid="stForm"],div[data-testid="stVerticalBlockBorderWrapper"] {{border-color:var(--edl-border)!important;border-radius:15px!important;box-shadow:0 7px 22px rgba(7,28,58,.04);background:rgba(255,255,255,.97);}}
.stTabs [data-baseweb="tab-list"] {{gap:.28rem;background:#FFF;border:1px solid var(--edl-border);padding:.28rem;border-radius:11px;box-shadow:0 4px 14px rgba(7,28,58,.035);}}
.stTabs [data-baseweb="tab"] {{border-radius:8px;padding:.48rem .75rem;color:var(--edl-muted);font-weight:700;}}
.stTabs [aria-selected="true"] {{background:rgba(199,139,18,.11)!important;color:#78520A!important;}}
.stTabs [data-baseweb="tab-highlight"] {{background-color:var(--edl-gold)!important;}}

@media(max-width:1000px) {{.edl-user-chip{{display:none}}.edl-login-hero{{min-height:520px}}}}
@media(max-width:700px) {{
  .block-container{{padding-left:.9rem;padding-right:.9rem}}
  .edl-app-header{{align-items:flex-start}}.edl-app-logo{{width:56px;height:56px}}
  .edl-login-points{{grid-template-columns:1fr}}.edl-login-hero{{min-height:510px;padding:1.35rem}}
  .edl-login-foot{{left:1.35rem;right:1.35rem}}.edl-dashboard-hero{{padding:1.35rem;background:linear-gradient(90deg,rgba(255,255,255,.97),rgba(255,255,255,.86)),var(--hero-image) center/cover}}
}}
</style>
"""
    _render_html(css)


def render_brand_stripe() -> None:
    _render_html('<div class="edl-brand-stripe"></div>')


def render_sidebar_brand() -> None:
    logo = _logo_data_uri()
    image = f'<img src="{logo}" alt="EDL GROUP OF COMPANIES logo">' if logo else ""
    _render_html(
        '<div class="edl-sidebar-brand">'
        f'{image}<h3>Internal Audit</h3><p>EDL GROUP OF COMPANIES</p>'
        '</div>'
    )


def render_app_header(user: dict[str, Any], *, version: str) -> None:
    logo = _logo_data_uri()
    image = f'<img class="edl-app-logo" src="{logo}" alt="EDL GROUP OF COMPANIES logo">' if logo else ""
    name = html.escape(str(user.get("full_name") or user.get("username") or "IARS User"))
    role = "Administrator" if str(user.get("role", "")).lower() == "admin" else "Auditor"
    _render_html(
        '<div class="edl-brand-stripe"></div>'
        '<div class="edl-app-header">'
        f'{image}<div><div class="edl-app-kicker">EDL GROUP OF COMPANIES</div>'
        '<h1 class="edl-app-title">Internal Audit Report System</h1>'
        f'<div class="edl-app-subtitle">Secure extraction, PDF tagging, shared archives and controlled records · v{html.escape(version)}</div></div>'
        f'<div class="edl-user-chip"><strong>{name}</strong><br><span>{role}</span></div></div>'
    )


def render_login_hero() -> None:
    logo = _logo_data_uri()
    audit_image = _audit_image_data_uri()
    image = f'<img src="{logo}" alt="EDL GROUP OF COMPANIES logo">' if logo else ""
    style = f' style="--audit-image:url({audit_image})"' if audit_image else ""
    _render_html(
        f'<div class="edl-login-hero"{style}>'
        f'{image}<div class="eyebrow">EDL GROUP OF COMPANIES</div>'
        '<h1>Secure Internal Audit <em>Workspace.</em></h1>'
        '<p>Access the Internal Audit Report System for secure report extraction, PDF tagging, shared archive access, reusable templates, policies and controlled audit records.</p>'
        '<div class="edl-login-points">'
        '<div class="edl-login-point">🛡️ Admin-approved access</div>'
        '<div class="edl-login-point">📄 Smart report extraction</div>'
        '<div class="edl-login-point">🗂️ Shared document libraries</div>'
        '<div class="edl-login-point">✅ Controlled audit records</div>'
        '</div><div class="edl-login-foot">Secure · Confidential · EDL GROUP OF COMPANIES Internal Audit</div></div>'
    )


def render_dashboard_hero() -> None:
    audit_image = _audit_image_data_uri()
    style = f' style="--hero-image:url({audit_image})"' if audit_image else ""
    _render_html(
        f'<div class="edl-dashboard-hero"{style}>'
        '<div class="edl-hero-tag">🛡️ Internal Audit Digital Workspace</div>'
        '<h1>Delivering Integrity.<br>Driving <em>Assurance.</em></h1>'
        '<p>Empowering the Internal Audit team with secure tools, accurate data, reusable resources and actionable records for confident decision-making.</p>'
        '</div>'
    )


def render_section_header(title: str, subtitle: str = "", badge: str = "") -> None:
    badge_html = f'<div class="edl-section-badge">{html.escape(badge)}</div>' if badge else ""
    _render_html(
        '<div class="edl-section-head"><div>'
        f'<h2>{html.escape(title)}</h2><p>{html.escape(subtitle)}</p></div>{badge_html}</div>'
    )


def render_metric_cards(cards: Iterable[dict[str, Any]]) -> None:
    accents = [EDL_GOLD, EDL_BLUE, EDL_GREEN, EDL_PURPLE, EDL_TEAL, EDL_RED]
    chunks: list[str] = []
    for index, card in enumerate(cards):
        label = html.escape(str(card.get("label", "")))
        value = html.escape(str(card.get("value", "")))
        note = html.escape(str(card.get("note", "")))
        icon = html.escape(str(card.get("icon", "")))
        accent = html.escape(str(card.get("accent") or accents[index % len(accents)]))
        chunks.append(
            f'<div class="edl-metric-card" style="--accent:{accent}">'
            f'<div class="edl-metric-icon">{icon}</div><div class="edl-metric-label">{label}</div>'
            f'<div class="edl-metric-value">{value}</div><div class="edl-metric-note">{note}</div></div>'
        )
    _render_html(f'<div class="edl-metric-grid">{"".join(chunks)}</div>')


def render_feature_cards(cards: Iterable[dict[str, Any]]) -> None:
    chunks: list[str] = []
    for card in cards:
        icon = html.escape(str(card.get("icon", "")))
        title = html.escape(str(card.get("title", "")))
        text = html.escape(str(card.get("text", "")))
        chunks.append(
            f'<div class="edl-feature-card"><div class="edl-feature-icon">{icon}</div>'
            f'<h4>{title}</h4><p>{text}</p></div>'
        )
    _render_html(f'<div class="edl-feature-grid">{"".join(chunks)}</div>')


def render_sidebar_status(title: str, detail: str, *, ok: bool = True) -> None:
    dot = EDL_GREEN if ok else EDL_RED
    _render_html(
        '<div class="edl-status-card">'
        f'<strong><span class="edl-status-dot" style="--dot:{dot}"></span>{html.escape(title)}</strong>'
        f'<span>{html.escape(detail)}</span></div>'
    )


def render_sidebar_user(user: dict[str, Any]) -> None:
    name = html.escape(str(user.get("full_name") or user.get("username") or "IARS User"))
    username = html.escape(str(user.get("username") or ""))
    role = "Administrator" if str(user.get("role", "")).lower() == "admin" else "Auditor"
    _render_html(
        '<div class="edl-user-card">'
        f'<strong>{name}</strong><span>@{username} · {role}</span></div>'
    )


def render_library_note(title: str, detail: str, icon: str = "ℹ️") -> None:
    _render_html(
        '<div class="edl-library-note">'
        f'<div>{html.escape(icon)}</div><div><strong>{html.escape(title)}</strong><br><span>{html.escape(detail)}</span></div></div>'
    )
