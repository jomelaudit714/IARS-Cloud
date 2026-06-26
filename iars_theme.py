from __future__ import annotations

import base64
import html
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

import streamlit as st


EDL_NAVY = "#061A36"
EDL_NAVY_2 = "#0A2C59"
EDL_NAVY_3 = "#123F78"
EDL_GOLD = "#C88A08"
EDL_GOLD_LIGHT = "#E4AE2F"
EDL_RED = "#D92D20"
EDL_GREEN = "#148A4B"
EDL_BLUE = "#175CD3"
EDL_PURPLE = "#6938EF"
EDL_TEAL = "#087E8B"
EDL_BG = "#F5F7FB"
EDL_TEXT = "#14213D"
EDL_MUTED = "#667085"
EDL_BORDER = "#E1E6EE"


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
    return _asset_data_uri("internal_audit_visual.png")


def _render_html(fragment: str) -> None:
    """Render trusted local HTML without Markdown treating tags as code."""
    if hasattr(st, "html"):
        st.html(fragment)
    else:  # pragma: no cover - compatibility with older Streamlit versions
        st.markdown(fragment, unsafe_allow_html=True)


def apply_iars_theme() -> None:
    """Apply the EDL enterprise Internal Audit design system."""
    css = f"""
<style>
:root {{
  --edl-navy:{EDL_NAVY}; --edl-navy-2:{EDL_NAVY_2}; --edl-navy-3:{EDL_NAVY_3};
  --edl-gold:{EDL_GOLD}; --edl-gold-light:{EDL_GOLD_LIGHT}; --edl-red:{EDL_RED};
  --edl-green:{EDL_GREEN}; --edl-blue:{EDL_BLUE}; --edl-purple:{EDL_PURPLE};
  --edl-teal:{EDL_TEAL}; --edl-bg:{EDL_BG}; --edl-text:{EDL_TEXT};
  --edl-muted:{EDL_MUTED}; --edl-border:{EDL_BORDER};
  --edl-shadow:0 8px 28px rgba(16,24,40,.07);
}}
html,body,.stApp,[class*="css"] {{font-family:Inter,"Segoe UI",Roboto,Arial,sans-serif;}}
.stApp {{background:linear-gradient(180deg,#FBFCFE 0%,var(--edl-bg) 100%);color:var(--edl-text);}}
.block-container {{max-width:1580px;padding:1.05rem 1.55rem 3rem;}}
header[data-testid="stHeader"] {{height:2.4rem;background:rgba(250,252,255,.88);backdrop-filter:blur(12px);border-bottom:1px solid rgba(225,230,238,.65);}}
#MainMenu,footer {{visibility:hidden;}}
[data-testid="stToolbar"] {{top:.25rem;}}

/* Sidebar */
section[data-testid="stSidebar"] {{background:linear-gradient(180deg,#05162E 0%,#07264D 58%,#061A36 100%);border-right:1px solid rgba(255,255,255,.08);}}
section[data-testid="stSidebar"] > div {{padding-top:.45rem;}}
section[data-testid="stSidebar"] * {{color:#F8FAFC;}}
section[data-testid="stSidebar"] hr {{border-color:rgba(255,255,255,.10);margin:.7rem 0;}}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],section[data-testid="stSidebar"] .stCaption {{color:rgba(255,255,255,.62)!important;}}
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {{gap:.18rem;}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
  min-height:42px;border-radius:9px;padding:.46rem .62rem;margin:.04rem 0;border:1px solid transparent;transition:.16s ease;
}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{background:rgba(255,255,255,.075);border-color:rgba(255,255,255,.06);}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{background:linear-gradient(135deg,#B87905,#DCA423);box-shadow:0 7px 18px rgba(199,139,18,.22);}}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {{color:#FFF!important;font-weight:760;}}
section[data-testid="stSidebar"] .stButton>button {{border-radius:9px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);color:#FFF;}}
section[data-testid="stSidebar"] .stButton>button:hover {{background:rgba(199,139,18,.22);border-color:rgba(229,177,60,.48);}}

.edl-sidebar-brand {{text-align:center;padding:.1rem .15rem .85rem;}}
.edl-sidebar-logo-shell {{display:inline-flex;background:#FFF;border-radius:14px;padding:.35rem;box-shadow:0 12px 28px rgba(0,0,0,.22);}}
.edl-sidebar-brand img {{width:118px;height:118px;object-fit:contain;border-radius:10px;}}
.edl-sidebar-brand h3 {{margin:.7rem 0 .08rem;color:#FFF;font-size:1.02rem;line-height:1.15;letter-spacing:.035em;}}
.edl-sidebar-brand p {{margin:0;color:rgba(255,255,255,.58)!important;font-size:.68rem;letter-spacing:.10em;text-transform:uppercase;}}
.edl-sidebar-section {{margin:.3rem 0 .35rem;color:rgba(255,255,255,.42)!important;font-size:.64rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;}}
.edl-user-card {{background:rgba(255,255,255,.075);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:.72rem .78rem;margin:.35rem 0 .55rem;}}
.edl-user-card strong {{display:block;color:#FFF;font-size:.88rem;}}
.edl-user-card span {{color:rgba(255,255,255,.62);font-size:.71rem;}}
.edl-status-card {{border-radius:10px;border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.055);padding:.58rem .66rem;margin:.25rem 0 .4rem;}}
.edl-status-card strong {{color:#FFF;display:block;margin-bottom:.08rem;font-size:.75rem;}}
.edl-status-card span {{color:rgba(255,255,255,.61);font-size:.67rem;line-height:1.35;}}
.edl-status-dot {{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:.38rem;background:var(--dot,var(--edl-green));box-shadow:0 0 0 3px rgba(23,138,82,.15);}}

/* Top bar */
.edl-topbar {{display:flex;align-items:center;gap:1rem;padding:.7rem .9rem;background:#FFF;border:1px solid var(--edl-border);border-radius:12px;box-shadow:0 4px 18px rgba(16,24,40,.045);margin:.05rem 0 .85rem;}}
.edl-topbar-title {{min-width:0;}}
.edl-topbar-title h1 {{margin:0;color:var(--edl-navy);font-size:1.32rem;font-weight:800;letter-spacing:-.025em;}}
.edl-topbar-title p {{margin:.15rem 0 0;color:var(--edl-muted);font-size:.75rem;}}
.edl-topbar-spacer {{flex:1;}}
.edl-topbar-date {{color:var(--edl-muted);font-size:.72rem;white-space:nowrap;}}
.edl-user-chip {{display:flex;align-items:center;gap:.55rem;background:#F8FAFC;border:1px solid var(--edl-border);border-radius:10px;padding:.42rem .58rem;min-width:170px;}}
.edl-user-avatar {{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#E9EEF6;color:var(--edl-navy);font-size:.75rem;font-weight:800;}}
.edl-user-chip strong {{display:block;color:var(--edl-navy);font-size:.77rem;}}
.edl-user-chip span {{display:block;color:var(--edl-muted);font-size:.64rem;margin-top:.04rem;}}
.edl-brand-stripe {{height:3px;border-radius:99px;background:linear-gradient(90deg,#1F6FDA 0 24%,#149A49 24% 49%,#E5B22D 49% 74%,#E62D32 74% 100%);margin-bottom:.45rem;}}

/* Page headings and cards */
.edl-section-head {{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;margin:.35rem 0 .72rem;}}
.edl-section-head h2 {{margin:0;color:var(--edl-navy);font-size:1.26rem;letter-spacing:-.018em;font-weight:800;}}
.edl-section-head p {{margin:.16rem 0 0;color:var(--edl-muted);font-size:.78rem;}}
.edl-section-badge {{white-space:nowrap;border:1px solid rgba(199,139,18,.25);background:#FFF8E8;color:#815B08;border-radius:999px;padding:.32rem .56rem;font-size:.66rem;font-weight:760;}}
.edl-panel {{background:#FFF;border:1px solid var(--edl-border);border-radius:13px;padding:.9rem 1rem;box-shadow:0 4px 18px rgba(16,24,40,.04);}}

.edl-metric-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:.62rem;margin:.08rem 0 .85rem;}}
.edl-metric-card {{position:relative;min-height:106px;background:#FFF;border:1px solid var(--edl-border);border-radius:12px;padding:.78rem .84rem;box-shadow:0 4px 16px rgba(16,24,40,.04);overflow:hidden;}}
.edl-metric-card:after {{content:"";position:absolute;right:-24px;top:-24px;width:80px;height:80px;border-radius:50%;background:color-mix(in srgb,var(--accent) 11%,transparent);}}
.edl-metric-icon {{position:absolute;right:.75rem;top:.66rem;width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:color-mix(in srgb,var(--accent) 11%,white);font-size:1.05rem;z-index:1;}}
.edl-metric-label {{color:#475467;font-size:.68rem;font-weight:750;max-width:70%;}}
.edl-metric-value {{color:var(--edl-navy);font-size:1.4rem;font-weight:830;line-height:1.12;margin:.38rem 0 .14rem;}}
.edl-metric-note {{color:var(--edl-muted);font-size:.66rem;}}

.edl-feature-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:.62rem;margin:.08rem 0 .85rem;}}
.edl-feature-card {{min-height:118px;background:#FFF;border:1px solid var(--edl-border);border-radius:12px;padding:.8rem;box-shadow:0 4px 16px rgba(16,24,40,.035);}}
.edl-feature-icon {{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:#F2F4F7;font-size:1.1rem;margin-bottom:.45rem;}}
.edl-feature-card h4 {{margin:0 0 .18rem;color:var(--edl-navy);font-size:.84rem;}}
.edl-feature-card p {{margin:0;color:var(--edl-muted);font-size:.70rem;line-height:1.42;}}

/* Dashboard hero */
.edl-dashboard-hero {{position:relative;isolation:isolate;overflow:hidden;min-height:245px;border-radius:14px;border:1px solid var(--edl-border);background:#FFF;box-shadow:0 7px 24px rgba(16,24,40,.055);padding:1.75rem 1.9rem;margin:.12rem 0 .85rem;}}
.edl-dashboard-hero:before {{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#FFF 0%,rgba(255,255,255,.98) 44%,rgba(255,255,255,.75) 61%,rgba(255,255,255,.14) 100%);z-index:-1;}}
.edl-dashboard-visual {{position:absolute;right:-1%;top:-10%;width:min(55%,650px);height:120%;object-fit:cover;object-position:center right;z-index:-2;filter:saturate(.88) contrast(1.03);}}
.edl-dashboard-hero h1 {{max-width:560px;color:var(--edl-navy);font-size:clamp(1.8rem,3.4vw,2.75rem);line-height:1.04;letter-spacing:-.04em;margin:0 0 .52rem;font-weight:850;}}
.edl-dashboard-hero h1 em {{color:var(--edl-gold);font-style:normal;}}
.edl-dashboard-hero p {{max-width:560px;color:#526077;font-size:.86rem;line-height:1.52;margin:0;}}
.edl-hero-tag {{display:inline-flex;align-items:center;gap:.35rem;background:#F3F6FA;color:var(--edl-navy);border:1px solid #E1E7EF;border-radius:999px;padding:.31rem .52rem;font-size:.64rem;font-weight:760;margin-bottom:.62rem;}}

/* Login */
.edl-login-hero {{position:relative;isolation:isolate;overflow:hidden;min-height:665px;border-radius:18px;padding:2.0rem;color:#FFF;background:linear-gradient(145deg,#05172F 0%,#08264C 58%,#061A36 100%);border:1px solid rgba(255,255,255,.08);box-shadow:0 20px 55px rgba(7,28,58,.19);}}
.edl-login-hero:before {{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,19,41,.98) 0%,rgba(5,24,50,.96) 50%,rgba(5,24,49,.52) 74%,rgba(5,24,49,.17) 100%);z-index:-1;}}
.edl-login-visual {{position:absolute;right:-6%;bottom:-4%;width:72%;height:96%;object-fit:cover;object-position:center right;z-index:-2;opacity:.91;filter:saturate(.87) contrast(1.04);}}
.edl-login-content {{position:relative;z-index:2;max-width:58%;}}
.edl-login-logo-shell {{display:inline-flex;background:#FFF;border-radius:14px;padding:.34rem;margin-bottom:1.1rem;box-shadow:0 12px 28px rgba(0,0,0,.20);}}
.edl-login-logo {{width:126px;height:126px;object-fit:contain;border-radius:10px;}}
.edl-login-hero .eyebrow {{color:#E9B839;font-size:.68rem;font-weight:820;letter-spacing:.14em;text-transform:uppercase;}}
.edl-login-hero h1 {{color:#FFF;font-size:clamp(2rem,3.8vw,3.05rem);letter-spacing:-.04em;line-height:1.03;margin:.48rem 0 .72rem;font-weight:850;}}
.edl-login-hero h1 em {{color:#F0BD3F;font-style:normal;}}
.edl-login-hero p {{color:rgba(255,255,255,.78);font-size:.82rem;line-height:1.58;margin:0;max-width:480px;}}
.edl-login-points {{display:grid;grid-template-columns:1fr;gap:.56rem;margin-top:1.35rem;max-width:365px;}}
.edl-login-point {{display:flex;align-items:center;gap:.55rem;color:#FFF;font-size:.76rem;font-weight:650;}}
.edl-login-point span {{width:34px;height:34px;border-radius:9px;border:1px solid rgba(229,177,60,.32);background:rgba(255,255,255,.07);display:flex;align-items:center;justify-content:center;}}
.edl-login-foot {{position:absolute;left:2rem;right:2rem;bottom:1.3rem;color:rgba(255,255,255,.54);font-size:.66rem;border-top:1px solid rgba(255,255,255,.10);padding-top:.7rem;}}
.st-key-iars_auth_card {{background:#FFF!important;border:1px solid var(--edl-border)!important;border-radius:16px!important;box-shadow:0 18px 48px rgba(16,24,40,.10)!important;padding:.35rem!important;}}
.st-key-iars_auth_card .stTabs [data-baseweb="tab-list"] {{box-shadow:none;margin-bottom:.3rem;}}
.st-key-iars_auth_card .stTextInput input {{background:#F8FAFC;border-color:#D8E0EA;min-height:46px;}}
.st-key-iars_auth_card .stTextInput input:focus {{border-color:var(--edl-gold);box-shadow:0 0 0 3px rgba(199,139,18,.12);}}
.st-key-iars_auth_card h3 {{color:var(--edl-navy);}}

/* Process stepper */
.edl-stepper {{display:grid;grid-template-columns:repeat(var(--steps),1fr);gap:.2rem;background:#FFF;border:1px solid var(--edl-border);border-radius:11px;padding:.58rem .65rem;margin:.1rem 0 .75rem;box-shadow:0 3px 14px rgba(16,24,40,.035);}}
.edl-step {{position:relative;display:flex;align-items:center;gap:.42rem;min-width:0;color:#98A2B3;font-size:.67rem;font-weight:700;}}
.edl-step:not(:last-child):after {{content:"";height:1px;background:#E5E9F0;flex:1;margin-left:.2rem;}}
.edl-step-number {{width:23px;height:23px;flex:0 0 auto;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#F2F4F7;color:#667085;border:1px solid #E4E7EC;font-size:.63rem;}}
.edl-step.active {{color:var(--edl-navy);}}
.edl-step.active .edl-step-number {{background:#FFF4D9;color:#8B6108;border-color:#E9C46A;}}
.edl-step.done {{color:#344054;}}
.edl-step.done .edl-step-number {{background:#EAF7EF;color:var(--edl-green);border-color:#B9E4CA;}}

/* Lists */
.edl-list {{background:#FFF;border:1px solid var(--edl-border);border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(16,24,40,.035);}}
.edl-list-row {{display:grid;grid-template-columns:38px minmax(0,1fr) auto;gap:.58rem;align-items:center;padding:.66rem .72rem;border-bottom:1px solid #EEF1F5;}}
.edl-list-row:last-child {{border-bottom:0;}}
.edl-list-icon {{width:31px;height:31px;border-radius:9px;background:var(--tone,#EEF4FF);display:flex;align-items:center;justify-content:center;font-size:.92rem;}}
.edl-list-title {{color:var(--edl-navy);font-size:.74rem;font-weight:720;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.edl-list-sub {{color:var(--edl-muted);font-size:.64rem;margin-top:.08rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.edl-list-meta {{color:var(--edl-muted);font-size:.62rem;text-align:right;white-space:nowrap;}}
.edl-overview {{background:#FFF;border:1px solid var(--edl-border);border-radius:12px;overflow:hidden;box-shadow:0 4px 16px rgba(16,24,40,.035);}}
.edl-overview-row {{display:flex;align-items:center;justify-content:space-between;gap:.8rem;padding:.66rem .75rem;border-bottom:1px solid #EEF1F5;font-size:.70rem;}}
.edl-overview-row:last-child {{border-bottom:0;}}
.edl-overview-row strong {{color:var(--edl-navy);font-weight:700;}}
.edl-overview-row span {{color:var(--edl-muted);text-align:right;}}
.edl-overview-row .ok {{color:var(--edl-green);font-weight:750;}}

.edl-library-note {{display:flex;gap:.65rem;align-items:flex-start;padding:.76rem .84rem;border:1px solid #D5E2F4;background:#F6F9FE;border-radius:10px;margin:.2rem 0 .65rem;}}
.edl-library-note strong {{color:var(--edl-navy);font-size:.76rem;}}
.edl-library-note span {{color:var(--edl-muted);font-size:.70rem;}}

/* Streamlit widgets */
.stButton>button,.stDownloadButton>button,button[kind="primary"] {{border-radius:8px;font-weight:720;transition:.12s ease;min-height:39px;}}
.stButton>button:hover,.stDownloadButton>button:hover {{transform:translateY(-1px);box-shadow:0 6px 14px rgba(16,24,40,.10);}}
button[kind="primary"] {{background:linear-gradient(135deg,#B97905,#D9A01F)!important;color:#FFF!important;border:1px solid #A66B04!important;}}
[data-testid="stFileUploaderDropzone"] {{border:1.4px dashed #B8C8DD;background:#FBFCFE;border-radius:12px;padding:1.15rem;}}
[data-testid="stMetric"] {{background:#FFF;border:1px solid var(--edl-border);border-radius:11px;padding:.72rem .8rem;box-shadow:0 4px 14px rgba(16,24,40,.035);}}
[data-testid="stDataFrame"],[data-testid="stDataEditor"] {{border:1px solid var(--edl-border);border-radius:10px;overflow:hidden;box-shadow:0 4px 16px rgba(16,24,40,.035);}}
[data-testid="stAlert"] {{border-radius:9px;border-width:1px;}}
div[data-testid="stForm"],div[data-testid="stVerticalBlockBorderWrapper"] {{border-color:var(--edl-border)!important;border-radius:12px!important;box-shadow:0 4px 16px rgba(16,24,40,.035);background:#FFF;}}
.stTabs [data-baseweb="tab-list"] {{gap:.2rem;background:#FFF;border:1px solid var(--edl-border);padding:.22rem;border-radius:9px;box-shadow:0 3px 12px rgba(16,24,40,.03);}}
.stTabs [data-baseweb="tab"] {{border-radius:7px;padding:.42rem .64rem;color:var(--edl-muted);font-weight:680;font-size:.74rem;}}
.stTabs [aria-selected="true"] {{background:#FFF7E5!important;color:#7B5608!important;}}
.stTabs [data-baseweb="tab-highlight"] {{background-color:var(--edl-gold)!important;}}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div {{border-radius:8px!important;}}
.st-key-extract_upload_action [data-testid="stRadio"] > div {{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:.65rem;}}
.st-key-extract_upload_action [data-testid="stRadio"] label {{min-height:78px;border:1px solid var(--edl-border);border-radius:11px;padding:.7rem .75rem;background:#FFF;align-items:flex-start;box-shadow:0 3px 12px rgba(16,24,40,.03);}}
.st-key-extract_upload_action [data-testid="stRadio"] label:hover {{border-color:#C9A04B;box-shadow:0 6px 17px rgba(16,24,40,.06);}}
.st-key-extract_upload_action [data-testid="stRadio"] label:has(input:checked) {{border-color:#D3A12D;background:#FFF9EC;box-shadow:0 0 0 3px rgba(200,138,8,.09);}}
.st-key-extract_upload_action [data-testid="stRadio"] label p {{font-size:.72rem;line-height:1.35;font-weight:680;color:var(--edl-navy);}}

@media(max-width:1000px) {{
  .edl-topbar-date,.edl-user-chip{{display:none}} .edl-login-hero{{min-height:600px}} .edl-login-content{{max-width:66%}} .edl-login-visual{{width:76%;opacity:.76}}
}}
@media(max-width:720px) {{
  .block-container{{padding-left:.75rem;padding-right:.75rem}} .edl-dashboard-hero{{padding:1.2rem;min-height:220px}} .edl-dashboard-visual{{width:100%;opacity:.20}}
  .edl-login-hero{{min-height:560px;padding:1.2rem}} .edl-login-content{{max-width:100%}} .edl-login-visual{{width:100%;opacity:.22}}
  .edl-login-foot{{left:1.2rem;right:1.2rem}} .edl-stepper{{grid-template-columns:1fr}} .edl-step:not(:last-child):after{{display:none}}
  .st-key-extract_upload_action [data-testid="stRadio"] > div {{grid-template-columns:1fr!important;}}
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
        f'<div class="edl-sidebar-logo-shell">{image}</div>'
        '<h3>INTERNAL AUDIT<br>REPORT SYSTEM</h3>'
        '<p>EDL GROUP OF COMPANIES</p>'
        '</div>'
        '<div class="edl-sidebar-section">Workspace</div>'
    )


def render_app_header(user: dict[str, Any], *, version: str, page_title: str = "Dashboard") -> None:
    name = html.escape(str(user.get("full_name") or user.get("username") or "IARS User"))
    role = "Administrator" if str(user.get("role", "")).lower() == "admin" else "Auditor"
    initials = "".join(part[:1].upper() for part in name.split()[:2]) or "IA"
    date_text = datetime.now().strftime("%b %d, %Y · %I:%M %p")
    subtitles = {
        "Dashboard": "Overview of the Internal Audit Report System",
        "Generate Extraction": "Upload audit reports, extract data and prepare import-ready records",
        "PDF Tagging": "Review, tag and archive audit-report PDFs",
        "Shared PDF Archive": "Browse shared audit reports uploaded by all authorized auditors",
        "Report Templates": "Access reusable count sheets, working papers and report templates",
        "Policies & Memoranda": "Access controlled policies, memoranda, procedures and manuals",
        "User Management": "Manage authorized accounts and account approvals",
        "Master Data": "Maintain the reference workbook used across IARS",
        "Settings": "Review system configuration, security and storage controls",
    }
    subtitle = subtitles.get(page_title, "EDL GROUP OF COMPANIES Internal Audit workspace")
    _render_html(
        '<div class="edl-topbar">'
        f'<div class="edl-topbar-title"><h1>{html.escape(page_title)}</h1><p>{html.escape(subtitle)}</p></div>'
        '<div class="edl-topbar-spacer"></div>'
        f'<div class="edl-topbar-date">{html.escape(date_text)} · v{html.escape(version)}</div>'
        f'<div class="edl-user-chip"><div class="edl-user-avatar">{html.escape(initials)}</div>'
        f'<div><strong>{name}</strong><span>{role}</span></div></div></div>'
    )


def render_login_hero() -> None:
    logo = _logo_data_uri()
    audit_image = _audit_image_data_uri()
    logo_html = (
        f'<div class="edl-login-logo-shell"><img class="edl-login-logo" src="{logo}" alt="EDL GROUP OF COMPANIES logo"></div>'
        if logo else ""
    )
    visual_html = (
        f'<img class="edl-login-visual" src="{audit_image}" alt="Internal audit reports and compliance workpapers">'
        if audit_image else ""
    )
    _render_html(
        '<div class="edl-login-hero">'
        f'{visual_html}<div class="edl-login-content">{logo_html}'
        '<div class="eyebrow">EDL GROUP OF COMPANIES</div>'
        '<h1>Secure Internal Audit <em>Workspace.</em></h1>'
        '<p>A secure and centralized workspace for managing internal audit reports, shared archives, templates, policies and controlled records.</p>'
        '<div class="edl-login-points">'
        '<div class="edl-login-point"><span>🛡️</span>Admin-approved access</div>'
        '<div class="edl-login-point"><span>📄</span>Smart report extraction</div>'
        '<div class="edl-login-point"><span>🗂️</span>Shared PDF and document libraries</div>'
        '<div class="edl-login-point"><span>✅</span>Controlled and traceable records</div>'
        '</div></div><div class="edl-login-foot">Secure · Confidential · Authorized Internal Audit personnel only</div></div>'
    )


def render_dashboard_hero() -> None:
    audit_image = _audit_image_data_uri()
    visual_html = (
        f'<img class="edl-dashboard-visual" src="{audit_image}" alt="Internal audit reports and workpapers">'
        if audit_image else ""
    )
    _render_html(
        '<div class="edl-dashboard-hero">'
        f'{visual_html}<div class="edl-hero-tag">🛡️ Internal Audit Digital Workspace</div>'
        '<h1>Delivering Integrity.<br>Driving <em>Assurance.</em></h1>'
        '<p>Empowering the Internal Audit team with secure tools, accurate data, reusable resources and controlled records for confident decision-making.</p>'
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


def render_stepper(labels: Sequence[str], active_index: int = 0) -> None:
    chunks: list[str] = []
    for index, label in enumerate(labels):
        state = "done" if index < active_index else "active" if index == active_index else ""
        mark = "✓" if index < active_index else str(index + 1)
        chunks.append(
            f'<div class="edl-step {state}"><div class="edl-step-number">{html.escape(mark)}</div>'
            f'<span>{html.escape(label)}</span></div>'
        )
    _render_html(f'<div class="edl-stepper" style="--steps:{len(labels)}">{"".join(chunks)}</div>')


def render_activity_list(rows: Iterable[dict[str, Any]]) -> None:
    chunks: list[str] = []
    palette = ["#EEF4FF", "#ECFDF3", "#FFF6E5", "#F4F0FF"]
    for index, row in enumerate(rows):
        icon = html.escape(str(row.get("icon", "📄")))
        title = html.escape(str(row.get("title", "")))
        subtitle = html.escape(str(row.get("subtitle", "")))
        meta = html.escape(str(row.get("meta", "")))
        chunks.append(
            f'<div class="edl-list-row"><div class="edl-list-icon" style="--tone:{palette[index % len(palette)]}">{icon}</div>'
            f'<div><div class="edl-list-title">{title}</div><div class="edl-list-sub">{subtitle}</div></div>'
            f'<div class="edl-list-meta">{meta}</div></div>'
        )
    if not chunks:
        chunks.append('<div class="edl-list-row"><div class="edl-list-icon">ℹ️</div><div><div class="edl-list-title">No recent activity</div><div class="edl-list-sub">New archive activity will appear here.</div></div><div></div></div>')
    _render_html(f'<div class="edl-list">{"".join(chunks)}</div>')


def render_system_overview(rows: Iterable[dict[str, Any]]) -> None:
    chunks: list[str] = []
    for row in rows:
        label = html.escape(str(row.get("label", "")))
        value = html.escape(str(row.get("value", "")))
        ok = bool(row.get("ok", False))
        cls = "ok" if ok else ""
        chunks.append(f'<div class="edl-overview-row"><strong>{label}</strong><span class="{cls}">{value}</span></div>')
    _render_html(f'<div class="edl-overview">{"".join(chunks)}</div>')


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
    _render_html('<div class="edl-sidebar-section">Account</div>')
    _render_html(
        '<div class="edl-user-card">'
        f'<strong>{name}</strong><span>@{username} · {role}</span></div>'
    )


def render_library_note(title: str, detail: str, icon: str = "ℹ️") -> None:
    _render_html(
        '<div class="edl-library-note">'
        f'<div>{html.escape(icon)}</div><div><strong>{html.escape(title)}</strong><br><span>{html.escape(detail)}</span></div></div>'
    )
