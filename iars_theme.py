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
    """Render trusted local HTML and CSS consistently across Streamlit versions."""
    # st.markdown with explicit HTML permission is more reliable for the custom
    # styling used by IARS, while all inserted user text is escaped by callers.
    st.markdown(fragment.strip(), unsafe_allow_html=True)


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
.block-container {{max-width:1580px;padding:.35rem 1.55rem 3rem;}}
header[data-testid="stHeader"] {{height:0!important;min-height:0!important;background:transparent!important;border-bottom:0!important;box-shadow:none!important;}}
#MainMenu,footer {{visibility:hidden;}}
[data-testid="stToolbar"] {{top:.08rem;}}

/* Sidebar */
section[data-testid="stSidebar"] {{background:linear-gradient(180deg,#05162E 0%,#07264D 58%,#061A36 100%);border-right:1px solid rgba(255,255,255,.08);}}
section[data-testid="stSidebar"] > div {{padding-top:0;}}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{position:absolute!important;top:2px!important;right:4px!important;z-index:5!important;height:28px!important;min-height:28px!important;padding:0!important;background:transparent!important;}}
section[data-testid="stSidebar"] [data-testid="stLogoSpacer"] {{display:none!important;}}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{margin-left:auto!important;align-self:center!important;}}
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
section[data-testid="stSidebar"] .stButton>button {{
  border-radius:9px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);color:#FFF;
  display:flex!important;align-items:center!important;justify-content:flex-start!important;text-align:left!important;
  padding-left:.78rem!important;padding-right:.65rem!important;
}}
section[data-testid="stSidebar"] .stButton>button > div,
section[data-testid="stSidebar"] .stButton>button > div > span,
section[data-testid="stSidebar"] .stButton>button [data-testid="stMarkdownContainer"] {{
  width:100%!important;display:flex!important;align-items:center!important;justify-content:flex-start!important;
}}
section[data-testid="stSidebar"] .stButton>button p {{width:100%!important;text-align:left!important;margin:0!important;}}
section[data-testid="stSidebar"] .stButton>button:hover {{background:rgba(199,139,18,.22);border-color:rgba(229,177,60,.48);}}
section[data-testid="stSidebar"] [data-testid="stExpander"] {{border:1px solid rgba(255,255,255,.12);border-radius:10px;background:rgba(255,255,255,.05);margin:.18rem 0 .35rem;overflow:hidden;}}
section[data-testid="stSidebar"] [data-testid="stExpander"] details {{background:transparent;}}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{padding:.2rem .38rem .15rem;justify-content:flex-start!important;text-align:left!important;}}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary p {{color:#FFF!important;font-weight:720;text-align:left!important;width:100%!important;}}
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {{padding:0 .18rem .2rem;}}
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] .stButton>button {{padding-left:1rem!important;}}

.edl-sidebar-brand {{text-align:center;padding:0 .15rem .55rem;}}
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
.edl-topbar {{position:relative;display:flex;align-items:center;gap:1rem;padding:.72rem .9rem;background:linear-gradient(112deg,#061A36 0%,#0A2C59 68%,#123F78 100%);border:1px solid rgba(228,174,47,.42);border-radius:12px;box-shadow:0 8px 22px rgba(6,26,54,.16);margin:-16px 0 .62rem;overflow:hidden;}}
.edl-topbar:after {{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,#E4AE2F 0 32%,#1F6FDA 32% 56%,#149A49 56% 78%,#E62D32 78% 100%);opacity:.95;}}
.edl-topbar-title {{min-width:0;position:relative;z-index:1;}}
.edl-topbar-title h1 {{margin:0!important;padding:0!important;color:#FFF;font-size:1.34rem;font-weight:820;letter-spacing:-.025em;}}
.edl-topbar-title p {{margin:.16rem 0 0;color:#D7E2F1;font-size:.75rem;}}
.edl-topbar-spacer {{flex:1;}}
.edl-topbar-date {{position:relative;z-index:1;color:#D8E3F2;font-size:.72rem;white-space:nowrap;font-weight:560;}}
.edl-user-chip {{position:relative;z-index:1;display:flex;align-items:center;gap:.58rem;background:rgba(255,255,255,.10);border:1px solid rgba(228,174,47,.55);border-radius:10px;padding:.44rem .62rem;min-width:174px;box-shadow:inset 0 1px 0 rgba(255,255,255,.09);}}
.edl-user-avatar {{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#F6D46B,#C88A08);color:#061A36;font-size:.76rem;font-weight:850;box-shadow:0 3px 10px rgba(0,0,0,.18);}}
.edl-user-chip strong {{display:block;color:#FFF;font-size:.78rem;font-weight:780;}}
.edl-user-chip span {{display:block;color:#F2CF68;font-size:.65rem;margin-top:.04rem;font-weight:650;}}
.edl-brand-stripe {{height:3px;border-radius:99px;background:linear-gradient(90deg,#1F6FDA 0 24%,#149A49 24% 49%,#E5B22D 49% 74%,#E62D32 74% 100%);margin-bottom:.45rem;}}

/* Page headings and cards */
.edl-section-head {{display:flex;align-items:flex-end;justify-content:space-between;gap:1rem;margin:.35rem 0 .72rem;}}
.edl-section-head h2 {{margin:0!important;padding:0!important;color:var(--edl-navy);font-size:1.26rem;letter-spacing:-.018em;font-weight:800;}}
.edl-section-head p {{margin:.16rem 0 0;color:var(--edl-muted);font-size:.78rem;}}
.edl-section-badge {{white-space:nowrap;border:1px solid rgba(199,139,18,.25);background:#FFF8E8;color:#815B08;border-radius:999px;padding:.32rem .56rem;font-size:.66rem;font-weight:760;}}
.edl-panel {{background:#FFF;border:1px solid var(--edl-border);border-radius:13px;padding:.9rem 1rem;box-shadow:0 4px 18px rgba(16,24,40,.04);}}

.edl-metric-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:.68rem;margin:.08rem 0 .92rem;}}
.edl-metric-card {{position:relative;min-height:116px;background:linear-gradient(150deg,#FFFFFF 0%,color-mix(in srgb,var(--accent) 7%,#FFFFFF) 100%);border:1px solid color-mix(in srgb,var(--accent) 24%,#DCE3EC);border-top:4px solid var(--accent);border-radius:12px;padding:.82rem 1rem .84rem .9rem;box-shadow:0 6px 18px rgba(16,24,40,.06);overflow:hidden;}}
.edl-metric-card:after {{content:"";position:absolute;right:0;top:-28px;width:78px;height:78px;border-radius:50%;background:color-mix(in srgb,var(--accent) 10%,transparent);}}
.edl-metric-icon {{position:absolute;right:.72rem;top:.68rem;width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;background:color-mix(in srgb,var(--accent) 15%,#FFFFFF);border:1px solid color-mix(in srgb,var(--accent) 26%,#FFFFFF);font-size:1.08rem;z-index:1;box-shadow:0 2px 7px rgba(16,24,40,.05);}}
.edl-metric-label {{color:#344054;font-size:.71rem;font-weight:800;letter-spacing:.005em;padding-right:3rem;max-width:none;}}
.edl-metric-value {{color:#061A36;font-size:1.34rem;font-weight:850;line-height:1.12;margin:.4rem 0 .18rem;letter-spacing:-.018em;padding-right:3rem;max-width:none;overflow-wrap:anywhere;word-break:break-word;}}
.edl-metric-value.long {{font-size:1.05rem;line-height:1.18;}}
.edl-metric-note {{color:#596780;font-size:.68rem;font-weight:560;line-height:1.3;padding-right:2.6rem;max-width:none;}}

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
.edl-list {{background:linear-gradient(180deg,#FFFFFF 0%,#FCFDFE 100%);border:1px solid #DCE6F2;border-radius:12px;overflow:hidden;box-shadow:0 5px 16px rgba(16,24,40,.04);}}
.edl-list-row {{display:grid;grid-template-columns:38px minmax(0,1fr) auto;gap:.58rem;align-items:center;padding:.72rem .78rem;border-bottom:1px solid #EEF1F5;background:linear-gradient(90deg,var(--rowtone,#FFFFFF) 0%,#FFFFFF 18%);}}
.edl-list-row:last-child {{border-bottom:0;}}
.edl-list-icon {{width:31px;height:31px;border-radius:9px;background:var(--tone,#EEF4FF);display:flex;align-items:center;justify-content:center;font-size:.92rem;}}
.edl-list-title {{color:var(--edl-navy);font-size:.74rem;font-weight:760;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.edl-list-sub {{color:#5B6B82;font-size:.64rem;margin-top:.08rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.edl-list-meta {{color:#526077;font-size:.62rem;text-align:right;white-space:nowrap;font-weight:620;}}
.edl-overview {{background:linear-gradient(180deg,#FFFFFF 0%,#FCFDFE 100%);border:1px solid #DCE6F2;border-radius:12px;overflow:hidden;box-shadow:0 5px 16px rgba(16,24,40,.04);}}
.edl-overview-row {{display:flex;align-items:center;justify-content:space-between;gap:.8rem;padding:.72rem .78rem;border-bottom:1px solid #EEF1F5;font-size:.70rem;}}
.edl-overview-row:last-child {{border-bottom:0;}}
.edl-overview-row strong {{color:var(--edl-navy);font-weight:760;}}
.edl-overview-row span {{color:var(--edl-muted);text-align:right;display:inline-flex;align-items:center;justify-content:center;padding:.22rem .55rem;border-radius:999px;min-height:24px;white-space:normal;line-height:1.1;max-width:58%;font-size:.66rem;font-weight:760;word-break:break-word;}}
.edl-overview-row .ok {{color:#0F7A43;font-weight:780;background:#ECFDF3;border:1px solid #ABEFC6;}}
.edl-overview-row .warn {{color:#9A3412;font-weight:780;background:#FFF2E8;border:1px solid #F7CFA8;}}
.edl-overview-row .neutral {{color:#175CD3;font-weight:780;background:#EEF4FF;border:1px solid #C7D7FE;}}

/* Dashboard quick actions */
.st-key-dash_action_generate button,
.st-key-dash_action_archive button,
.st-key-dash_action_tagging button,
.st-key-dash_action_workpapers button,
.st-key-dash_action_policies button,
.st-key-dash_action_users button {{font-weight:760!important;border-width:1px!important;box-shadow:0 4px 12px rgba(16,24,40,.045)!important;}}
.st-key-dash_action_generate button {{background:linear-gradient(135deg,#061A36,#0A2C59)!important;color:#FFF!important;border-color:#061A36!important;}}
.st-key-dash_action_archive button {{background:#F4F0FF!important;color:#4C1D95!important;border-color:#D8C7FF!important;}}
.st-key-dash_action_tagging button {{background:#FFF8E8!important;color:#7A5200!important;border-color:#F0D58E!important;}}
.st-key-dash_action_workpapers button {{background:#ECFDF3!important;color:#116B3B!important;border-color:#ABEFC6!important;}}
.st-key-dash_action_policies button {{background:#EAFBFD!important;color:#0A6570!important;border-color:#AEE3E9!important;}}
.st-key-dash_action_users button {{background:#EEF4FF!important;color:#174EA6!important;border-color:#C7D7FE!important;}}
.st-key-dash_action_archive button:hover,
.st-key-dash_action_tagging button:hover,
.st-key-dash_action_workpapers button:hover,
.st-key-dash_action_policies button:hover,
.st-key-dash_action_users button:hover {{filter:brightness(.98);transform:translateY(-1px)!important;}}

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


/* v4.2: native Streamlit image and navigation layout for reliable rendering */
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{display:none!important;}}
section[data-testid="stSidebar"] [data-testid="stImage"] {{display:flex;justify-content:center;margin:0 auto .25rem!important;}}
section[data-testid="stSidebar"] [data-testid="stImage"] img {{width:126px!important;height:126px!important;object-fit:contain;background:#FFF;border-radius:16px;padding:5px;box-shadow:0 12px 28px rgba(0,0,0,.24);}}
section[data-testid="stSidebar"] .stButton {{margin:.08rem 0;}}
section[data-testid="stSidebar"] .stButton>button {{width:100%;justify-content:flex-start;text-align:left;min-height:43px;padding:.52rem .68rem;font-size:.78rem;}}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"] {{background:transparent!important;border-color:transparent!important;box-shadow:none!important;color:#F8FAFC!important;}}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover {{background:rgba(255,255,255,.08)!important;border-color:rgba(255,255,255,.08)!important;}}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] {{background:linear-gradient(135deg,#B87905,#DCA423)!important;border-color:#DCA423!important;box-shadow:0 7px 18px rgba(199,139,18,.25)!important;color:#FFF!important;}}


.st-key-edl_dashboard_hero_panel {{background:#FFF;border:1px solid var(--edl-border);border-radius:14px;padding:1.15rem 1.3rem;box-shadow:0 7px 24px rgba(16,24,40,.055);margin:.12rem 0 .85rem;overflow:hidden;}}
.st-key-edl_dashboard_hero_panel [data-testid="stImage"] img {{border-radius:12px;max-height:300px;object-fit:cover;object-position:center;}}
.st-key-edl_dashboard_hero_panel .edl-native-dashboard-copy {{padding:.65rem .35rem .35rem;}}
.st-key-edl_dashboard_hero_panel .edl-native-dashboard-copy h1 {{color:var(--edl-navy);font-size:clamp(1.8rem,3.1vw,2.65rem);line-height:1.04;letter-spacing:-.04em;margin:.45rem 0 .55rem;font-weight:850;}}
.st-key-edl_dashboard_hero_panel .edl-native-dashboard-copy h1 em {{color:var(--edl-gold);font-style:normal;}}
.st-key-edl_dashboard_hero_panel .edl-native-dashboard-copy p {{color:var(--edl-muted);font-size:.82rem;line-height:1.58;max-width:560px;}}
.edl-native-hero-tag {{display:inline-flex;align-items:center;gap:.38rem;color:#815B08;border:1px solid rgba(199,139,18,.28);background:#FFF8E8;border-radius:999px;padding:.32rem .55rem;font-size:.66rem;font-weight:760;}}


/* v4.4 exact-reference refinements */
section[data-testid="stSidebar"] {{width:238px!important;min-width:238px!important;}}
section[data-testid="stSidebar"] > div:first-child {{padding:18px 10px 18px!important;}}
section[data-testid="stSidebar"] [data-testid="stImage"] img {{background:transparent!important;border:none!important;box-shadow:none!important;}}
section[data-testid="stSidebar"] .stButton>button {{min-height:40px!important;border:none!important;background:transparent!important;text-align:left!important;font-weight:620!important;padding:.46rem .62rem!important;}}
section[data-testid="stSidebar"] .stButton>button:hover {{background:rgba(255,255,255,.08)!important;}}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] {{background:linear-gradient(135deg,#B77B05,#D99D19)!important;color:#fff!important;box-shadow:0 6px 15px rgba(186,124,5,.22)!important;}}
.stButton>button[kind="primary"], .stFormSubmitButton>button, [data-testid="stDownloadButton"]>button {{background:#061A36!important;color:white!important;border:1px solid #061A36!important;border-radius:6px!important;box-shadow:none!important;}}
.stButton>button[kind="primary"]:hover, .stFormSubmitButton>button:hover, [data-testid="stDownloadButton"]>button:hover {{background:#0A2C59!important;border-color:#0A2C59!important;}}
.stButton>button[kind="secondary"] {{border:1px solid #C7D0DD!important;background:#fff!important;color:#061A36!important;border-radius:6px!important;}}
/* Dashboard action colors override the global button theme. */
.stElementContainer.st-key-dash_action_generate .stButton>button[kind="primary"] {{background:linear-gradient(135deg,#061A36,#0A2C59)!important;color:#FFF!important;border-color:#061A36!important;}}
.stElementContainer.st-key-dash_action_archive .stButton>button[kind="secondary"] {{background:#F4F0FF!important;color:#4C1D95!important;border-color:#D8C7FF!important;}}
.stElementContainer.st-key-dash_action_tagging .stButton>button[kind="secondary"] {{background:#FFF8E8!important;color:#7A5200!important;border-color:#F0D58E!important;}}
.stElementContainer.st-key-dash_action_workpapers .stButton>button[kind="secondary"] {{background:#ECFDF3!important;color:#116B3B!important;border-color:#ABEFC6!important;}}
.stElementContainer.st-key-dash_action_policies .stButton>button[kind="secondary"] {{background:#EAFBFD!important;color:#0A6570!important;border-color:#AEE3E9!important;}}
.stElementContainer.st-key-dash_action_users .stButton>button[kind="secondary"] {{background:#EEF4FF!important;color:#174EA6!important;border-color:#C7D7FE!important;}}
.stTabs [data-baseweb="tab-list"] {{gap:0!important;border-bottom:1px solid #D9E0EA!important;background:#fff!important;}}
.stTabs [data-baseweb="tab"] {{border-radius:0!important;padding:.65rem .9rem!important;color:#475467!important;}}
.stTabs [aria-selected="true"] {{color:#061A36!important;border-bottom:2px solid #C88A08!important;background:#fff!important;}}
[data-testid="stMetric"] {{background:#fff;border:1px solid #E1E6EE;border-radius:8px;padding:.68rem .76rem;}}
.edl-panel,.edl-metric-card,.edl-feature-card,.edl-topbar {{border-radius:8px!important;box-shadow:0 2px 8px rgba(16,24,40,.035)!important;}}
.edl-topbar {{padding:.58rem .72rem!important;}}
.edl-metric-grid {{grid-template-columns:repeat(6,minmax(0,1fr))!important;gap:.48rem!important;}}
.edl-metric-card {{min-height:104px!important;padding:.7rem .74rem!important;}}
.edl-metric-value {{font-size:1.22rem!important;}}
@media(max-width:1200px){{.edl-metric-grid{{grid-template-columns:repeat(3,minmax(0,1fr))!important;}}}}
@media(max-width:760px){{.edl-metric-grid{{grid-template-columns:repeat(2,minmax(0,1fr))!important;}}section[data-testid="stSidebar"]{{width:230px!important;min-width:230px!important;}}}}


@media(max-width:1000px) {{
  .edl-topbar-date,.edl-user-chip{{display:none}}
}}
@media(max-width:720px) {{
  .block-container{{padding-left:.75rem;padding-right:.75rem}}
  .edl-dashboard-hero{{padding:1.2rem;min-height:220px}}
  .edl-dashboard-visual{{width:100%;opacity:.20}}
  .edl-stepper{{grid-template-columns:1fr}}
  .edl-step:not(:last-child):after{{display:none}}
  .st-key-extract_upload_action [data-testid="stRadio"] > div{{grid-template-columns:1fr!important;}}
  .st-key-edl_dashboard_hero_panel{{padding:.8rem}}
}}

/* IARS LOGIN — SINGLE AUTHORITATIVE SECTION */
@keyframes iarsAuthPanelIn {{
  from {{opacity:0;transform:translateY(8px)}}
  to {{opacity:1;transform:translateY(0)}}
}}
@keyframes iarsLoginMaskOut {{
  from {{opacity:1;visibility:visible}}
  to {{opacity:0;visibility:hidden}}
}}
@keyframes iarsLoginSpinner {{to {{transform:rotate(360deg)}}}}

.iars-login-marker,
.iars-auth-view-marker,
.iars-signin-view,
.iars-signup-view,
.iars-verify-view,
.iars-forgot-view,
.iars-app-ready-marker {{display:none!important;}}

html:has(.iars-login-marker),
body:has(.iars-login-marker),
.stApp:has(.iars-login-marker) {{
  width:100%!important;
  height:100dvh!important;
  min-height:100dvh!important;
  overflow:hidden!important;
  background:#F4F6FA!important;
}}
.stApp:has(.iars-login-marker) header[data-testid="stHeader"],
.stApp:has(.iars-login-marker) section[data-testid="stSidebar"],
.stApp:has(.iars-login-marker) [data-testid="stToolbar"],
.stApp:has(.iars-login-marker) [data-testid="stDecoration"],
.stApp:has(.iars-login-marker) [data-testid="stStatusWidget"] {{display:none!important;}}
.stApp:has(.iars-login-marker) [data-testid="stAppViewContainer"],
.stApp:has(.iars-login-marker) [data-testid="stMain"],
.stApp:has(.iars-login-marker) .main {{
  width:100%!important;
  height:100dvh!important;
  min-height:100dvh!important;
  overflow:hidden!important;
  background:#F4F6FA!important;
}}
.stApp:has(.iars-login-marker) .block-container {{
  width:100%!important;
  max-width:none!important;
  height:100dvh!important;
  min-height:100dvh!important;
  padding:8px!important;
  overflow:hidden!important;
}}
.stApp:has(.iars-login-marker) .block-container > div[data-testid="stVerticalBlock"] {{
  height:100%!important;
  min-height:0!important;
  gap:0!important;
  overflow:hidden!important;
}}
.st-key-iars_login_shell {{
  flex:0 0 calc(100dvh - 16px)!important;
  gap:0!important;
  align-items:stretch!important;
}}
.st-key-iars_login_shell > div[data-testid="stLayoutWrapper"] {{
  width:100%!important;
  height:100%!important;
  min-height:0!important;
  flex:1 1 auto!important;
}}
.st-key-iars_login_shell > div[data-testid="stLayoutWrapper"] > div[data-testid="stHorizontalBlock"] {{
  width:100%!important;
  height:100%!important;
  min-height:0!important;
  flex:1 1 auto!important;
}}
.st-key-iars_login_shell,
.st-key-iars_login_shell > div[data-testid="stVerticalBlock"],
.st-key-iars_login_shell [data-testid="stHorizontalBlock"] {{
  width:100%!important;
  height:calc(100dvh - 16px)!important;
  min-height:0!important;
  max-height:calc(100dvh - 16px)!important;
}}
.st-key-iars_login_shell [data-testid="stHorizontalBlock"] {{
  align-items:stretch!important;
  gap:10px!important;
}}
.st-key-iars_login_shell [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
  height:auto!important;
  min-height:0!important;
  max-height:100%!important;
  min-width:0!important;
  align-self:stretch!important;
  display:flex!important;
}}
.st-key-iars_login_shell [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  min-width:0!important;
  flex:1 1 auto!important;
  gap:0!important;
  align-items:stretch!important;
}}
.st-key-iars_login_shell [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stLayoutWrapper"] {{
  width:100%!important;
  height:100%!important;
  min-height:0!important;
  flex:1 1 auto!important;
}}

.st-key-edl_login_hero_panel,
.st-key-edl_login_hero_panel > div,
.st-key-edl_login_hero_panel [data-testid="stImage"],
.st-key-edl_login_hero_panel [data-testid="stImage"] > div {{
  width:100%!important;
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  margin:0!important;
  padding:0!important;
  overflow:hidden!important;
  border-radius:16px!important;
}}
.st-key-edl_login_hero_panel {{
  background:#061A36!important;
  border:0!important;
  box-shadow:0 14px 36px rgba(5,24,50,.18)!important;
  clip-path:inset(0 round 16px)!important;
}}
.st-key-edl_login_hero_panel img {{
  display:block!important;
  width:100%!important;
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  object-fit:cover!important;
  object-position:center center!important;
  border-radius:16px!important;
  clip-path:inset(0 round 16px)!important;
}}

.st-key-iars_auth_card {{
  width:100%!important;
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:center!important;
  background:#FFF!important;
  border:1px solid #DCE3EC!important;
  border-radius:16px!important;
  padding:clamp(18px,3vh,28px) clamp(30px,4.1vw,58px)!important;
  box-shadow:0 14px 36px rgba(16,24,40,.08)!important;
  overflow:hidden!important;
}}
.st-key-iars_auth_card {{
  align-items:stretch!important;
  gap:8px!important;
  overflow-y:auto!important;
  scrollbar-width:thin;
}}
.st-key-iars_auth_card > * {{
  width:100%!important;
  max-width:570px!important;
  margin-left:auto!important;
  margin-right:auto!important;
  flex-shrink:0!important;
}}
.st-key-iars_auth_card:has(.iars-auth-view-marker) {{
  animation:iarsAuthPanelIn .22s cubic-bezier(.22,.61,.36,1) both;
  justify-content:flex-start!important;
}}
.st-key-iars_auth_card:has(.iars-signup-view),
.st-key-iars_auth_card:has(.iars-verify-view),
.st-key-iars_auth_card:has(.iars-forgot-view) {{
  justify-content:flex-start!important;
  overflow-y:auto!important;
  padding-top:18px!important;
  scroll-padding-top:18px!important;
}}
.st-key-iars_auth_card:has(.iars-signin-view) {{
  justify-content:flex-start!important;
  overflow:visible!important;
}}
.st-key-iars_auth_card > div[data-testid="stElementContainer"]:has(.edl-login-authorized) {{
  margin-top:auto!important;
}}

.edl-auth-title {{text-align:center;margin:clamp(8px,2.6vh,22px) 0 clamp(8px,1.5vh,13px)!important;}}
.edl-auth-title h1 {{
  margin:0!important;
  color:#061A36!important;
  font-size:clamp(1.8rem,3.5vh,2.4rem)!important;
  font-weight:850!important;
  letter-spacing:-.035em!important;
  line-height:1.08!important;
}}
.edl-auth-title p {{
  margin:.42rem 0 0!important;
  color:#667085!important;
  font-size:clamp(.82rem,1.55vh,1rem)!important;
}}
.stApp:has(.iars-login-marker) div[data-testid="stForm"] {{
  margin:0!important;
  padding:0!important;
  border:0!important;
  border-radius:0!important;
  background:transparent!important;
  box-shadow:none!important;
}}
.stApp:has(.iars-login-marker) .stTextInput {{margin:0!important;}}
.stApp:has(.iars-login-marker) .stTextInput label p {{
  margin:0!important;
  color:#061A36!important;
  font-size:.95rem!important;
  font-weight:720!important;
  line-height:1.25!important;
}}
.stApp:has(.iars-login-marker) .stTextInput [data-baseweb="input"] {{
  width:100%!important;
  min-height:52px!important;
  background:#FFF!important;
  border:1.5px solid #C9D3E0!important;
  border-radius:8px!important;
  box-shadow:none!important;
  overflow:hidden!important;
}}
.stApp:has(.iars-login-marker) .stTextInput [data-baseweb="input"]:focus-within {{
  border-color:#174A86!important;
  box-shadow:0 0 0 3px rgba(23,74,134,.10)!important;
}}
.stApp:has(.iars-login-marker) .stTextInput input {{
  width:100%!important;
  min-height:49px!important;
  padding:.68rem 1rem!important;
  color:#101828!important;
  background:transparent!important;
  border:0!important;
  border-radius:0!important;
  outline:0!important;
  box-shadow:none!important;
  font-size:.98rem!important;
}}
.st-key-auth_signin_username input {{
  padding-left:3rem!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' stroke='%2366788F' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 21a8 8 0 0 0-16 0'/%3E%3Ccircle cx='12' cy='7' r='4'/%3E%3C/svg%3E")!important;
  background-repeat:no-repeat!important;
  background-position:1rem center!important;
  background-size:1.2rem 1.2rem!important;
}}
.stApp:has(.iars-login-marker) .stTextInput [data-baseweb="input"] button {{
  align-self:stretch!important;
  min-width:48px!important;
  margin:0!important;
  padding:0 14px!important;
  background:transparent!important;
  border:0!important;
  border-left:1px solid #E3E8EF!important;
  border-radius:0!important;
  box-shadow:none!important;
}}
.stApp:has(.iars-login-marker) .stTextInput [data-baseweb="input"] button:hover {{
  background:#F8FAFC!important;
  transform:none!important;
}}

.stApp:has(.iars-login-marker) div[data-testid="stForm"] [data-testid="stHorizontalBlock"] {{
  min-height:34px!important;
  align-items:center!important;
  gap:10px!important;
}}
.stApp:has(.iars-login-marker) .stCheckbox,
.stApp:has(.iars-login-marker) .stCheckbox > label,
.stApp:has(.iars-login-marker) .stCheckbox label > div,
.stApp:has(.iars-login-marker) .stCheckbox label p {{
  white-space:nowrap!important;
  flex-wrap:nowrap!important;
}}
.stApp:has(.iars-login-marker) .stCheckbox label {{
  display:inline-flex!important;
  align-items:center!important;
  width:max-content!important;
  gap:.42rem!important;
}}
.stApp:has(.iars-login-marker) .stCheckbox label p {{
  margin:0!important;
  color:#344054!important;
  font-size:.91rem!important;
  line-height:1.2!important;
}}
.st-key-auth_forgot_submit {{display:flex!important;justify-content:flex-end!important;}}
.st-key-auth_forgot_submit .stFormSubmitButton {{width:100%!important;}}
.st-key-auth_forgot_submit button {{
  width:100%!important;
  min-height:32px!important;
  height:32px!important;
  justify-content:flex-end!important;
  padding:0!important;
  color:#175CD3!important;
  background:transparent!important;
  border:0!important;
  box-shadow:none!important;
  font-size:.91rem!important;
  font-weight:680!important;
}}
.st-key-auth_forgot_submit button:hover {{
  color:#0B4FB3!important;
  background:transparent!important;
  border:0!important;
  box-shadow:none!important;
  transform:none!important;
  text-decoration:underline!important;
}}
.stApp:has(.iars-login-marker) .stFormSubmitButton {{margin-top:2px!important;}}
.stApp:has(.iars-login-marker) button[kind="primary"],
.stApp:has(.iars-login-marker) button[kind="primaryFormSubmit"] {{
  box-sizing:border-box!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:100%!important;
  min-height:52px!important;
  height:52px!important;
  color:#FFF!important;
  background:#061A36!important;
  border:1px solid #061A36!important;
  border-radius:8px!important;
  box-shadow:none!important;
  font-size:1rem!important;
  font-weight:760!important;
}}
.stApp:has(.iars-login-marker) button[kind="primary"]:hover,
.stApp:has(.iars-login-marker) button[kind="primaryFormSubmit"]:hover {{
  color:#FFF!important;
  background:#0A2C59!important;
  border-color:#0A2C59!important;
  transform:none!important;
}}
.edl-auth-divider {{
  position:relative!important;
  z-index:auto!important;
  display:flex!important;
  align-items:center!important;
  min-height:24px!important;
  margin:10px 0 12px!important;
  gap:14px!important;
  color:#667085!important;
  background:transparent!important;
  font-size:.78rem!important;
  line-height:24px!important;
  text-align:center!important;
}}
.edl-auth-divider:before,.edl-auth-divider:after {{
  content:""!important;
  height:1px!important;
  flex:1!important;
  background:#DCE3EC!important;
}}
.iars-login-actions {{
  box-sizing:border-box!important;
  display:flex!important;
  flex-direction:column!important;
  align-items:stretch!important;
  width:100%!important;
  max-width:none!important;
  margin:2px 0 0!important;
  padding:0!important;
  gap:10px!important;
}}
a.iars-signup-action,
a.iars-signup-action:visited {{
  box-sizing:border-box!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  width:100%!important;
  max-width:none!important;
  min-height:52px!important;
  height:52px!important;
  margin:0!important;
  padding:0 18px!important;
  gap:10px!important;
  color:#061A36!important;
  background:#FFF!important;
  border:2px solid #174A86!important;
  border-radius:8px!important;
  outline:0!important;
  box-shadow:none!important;
  overflow:hidden!important;
  text-decoration:none!important;
  font-size:1rem!important;
  line-height:1!important;
  font-weight:760!important;
  cursor:pointer!important;
}}
a.iars-signup-action:hover,
a.iars-signup-action:focus-visible {{
  color:#061A36!important;
  background:#F8FAFC!important;
  border-color:#0A2C59!important;
  box-shadow:0 0 0 3px rgba(23,74,134,.10)!important;
  text-decoration:none!important;
  transform:none!important;
}}
.iars-signup-icon {{
  display:inline-block!important;
  flex:0 0 31px!important;
  width:31px!important;
  height:22px!important;
  background-repeat:no-repeat!important;
  background-position:center!important;
  background-size:31px 22px!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='31' height='22' viewBox='0 0 31 22' fill='none'%3E%3Cpath d='M4 5v6M1 8h6' stroke='%23061A36' stroke-width='1.8' stroke-linecap='round'/%3E%3Ccircle cx='19' cy='6' r='4' stroke='%23061A36' stroke-width='1.8'/%3E%3Cpath d='M11.5 20c.35-5.1 3-7.5 7.5-7.5s7.15 2.4 7.5 7.5' stroke='%23061A36' stroke-width='1.8' stroke-linecap='round'/%3E%3C/svg%3E")!important;
}}
.iars-signup-label {{
  display:inline-block!important;
  margin:0!important;
  white-space:nowrap!important;
  color:#061A36!important;
}}
a.iars-verify-action,
a.iars-verify-action:visited {{
  box-sizing:border-box!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  align-self:center!important;
  width:auto!important;
  min-width:0!important;
  min-height:44px!important;
  height:44px!important;
  margin:0 auto!important;
  padding:0 12px!important;
  gap:9px!important;
  color:#175CD3!important;
  background:transparent!important;
  border:0!important;
  border-radius:4px!important;
  box-shadow:none!important;
  text-decoration:none!important;
  font-size:17px!important;
  line-height:1!important;
  font-weight:700!important;
  cursor:pointer!important;
}}
a.iars-verify-action:hover,
a.iars-verify-action:focus-visible {{
  color:#0B4FB3!important;
  background:transparent!important;
  border:0!important;
  box-shadow:none!important;
  text-decoration:underline!important;
  transform:none!important;
}}
.iars-verify-icon {{
  display:inline-block!important;
  flex:0 0 22px!important;
  width:22px!important;
  height:22px!important;
  background-repeat:no-repeat!important;
  background-position:center!important;
  background-size:22px 22px!important;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none'%3E%3Cpath d='M12 3l7 3v5c0 4.8-2.8 8.2-7 10-4.2-1.8-7-5.2-7-10V6l7-3z' stroke='%23061A36' stroke-width='1.8' stroke-linejoin='round'/%3E%3Cpath d='M9 12l2 2 4-4' stroke='%23061A36' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")!important;
}}
.iars-verify-label {{
  display:inline-block!important;
  margin:0!important;
  white-space:nowrap!important;
  color:inherit!important;
}}
.edl-login-authorized {{
  margin-top:auto!important;
  padding:6px 0 0!important;
  color:#667085!important;
  font-size:.78rem!important;
  text-align:center!important;
}}

.iars-login-exit-mask {{
  position:fixed!important;
  inset:0!important;
  z-index:2147483000!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  opacity:1;
  visibility:visible;
  color:#061A36!important;
  background:#F4F6FA!important;
  pointer-events:auto!important;
}}
.iars-login-exit-card {{
  display:flex!important;
  flex-direction:column!important;
  align-items:center!important;
  gap:.5rem!important;
  font-family:Inter,"Segoe UI",sans-serif!important;
}}
.iars-login-exit-card strong {{font-size:1rem!important;}}
.iars-login-exit-card span {{color:#667085!important;font-size:.76rem!important;}}
.iars-login-exit-spinner {{
  width:30px!important;
  height:30px!important;
  border:3px solid #DCE3EC!important;
  border-top-color:#061A36!important;
  border-radius:50%!important;
  animation:iarsLoginSpinner .72s linear infinite;
}}
.stApp:has(.iars-app-ready-marker) .iars-login-exit-mask {{
  animation:iarsLoginMaskOut .38s .12s cubic-bezier(.22,.61,.36,1) forwards;
}}

@media(max-height:720px) and (min-width:901px) {{
  .st-key-iars_auth_card{{padding:12px 34px!important;}}
  .edl-auth-title{{margin:4px 0 7px!important;}}
  .st-key-iars_auth_card{{gap:5px!important;}}
  .stApp:has(.iars-login-marker) .stTextInput [data-baseweb="input"]{{min-height:46px!important;}}
  .stApp:has(.iars-login-marker) .stTextInput input{{min-height:43px!important;}}
  .stApp:has(.iars-login-marker) button[kind="primary"],
  .stApp:has(.iars-login-marker) .iars-signup-action{{min-height:47px!important;height:47px!important;}}
  .edl-auth-divider{{margin:6px 0 8px!important;}}
  .edl-login-authorized{{padding-top:2px!important;font-size:.74rem!important;}}
}}
@media(max-width:900px) {{
  html:has(.iars-login-marker),body:has(.iars-login-marker),.stApp:has(.iars-login-marker){{height:auto!important;min-height:100dvh!important;overflow:auto!important;}}
  .stApp:has(.iars-login-marker) [data-testid="stAppViewContainer"],
  .stApp:has(.iars-login-marker) [data-testid="stMain"],
  .stApp:has(.iars-login-marker) .main,
  .stApp:has(.iars-login-marker) .block-container{{height:auto!important;min-height:100dvh!important;overflow:auto!important;}}
  .st-key-iars_login_shell,
  .st-key-iars_login_shell > div[data-testid="stVerticalBlock"],
  .st-key-iars_login_shell [data-testid="stHorizontalBlock"]{{height:auto!important;max-height:none!important;}}
  .st-key-iars_login_shell [data-testid="stHorizontalBlock"]{{display:block!important;}}
  .st-key-edl_login_hero_panel{{height:44dvh!important;min-height:360px!important;}}
  .st-key-iars_auth_card{{height:auto!important;min-height:620px!important;margin-top:10px!important;padding:28px 20px!important;overflow:visible!important;}}
  .st-key-iars_auth_card:has(.iars-signin-view){{height:auto!important;overflow:visible!important;}}
}}
@media(prefers-reduced-motion:reduce) {{
  .st-key-iars_auth_card:has(.iars-auth-view-marker),
  .iars-login-exit-spinner{{animation:none!important;}}
  .stApp:has(.iars-app-ready-marker) .iars-login-exit-mask{{display:none!important;}}
}}

</style>
"""
    _render_html(css)


def render_brand_stripe() -> None:
    _render_html('<div class="edl-brand-stripe"></div>')


def render_sidebar_brand() -> None:
    """Render the exact EDL logo with native Streamlit image support."""
    logo_path = _asset_path("edl_logo.png")
    if logo_path.exists():
        st.image(str(logo_path), width=118)
    _render_html(
        '<div class="edl-sidebar-brand" style="padding-top:.02rem">'
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
        "Audit Workpapers": "Access reusable count sheets, working papers and audit workpapers",
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
    """Render the approved left-side login artwork at full panel height."""
    panel_path = _asset_path("login_left_panel.png")
    with st.container(key="edl_login_hero_panel"):
        if panel_path.exists():
            st.image(str(panel_path), use_container_width=True)
        else:
            logo_path = _asset_path("edl_logo.png")
            if logo_path.exists():
                st.image(str(logo_path), width=180)
            _render_html(
                '<div class="edl-native-login-copy">'
                '<h1>INTERNAL AUDIT<br>REPORT SYSTEM</h1>'
                '<p>A secure and centralized workspace for managing internal audit reports, archives, templates, and compliance documents.</p>'
                '</div>'
            )

def render_dashboard_hero() -> None:
    """Render the dashboard hero with a guaranteed visible audit image."""
    visual_path = _asset_path("internal_audit_visual.png")
    with st.container(key="edl_dashboard_hero_panel"):
        copy_col, image_col = st.columns([1.05, 1], gap="large", vertical_alignment="center")
        with copy_col:
            _render_html(
                '<div class="edl-native-dashboard-copy">'
                '<div class="edl-native-hero-tag">🛡️ Internal Audit Digital Workspace</div>'
                '<h1>Delivering Integrity.<br>Driving <em>Assurance.</em></h1>'
                '<p>Empowering the Internal Audit team with secure tools, accurate data, reusable resources and controlled records for confident decision-making.</p>'
                '</div>'
            )
        with image_col:
            if visual_path.exists():
                st.image(str(visual_path), use_container_width=True)


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
        value_class = "edl-metric-value long" if len(str(card.get("value", ""))) >= 12 else "edl-metric-value"
        chunks.append(
            f'<div class="edl-metric-card" style="--accent:{accent}">'
            f'<div class="edl-metric-icon">{icon}</div><div class="edl-metric-label">{label}</div>'
            f'<div class="{value_class}">{value}</div><div class="edl-metric-note">{note}</div></div>'
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
        tone = palette[index % len(palette)]
        chunks.append(
            f'<div class="edl-list-row" style="--rowtone:{tone}"><div class="edl-list-icon" style="--tone:{tone}">{icon}</div>'
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
        raw_value = str(row.get("value", ""))
        value = html.escape(raw_value)
        ok = bool(row.get("ok", False))
        lowered = raw_value.strip().lower()
        if ok:
            cls = "ok"
        elif any(token in lowered for token in ["not configured", "missing", "review", "setup", "offline"]):
            cls = "warn"
        else:
            cls = "neutral"
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
