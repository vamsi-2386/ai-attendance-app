import streamlit as st


# ── Shared CSS injected once ────────────────────────────────────────────────

_FONTS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
"""

_GLOBAL_STYLE = """
/* ── Reset & Fonts ── */
* { box-sizing: border-box; }

body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px !important; }

/* ── Headings ── */
h1 {
    font-family: 'Climate Crisis', sans-serif !important;
    font-size: 3rem !important;
    line-height: 1.05 !important;
    margin-bottom: 0.25rem !important;
    letter-spacing: 1px;
}
h2 {
    font-family: 'Climate Crisis', sans-serif !important;
    font-size: 1.8rem !important;
    line-height: 1 !important;
    margin-bottom: 0.1rem !important;
}
h3, h4, p, label { font-family: 'Inter', sans-serif !important; }

/* ── Primary Button ── */
button[kind="primary"] {
    background: linear-gradient(135deg, #5865F2, #8A2BE2) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(88, 101, 242, 0.35) !important;
}
button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 24px rgba(88, 101, 242, 0.55) !important;
}

/* ── Secondary Button ── */
button[kind="secondary"] {
    background: transparent !important;
    color: #5865F2 !important;
    border: 2px solid #5865F2 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
}
button[kind="secondary"]:hover {
    background: rgba(88, 101, 242, 0.08) !important;
    transform: translateY(-1px) !important;
}

/* ── Tertiary Button ── */
button[kind="tertiary"] {
    background: rgba(30, 30, 40, 0.85) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
button[kind="tertiary"]:hover {
    background: rgba(88, 101, 242, 0.15) !important;
    border-color: rgba(88, 101, 242, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div {
    border-radius: 12px !important;
    border: 1.5px solid rgba(88, 101, 242, 0.25) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #5865F2 !important;
    box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.15) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(88, 101, 242, 0.06) !important;
    border-radius: 16px !important;
    padding: 6px !important;
    border-bottom: none !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 16px !important;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, #5865F2, #8A2BE2) !important;
    color: #fff !important;
    box-shadow: 0 4px 12px rgba(88, 101, 242, 0.3) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Metric Cards ── */
[data-testid="stMetric"] {
    background: rgba(88, 101, 242, 0.06) !important;
    border-radius: 16px !important;
    padding: 1rem 1.25rem !important;
    border: 1px solid rgba(88, 101, 242, 0.15) !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(88,101,242,0.12) !important;
}

/* ── Divider ── */
hr { border-color: rgba(88, 101, 242, 0.12) !important; }

/* ── Alert / Info boxes ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 4px !important;
}
"""


def style_background_home():
    st.markdown(f"""
        <style>
        {_FONTS}
        {_GLOBAL_STYLE}

        /* Home-specific background */
        .stApp {{
            background: linear-gradient(145deg, #0f0c29, #302b63, #24243e) !important;
        }}
        .stApp [data-testid="stColumn"] {{
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            padding: 2.5rem !important;
            border-radius: 2rem !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3) !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }}
        .stApp [data-testid="stColumn"]:hover {{
            transform: translateY(-4px) !important;
            box-shadow: 0 16px 48px rgba(88,101,242,0.25) !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown(f"""
        <style>
        {_FONTS}
        {_GLOBAL_STYLE}

        /* Dashboard background */
        .stApp {{
            background: linear-gradient(160deg, #f0f2ff 0%, #e8eafe 50%, #f5f0ff 100%) !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    # No-op: styles are now injected by the background functions above
    pass