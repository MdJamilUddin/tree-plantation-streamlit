# ui_utils.py
import streamlit as st

BANGLA_FONT = "Noto Sans Bengali"

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700&display=swap');

/* ---------- Global font ---------- */
html, body, [class*="css"], [class*="st-"], button, input, textarea, select {{
    font-family: '{BANGLA_FONT}', sans-serif !important;
}}

/* ---------- Hide Streamlit menu/footer for cleaner look ---------- */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{background: transparent !important;}}

/* ---------- Main container padding ---------- */
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 1200px;
}}

/* ---------- Hero header ---------- */
.hero {{
    background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
    color: #fff;
    padding: 24px 20px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 6px 24px rgba(46,125,50,0.25);
}}
.hero h1 {{ margin: 0; font-size: 1.6rem; font-weight: 700; }}
.hero p {{ margin: 8px 0 0; opacity: 0.92; font-size: 0.95rem; }}

/* ---------- Metric cards ---------- */
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
}}
.metric-card {{
    background: #fff;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    border-left: 5px solid #2e7d32;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}}
.metric-card .label {{ font-size: 0.82rem; color: #557; margin-bottom: 6px; }}
.metric-card .value {{ font-size: 1.6rem; font-weight: 700; color: #1b5e20; }}

/* ---------- Section card ---------- */
.section-card {{
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e0efe0;
}}
.section-title {{
    font-size: 1.05rem; font-weight: 700; color: #2e7d32;
    margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.2rem !important;
    min-height: 44px;  /* mobile tap target */
}}
.stButton > button[kind="primary"],
.stFormSubmitButton > button {{
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(46,125,50,0.3) !important;
}}

/* ---------- Form inputs ---------- */
.stTextInput input, .stNumberInput input, .stDateInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea {{
    border-radius: 10px !important;
    border: 1px solid #c8e6c9 !important;
    min-height: 42px;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: #2e7d32 !important;
    box-shadow: 0 0 0 2px rgba(46,125,50,0.2) !important;
}}

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"] {{
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background: #e8f5e9;
}}
[data-testid="stSidebar"] .block-container {{
    padding-top: 1rem;
}}

/* ---------- Progress bar ---------- */
.stProgress > div > div > div {{
    background: linear-gradient(90deg, #66bb6a, #2e7d32) !important;
    border-radius: 10px !important;
}}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 10px 10px 0 0;
    padding: 10px 16px;
    font-weight: 600;
}}

/* ---------- Success / error / info boxes ---------- */
.stAlert {{
    border-radius: 12px;
}}

/* ================= MOBILE ================= */
@media (max-width: 640px) {{
    .hero {{ padding: 18px 14px; border-radius: 12px; }}
    .hero h1 {{ font-size: 1.25rem; }}
    .hero p {{ font-size: 0.85rem; }}
    .metric-grid {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    .metric-card {{ padding: 12px; }}
    .metric-card .value {{ font-size: 1.3rem; }}
    .block-container {{
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }}
    .section-card {{ padding: 14px; border-radius: 12px; }}
    /* Stack columns */
    [data-testid="column"] {{ min-width: 100% !important; flex: 1 1 100% !important; }}
    /* Larger tap targets */
    .stButton > button {{ width: 100%; min-height: 48px; }}
    /* Compact dataframe */
    [data-testid="stDataFrame"] {{ font-size: 0.85rem; }}
}}
</style>
"""


def inject_css():
    """প্রতিটি পেজে একবার কল করুন"""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1>'
        + (f"<p>{subtitle}</p>" if subtitle else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def metric_cards(items: list[tuple[str, str]]):
    """
    items: [("মোট বিদ্যালয়", "25 / 100"), ("ফলদ চারা", "120"), ...]
    """
    html = '<div class="metric-grid">'
    for label, value in items:
        html += (
            f'<div class="metric-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value">{value}</div>'
            f"</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section(title: str):
    """সেকশন কার্ডের শুরু — context manager এর বদলে সহজ wrapper"""
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def section_start():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)


def section_end():
    st.markdown("</div>", unsafe_allow_html=True)