"""
Shared sidebar navigation + global CSS injection.

Call render_sidebar() near the top of every page after st.set_page_config().
Call inject_global_css() for consistent theming across pages.
"""

import streamlit as st
from utils.session import is_authenticated, log_out

# ───────────────────────────── GLOBAL CSS ──────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a0818 0%, #0f0c29 40%, #1a0e3a 70%, #0d1b3e 100%);
    min-height: 100vh;
}

/* ── Hide default Streamlit nav ── */
[data-testid="stSidebarNav"] { display: none !important; }
header[data-testid="stHeader"] { background: rgba(10,8,24,0.8) !important; backdrop-filter: blur(10px); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0b24 0%, #120f33 60%, #0a1628 100%) !important;
    border-right: 1px solid rgba(167,139,250,0.15);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* ── Cards ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
    transition: border-color 0.3s ease, transform 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(167,139,250,0.5);
    transform: translateY(-2px);
}

/* ── Stat / metric cards ── */
.stat-card {
    background: linear-gradient(135deg, rgba(167,139,250,0.08), rgba(96,165,250,0.05));
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.stat-number {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.stat-label {
    color: #9ca3af;
    font-size: 0.82rem;
    font-weight: 500;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Score badges ── */
.score-circle {
    width: 90px; height: 90px;
    border-radius: 50%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: conic-gradient(#a78bfa var(--pct), rgba(255,255,255,0.08) 0);
    font-size: 1.4rem; font-weight: 800; color: #fff;
    margin: 0 auto;
}

/* ── Sub-score pill ── */
.sub-score-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.sub-score-value { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.sub-score-label { color: #9ca3af; font-size: 0.8rem; margin-top: 0.2rem; }

/* ── Page headings ── */
.page-header {
    background: linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2rem; font-weight: 800;
    margin-bottom: 0.2rem;
}
.page-subheader { color: #9ca3af; font-size: 0.95rem; margin-bottom: 1.5rem; }

/* ── Table ── */
.custom-table {
    width: 100%; border-collapse: collapse; font-size: 0.9rem;
}
.custom-table th {
    background: rgba(167,139,250,0.12);
    color: #a78bfa;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid rgba(167,139,250,0.2);
}
.custom-table td {
    padding: 0.75rem 1rem;
    color: #d1d5db;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.custom-table tr:hover td { background: rgba(167,139,250,0.05); }

/* ── Status pills ── */
.pill-green {
    background: rgba(52,211,153,0.15); color: #34d399;
    border: 1px solid rgba(52,211,153,0.3);
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem; font-weight: 600;
}
.pill-blue {
    background: rgba(96,165,250,0.15); color: #60a5fa;
    border: 1px solid rgba(96,165,250,0.3);
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem; font-weight: 600;
}
.pill-yellow {
    background: rgba(251,191,36,0.15); color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.3);
    border-radius: 20px; padding: 2px 10px; font-size: 0.78rem; font-weight: 600;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    border-radius: 10px !important;
    color: #e5e7eb !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important;
}

/* ── Primary Button ── */
.stButton > button {
    background: linear-gradient(135deg,#7c3aed,#4f46e5) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#8b5cf6,#6366f1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}

/* ── Sidebar page links ── */
[data-testid="stSidebar"] [data-testid="stPageLink"] {
    border-radius: 10px;
    margin-bottom: 2px;
    color: #c4c4d4 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
    background: rgba(167,139,250,0.15) !important;
    color: #a78bfa !important;
}

/* ── Dividers ── */
hr { border-color: rgba(167,139,250,0.15) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #9ca3af;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(167,139,250,0.2) !important;
    color: #a78bfa !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(167,139,250,0.15);
    border-radius: 14px;
    margin-bottom: 0.5rem;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── Metric ── */
[data-testid="stMetricValue"] { color: #a78bfa !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #9ca3af !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(167,139,250,0.05) !important;
    border: 2px dashed rgba(167,139,250,0.4) !important;
    border-radius: 14px !important;
}
</style>
"""

# ───────────────────────────── SIDEBAR ─────────────────────────────────────

SIDEBAR_BRAND_CSS = """
<style>
.sidebar-logo-wrap {
    padding: 1.2rem 1rem 0.5rem;
    display: flex; align-items: center; gap: 0.6rem;
    border-bottom: 1px solid rgba(167,139,250,0.2);
    margin-bottom: 0.5rem;
}
.sidebar-logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg,#7c3aed,#4f46e5);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; font-weight: 900; color: white;
}
.sidebar-brand-name {
    font-size: 1.1rem; font-weight: 800;
    background: linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sidebar-brand-tag {
    font-size: 0.65rem; color: #6b7280;
    margin-top: -3px; letter-spacing: 0.04em;
}
.sidebar-user-box {
    margin: 0.4rem 0.5rem 0.2rem;
    padding: 0.7rem 0.8rem;
    background: rgba(167,139,250,0.08);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 10px;
}
.sidebar-user-name { font-weight: 700; color: #e5e7eb; font-size: 0.9rem; }
.sidebar-user-role {
    font-size: 0.72rem; color: #a78bfa; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.sidebar-section-label {
    color: #6b7280; font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 0.6rem 0.8rem 0.2rem;
}
</style>
"""

AUTHENTICATED_NAV = [
    ("pages/3_Dashboard.py",        "📊", "Dashboard"),
    ("pages/4_Upload_Essay.py",     "⬆️", "Upload Essays"),
    ("pages/5_Essay_Analysis.py",   "🔍", "Essay Analysis"),
    ("pages/6_Detailed_Analysis.py","🗂️", "Detailed Analysis"),
    ("pages/7_Compare_Essays.py",   "⚖️", "Compare Essays"),
    ("pages/8_AI_Writing_Mentor.py","🤖", "AI Writing Mentor"),
    ("pages/9_Analytics.py",        "📈", "Analytics"),
    ("pages/10_Reports.py",         "📄", "Reports"),
    ("pages/11_My_Essays.py",       "📚", "My Essays"),
    ("pages/13_Essay_Preview.py",   "👁️", "Essay Preview"),
    ("pages/12_Settings.py",        "⚙️", "Settings"),
]


def inject_global_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_sidebar():
    inject_global_css()
    st.markdown(SIDEBAR_BRAND_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # Logo / brand
        st.markdown("""
        <div class="sidebar-logo-wrap">
            <div class="sidebar-logo-icon">AI</div>
            <div>
                <div class="sidebar-brand-name">IntelliScore AI</div>
                <div class="sidebar-brand-tag">Evaluate · Improve · Excel</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if is_authenticated():
            user = st.session_state.user
            st.markdown(f"""
            <div class="sidebar-user-box">
                <div class="sidebar-user-name">👤 {user['full_name']}</div>
                <div class="sidebar-user-role">{user['role'].capitalize()}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
            for path, icon, label in AUTHENTICATED_NAV:
                st.page_link(path, label=label, icon=icon)

            st.divider()
            if st.button("🚪 Log Out", use_container_width=True):
                log_out()
                st.switch_page("Home.py")
        else:
            st.markdown('<div class="sidebar-section-label">Menu</div>', unsafe_allow_html=True)
            st.page_link("Home.py",            label="Home",          icon="🏠")
            st.page_link("pages/1_Login.py",   label="Log In",        icon="🔐")
            st.page_link("pages/2_Register.py",label="Register",      icon="📝")
            st.page_link("pages/0_Forgot_Password.py", label="Forgot Password", icon="🔑")
