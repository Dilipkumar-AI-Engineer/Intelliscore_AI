"""
Landing page (Streamlit's convention: the file run with `streamlit run`
is the app's home/entrypoint). Sidebar pages come from pages/*.py.
"""

import streamlit as st

from utils.session import init_session_state, is_authenticated

st.set_page_config(
    page_title="IntelliScore AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

# Custom CSS: dark theme with purple/blue gradients, per the project's
# design spec. Streamlit's default theme is light -- this overrides it
# via injected CSS, which is the standard way to customize Streamlit's
# appearance without ejecting to a full custom frontend.
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #c4c4d4;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
    }
    .feature-card h4 {
        color: #a78bfa;
        margin-top: 0;
    }
    .feature-card p {
        color: #c4c4d4;
        font-size: 0.95rem;
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        color: #60a5fa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Hero section ----------
st.markdown('<p class="hero-title">IntelliScore AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">An Explainable AI Platform for Automated Essay Evaluation, '
    "Writing Improvement, Academic Integrity, and Learning Analytics.</p>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    if is_authenticated():
        st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="📊")
    else:
        st.page_link("pages/2_Register.py", label="Get Started", icon="🚀")
with col2:
    if not is_authenticated():
        st.page_link("pages/1_Login.py", label="Log In", icon="🔐")

st.divider()

# ---------- Feature cards ----------
st.subheader("What IntelliScore AI Does")
feature_cols = st.columns(4)
features = [
    ("📊", "Automated Scoring", "XGBoost-powered scoring across grammar, vocabulary, coherence, and argument strength."),
    ("🔍", "Explainable Results", "See exactly which features drove your score -- not just a number."),
    ("🤖", "AI Writing Mentor", "Chat with an AI mentor to improve grammar, vocabulary, and structure."),
    ("📈", "Learning Analytics", "Track progress over time with visual dashboards and trend analysis."),
]
for col, (icon, title, desc) in zip(feature_cols, features):
    with col:
        st.markdown(
            f'<div class="feature-card"><h4>{icon} {title}</h4><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

st.divider()

# ---------- How it works ----------
st.subheader("How It Works")
step_cols = st.columns(4)
steps = [
    ("1", "Upload", "Upload your essay as PDF, DOCX, TXT, or a scanned image."),
    ("2", "Analyze", "NLP and ML models extract features and generate a score."),
    ("3", "Review", "See detailed feedback: grammar, vocabulary, coherence, and more."),
    ("4", "Improve", "Chat with the AI mentor to revise and strengthen your writing."),
]
for col, (num, title, desc) in zip(step_cols, steps):
    with col:
        st.markdown(f"**{num}. {title}**")
        st.caption(desc)

