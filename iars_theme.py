from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any, Iterable

import streamlit as st


EDL_NAVY = "#0F172A"
EDL_NAVY_2 = "#17233D"
EDL_GOLD = "#C9971A"
EDL_GOLD_LIGHT = "#F4C430"
EDL_RED = "#E11D28"
EDL_GREEN = "#16A34A"
EDL_BLUE = "#2563EB"
EDL_BG = "#F6F8FC"
EDL_TEXT = "#172033"
EDL_MUTED = "#667085"
EDL_BORDER = "#E4E7EC"


def _logo_path() -> Path:
    return Path(__file__).resolve().parent / "assets" / "edl_logo.png"


def _logo_data_uri() -> str:
    path = _logo_path()
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def apply_iars_theme() -> None:
    """Apply the EDL Audit Pro visual system without changing application logic."""
    st.markdown(
        f"""
        <style>
        :root {{
            --edl-navy: {EDL_NAVY};
            --edl-navy-2: {EDL_NAVY_2};
            --edl-gold: {EDL_GOLD};
            --edl-red: {EDL_RED};
            --edl-green: {EDL_GREEN};
            --edl-blue: {EDL_BLUE};
            --edl-bg: {EDL_BG};
            --edl-text: {EDL_TEXT};
            --edl-muted: {EDL_MUTED};
            --edl-border: {EDL_BORDER};
        }}

        html, body, [class*="css"] {{
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                "Segoe UI", sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(circle at 92% 2%, rgba(201,151,26,.09), transparent 21rem),
                radial-gradient(circle at 75% 12%, rgba(37,99,235,.05), transparent 24rem),
                var(--edl-bg);
            color: var(--edl-text);
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.35rem;
            padding-bottom: 3rem;
        }}

        header[data-testid="stHeader"] {{
            background: rgba(246,248,252,.92);
            border-bottom: 1px solid rgba(228,231,236,.85);
            backdrop-filter: blur(12px);
        }}

        section[data-testid="stSidebar"] {{
            background:
                linear-gradient(180deg, rgba(15,23,42,.98), rgba(23,35,61,.99));
            border-right: 1px solid rgba(255,255,255,.08);
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding-top: .75rem;
        }}

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
            color: #F8FAFC !important;
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,.12);
        }}

        section[data-testid="stSidebar"] .stButton > button {{
            border-color: rgba(255,255,255,.18);
            background: rgba(255,255,255,.07);
            color: #FFFFFF;
        }}

        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: rgba(201,151,26,.22);
            border-color: rgba(244,196,48,.55);
        }}

        .edl-brand-stripe {{
            height: 5px;
            border-radius: 99px;
            background: linear-gradient(90deg,
                var(--edl-blue) 0 24%,
                var(--edl-green) 24% 49%,
                var(--edl-gold) 49% 74%,
                var(--edl-red) 74% 100%);
            box-shadow: 0 5px 14px rgba(15,23,42,.10);
        }}

        .edl-app-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.2rem;
            background: rgba(255,255,255,.94);
            border: 1px solid var(--edl-border);
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(15,23,42,.07);
            margin-bottom: .9rem;
        }}

        .edl-app-logo {{
            width: 76px;
            height: 76px;
            object-fit: contain;
            flex: 0 0 auto;
            border-radius: 16px;
            background: #FFFFFF;
            padding: 4px;
        }}

        .edl-app-kicker {{
            color: var(--edl-gold);
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin-bottom: .2rem;
        }}

        .edl-app-title {{
            margin: 0;
            color: var(--edl-navy);
            font-size: clamp(1.55rem, 3vw, 2.35rem);
            line-height: 1.08;
            font-weight: 850;
            letter-spacing: -.035em;
        }}

        .edl-app-subtitle {{
            color: var(--edl-muted);
            margin-top: .35rem;
            font-size: .94rem;
        }}

        .edl-user-chip {{
            margin-left: auto;
            background: #F8FAFC;
            border: 1px solid var(--edl-border);
            border-radius: 14px;
            padding: .65rem .85rem;
            min-width: 165px;
            text-align: right;
        }}

        .edl-user-chip strong {{ color: var(--edl-navy); }}
        .edl-user-chip span {{ color: var(--edl-muted); font-size: .78rem; }}

        .edl-sidebar-brand {{
            text-align: center;
            padding: .45rem .25rem .85rem;
        }}
        .edl-sidebar-brand img {{
            width: 118px;
            max-width: 72%;
            filter: drop-shadow(0 8px 18px rgba(0,0,0,.22));
            background: white;
            border-radius: 18px;
            padding: 5px;
        }}
        .edl-sidebar-brand h3 {{
            margin: .6rem 0 .12rem;
            font-size: 1rem;
            letter-spacing: .02em;
        }}
        .edl-sidebar-brand p {{
            margin: 0;
            color: rgba(255,255,255,.66) !important;
            font-size: .76rem;
        }}

        .edl-section-head {{
            display:flex;
            align-items:flex-end;
            justify-content:space-between;
            gap:1rem;
            margin: .6rem 0 1rem;
        }}
        .edl-section-head h2 {{
            margin:0;
            color:var(--edl-navy);
            font-size:1.55rem;
            letter-spacing:-.02em;
        }}
        .edl-section-head p {{
            margin:.25rem 0 0;
            color:var(--edl-muted);
        }}
        .edl-section-badge {{
            white-space:nowrap;
            border:1px solid rgba(201,151,26,.30);
            background:rgba(201,151,26,.10);
            color:#8A6510;
            border-radius:999px;
            padding:.42rem .68rem;
            font-size:.76rem;
            font-weight:750;
        }}

        .edl-metric-grid {{
            display:grid;
            grid-template-columns: repeat(4, minmax(0,1fr));
            gap:.85rem;
            margin:.2rem 0 1rem;
        }}
        .edl-metric-card {{
            position:relative;
            overflow:hidden;
            background:#FFFFFF;
            border:1px solid var(--edl-border);
            border-radius:16px;
            padding:1rem 1.05rem;
            box-shadow:0 7px 20px rgba(15,23,42,.05);
        }}
        .edl-metric-card::before {{
            content:"";
            position:absolute;
            left:0; top:0; bottom:0;
            width:5px;
            background:var(--accent, var(--edl-gold));
        }}
        .edl-metric-label {{
            color:var(--edl-muted);
            font-size:.78rem;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:.05em;
        }}
        .edl-metric-value {{
            color:var(--edl-navy);
            font-size:1.75rem;
            font-weight:850;
            line-height:1.15;
            margin:.32rem 0 .2rem;
        }}
        .edl-metric-note {{ color:var(--edl-muted); font-size:.78rem; }}

        .edl-feature-grid {{
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:.85rem;
            margin:.2rem 0 1.1rem;
        }}
        .edl-feature-card {{
            min-height:150px;
            background:linear-gradient(145deg,#FFFFFF,#FAFBFD);
            border:1px solid var(--edl-border);
            border-radius:16px;
            padding:1rem;
            box-shadow:0 7px 20px rgba(15,23,42,.04);
        }}
        .edl-feature-icon {{ font-size:1.5rem; margin-bottom:.55rem; }}
        .edl-feature-card h4 {{ margin:0 0 .3rem; color:var(--edl-navy); }}
        .edl-feature-card p {{ margin:0; color:var(--edl-muted); font-size:.84rem; line-height:1.45; }}

        .edl-login-hero {{
            min-height: 540px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            padding:2rem 1.25rem;
        }}
        .edl-login-hero img {{
            width:180px;
            max-width:60%;
            background:#FFFFFF;
            border-radius:24px;
            padding:8px;
            box-shadow:0 18px 45px rgba(15,23,42,.14);
            margin-bottom:1.15rem;
        }}
        .edl-login-hero .eyebrow {{
            color:var(--edl-gold);
            font-size:.78rem;
            font-weight:850;
            letter-spacing:.14em;
            text-transform:uppercase;
        }}
        .edl-login-hero h1 {{
            color:var(--edl-navy);
            font-size:clamp(2rem,4vw,3.25rem);
            letter-spacing:-.045em;
            line-height:1.03;
            margin:.45rem 0 .75rem;
        }}
        .edl-login-hero p {{
            color:var(--edl-muted);
            max-width:580px;
            font-size:1rem;
            line-height:1.6;
        }}
        .edl-login-points {{
            display:grid;
            grid-template-columns:repeat(2,minmax(0,1fr));
            gap:.55rem;
            margin-top:1.05rem;
        }}
        .edl-login-point {{
            background:#FFFFFF;
            border:1px solid var(--edl-border);
            border-radius:12px;
            padding:.72rem .8rem;
            color:var(--edl-text);
            font-size:.82rem;
            box-shadow:0 5px 16px rgba(15,23,42,.04);
        }}

        div[data-testid="stForm"],
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-color: var(--edl-border) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 24px rgba(15,23,42,.045);
            background: rgba(255,255,255,.94);
        }}

        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"] {{
            border-radius: 10px;
            font-weight: 750;
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(15,23,42,.10);
        }}
        button[kind="primary"] {{
            background: linear-gradient(135deg, #B88410, {EDL_GOLD_LIGHT}) !important;
            color: #17120A !important;
            border: 1px solid #B88410 !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap:.35rem;
            background:#FFFFFF;
            border:1px solid var(--edl-border);
            padding:.35rem;
            border-radius:13px;
            box-shadow:0 5px 16px rgba(15,23,42,.04);
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius:9px;
            padding:.55rem .85rem;
            color:var(--edl-muted);
            font-weight:700;
        }}
        .stTabs [aria-selected="true"] {{
            background:rgba(201,151,26,.13) !important;
            color:#795A0D !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color:var(--edl-gold) !important;
        }}

        [data-testid="stFileUploaderDropzone"] {{
            border:1.5px dashed rgba(37,99,235,.42);
            background:linear-gradient(145deg,rgba(37,99,235,.035),rgba(201,151,26,.045));
            border-radius:16px;
            padding:1rem;
        }}

        [data-testid="stMetric"] {{
            background:#FFFFFF;
            border:1px solid var(--edl-border);
            border-radius:15px;
            padding:.85rem 1rem;
            box-shadow:0 6px 18px rgba(15,23,42,.04);
        }}

        [data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
            border:1px solid var(--edl-border);
            border-radius:14px;
            overflow:hidden;
            box-shadow:0 6px 20px rgba(15,23,42,.04);
        }}

        [data-testid="stAlert"] {{
            border-radius:12px;
            border-width:1px;
        }}

        .edl-status-card {{
            border-radius:13px;
            border:1px solid rgba(255,255,255,.12);
            background:rgba(255,255,255,.07);
            padding:.75rem .85rem;
            margin:.3rem 0 .6rem;
            color:#FFFFFF;
        }}
        .edl-status-card strong {{ color:#FFFFFF; display:block; margin-bottom:.15rem; }}
        .edl-status-card span {{ color:rgba(255,255,255,.70); font-size:.78rem; }}
        .edl-status-dot {{
            display:inline-block;
            width:8px;height:8px;border-radius:50%;
            margin-right:.42rem;
            background:var(--dot, var(--edl-green));
            box-shadow:0 0 0 3px rgba(22,163,74,.16);
        }}

        @media (max-width: 1000px) {{
            .edl-metric-grid, .edl-feature-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
            .edl-user-chip {{ display:none; }}
        }}
        @media (max-width: 650px) {{
            .block-container {{ padding-left:1rem; padding-right:1rem; }}
            .edl-app-header {{ align-items:flex-start; }}
            .edl-app-logo {{ width:58px; height:58px; }}
            .edl-metric-grid, .edl-feature-grid, .edl-login-points {{ grid-template-columns:1fr; }}
            .edl-login-hero {{ min-height:auto; padding:1rem 0 .5rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_stripe() -> None:
    st.markdown('<div class="edl-brand-stripe"></div>', unsafe_allow_html=True)


def render_sidebar_brand() -> None:
    logo = _logo_data_uri()
    image = f'<img src="{logo}" alt="EDL Group logo">' if logo else ""
    st.markdown(
        f"""
        <div class="edl-sidebar-brand">
            {image}
            <h3>Internal Audit</h3>
            <p>EDL Group of Companies</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_app_header(user: dict[str, Any], *, version: str) -> None:
    logo = _logo_data_uri()
    image = f'<img class="edl-app-logo" src="{logo}" alt="EDL Group logo">' if logo else ""
    name = html.escape(str(user.get("full_name") or user.get("username") or "IARS User"))
    role = "Administrator" if str(user.get("role", "")).lower() == "admin" else "Auditor"
    st.markdown(
        f"""
        <div class="edl-brand-stripe"></div>
        <div class="edl-app-header">
            {image}
            <div>
                <div class="edl-app-kicker">EDL Group Internal Audit</div>
                <h1 class="edl-app-title">Internal Audit Report System</h1>
                <div class="edl-app-subtitle">Secure report extraction, PDF tagging, shared archive and controlled account access · v{html.escape(version)}</div>
            </div>
            <div class="edl-user-chip"><strong>{name}</strong><br><span>{role}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_hero() -> None:
    logo = _logo_data_uri()
    image = f'<img src="{logo}" alt="EDL Group logo">' if logo else ""
    st.markdown(
        f"""
        <div class="edl-login-hero">
            {image}
            <div class="eyebrow">EDL Group Internal Audit</div>
            <h1>Internal Audit<br>Report System</h1>
            <p>One secure workspace for extracting audit reports, validating findings, tagging PDFs and maintaining a shared document archive.</p>
            <div class="edl-login-points">
                <div class="edl-login-point">🛡️ Admin-approved access</div>
                <div class="edl-login-point">📄 Smart report extraction</div>
                <div class="edl-login-point">🗂️ Shared PDF archive</div>
                <div class="edl-login-point">✅ Controlled audit records</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "", badge: str = "") -> None:
    badge_html = f'<div class="edl-section-badge">{html.escape(badge)}</div>' if badge else ""
    st.markdown(
        f"""
        <div class="edl-section-head">
            <div><h2>{html.escape(title)}</h2><p>{html.escape(subtitle)}</p></div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(cards: Iterable[dict[str, Any]]) -> None:
    accents = [EDL_GOLD, EDL_BLUE, EDL_GREEN, EDL_RED]
    chunks: list[str] = []
    for index, card in enumerate(cards):
        label = html.escape(str(card.get("label", "")))
        value = html.escape(str(card.get("value", "")))
        note = html.escape(str(card.get("note", "")))
        accent = html.escape(str(card.get("accent") or accents[index % len(accents)]))
        chunks.append(
            f"""
            <div class="edl-metric-card" style="--accent:{accent}">
                <div class="edl-metric-label">{label}</div>
                <div class="edl-metric-value">{value}</div>
                <div class="edl-metric-note">{note}</div>
            </div>
            """
        )
    st.markdown(f'<div class="edl-metric-grid">{"".join(chunks)}</div>', unsafe_allow_html=True)


def render_feature_cards(cards: Iterable[dict[str, Any]]) -> None:
    chunks: list[str] = []
    for card in cards:
        icon = html.escape(str(card.get("icon", "")))
        title = html.escape(str(card.get("title", "")))
        text = html.escape(str(card.get("text", "")))
        chunks.append(
            f"""
            <div class="edl-feature-card">
                <div class="edl-feature-icon">{icon}</div>
                <h4>{title}</h4>
                <p>{text}</p>
            </div>
            """
        )
    st.markdown(f'<div class="edl-feature-grid">{"".join(chunks)}</div>', unsafe_allow_html=True)


def render_sidebar_status(title: str, detail: str, *, ok: bool = True) -> None:
    dot = EDL_GREEN if ok else EDL_RED
    st.markdown(
        f"""
        <div class="edl-status-card">
            <strong><span class="edl-status-dot" style="--dot:{dot}"></span>{html.escape(title)}</strong>
            <span>{html.escape(detail)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
