"""
IntelliScore AI – Landing / Splash Page (Home.py)
"""
import streamlit as st
from utils.layout import render_sidebar
from utils.session import init_session_state, is_authenticated

st.set_page_config(
    page_title="IntelliScore AI – AI-Powered Essay Evaluation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_session_state()
render_sidebar()

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg,rgba(124,58,237,0.2),rgba(79,70,229,0.2));
    border: 1px solid rgba(167,139,250,0.4);
    color: #a78bfa; font-size:0.8rem; font-weight:600;
    padding:4px 14px; border-radius:20px; letter-spacing:0.08em;
    margin-bottom:1rem;
}
.hero-title {
    font-size:3.4rem; font-weight:900; line-height:1.15;
    background: linear-gradient(135deg,#a78bfa 0%,#60a5fa 50%,#34d399 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:0.6rem;
}
.hero-desc {
    font-size:1.15rem; color:#9ca3af; line-height:1.7;
    max-width:600px; margin-bottom:2rem;
}
.hero-btn-primary {
    display:inline-block;
    background:linear-gradient(135deg,#7c3aed,#4f46e5);
    color:white; padding:0.75rem 2rem; border-radius:12px;
    font-weight:700; font-size:1rem; text-decoration:none;
    box-shadow:0 4px 20px rgba(124,58,237,0.4);
    transition:transform 0.2s;
}
.hero-btn-secondary {
    display:inline-block;
    background:rgba(167,139,250,0.1);
    border:1px solid rgba(167,139,250,0.3);
    color:#a78bfa; padding:0.75rem 2rem; border-radius:12px;
    font-weight:700; font-size:1rem; text-decoration:none;
    margin-left:1rem;
}
.feature-icon {
    width:48px; height:48px;
    background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(79,70,229,0.2));
    border:1px solid rgba(167,139,250,0.3);
    border-radius:12px;
    display:flex; align-items:center; justify-content:center;
    font-size:1.5rem; margin-bottom:0.75rem;
}
.feat-title { font-size:1rem; font-weight:700; color:#e5e7eb; margin-bottom:0.3rem; }
.feat-desc  { font-size:0.85rem; color:#9ca3af; line-height:1.6; }
.step-num {
    width:36px; height:36px;
    background:linear-gradient(135deg,#7c3aed,#4f46e5);
    border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-weight:800; color:white; font-size:0.9rem;
    margin-bottom:0.6rem;
}
.step-title { font-weight:700; color:#e5e7eb; margin-bottom:0.25rem; }
.step-desc  { font-size:0.83rem; color:#9ca3af; }
.stat-hero { text-align:center; }
.stat-hero-num {
    font-size:2.8rem; font-weight:900;
    background:linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.stat-hero-label { color:#9ca3af; font-size:0.88rem; margin-top:0.2rem; }
</style>
""", unsafe_allow_html=True)

col_hero, col_img = st.columns([3, 2], gap="large")
with col_hero:
    st.markdown('<div class="hero-badge">✨ AI-POWERED ESSAY PLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">AI-Powered Essay<br/>Evaluation &amp;<br/>Learning Platform</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-desc">Get accurate scores, detailed feedback, AI suggestions '
        'and improve your writing with our intelligent platform.</div>',
        unsafe_allow_html=True
    )
    b1, b2, _ = st.columns([1.4, 1.4, 2])
    with b1:
        if is_authenticated():
            st.page_link("pages/3_Dashboard.py", label="📊 Go to Dashboard")
        else:
            st.page_link("pages/2_Register.py", label="🚀 Get Started")
    with b2:
        if not is_authenticated():
            st.page_link("pages/1_Login.py", label="▶️ Watch Demo")

with col_img:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(79,70,229,0.1));
                border:1px solid rgba(167,139,250,0.25); border-radius:20px;
                padding:2rem; text-align:center; margin-top:1rem;">
        <div style="font-size:5rem;">🤖</div>
        <div style="font-size:1.1rem; font-weight:700; color:#a78bfa; margin-top:0.5rem;">IntelliScore AI</div>
        <div style="font-size:0.82rem; color:#9ca3af; margin-top:0.3rem;">Evaluate · Improve · Excel</div>
        <div style="margin-top:1.5rem; display:flex; flex-direction:column; gap:0.5rem;">
            <div style="background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.3);
                        border-radius:8px; padding:0.5rem 1rem; color:#34d399; font-size:0.82rem; font-weight:600;">
                ✅ Accurate Scoring — Advanced AI models
            </div>
            <div style="background:rgba(96,165,250,0.1);border:1px solid rgba(96,165,250,0.3);
                        border-radius:8px; padding:0.5rem 1rem; color:#60a5fa; font-size:0.82rem; font-weight:600;">
                📋 Detailed Feedback — Improve your writing
            </div>
            <div style="background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.3);
                        border-radius:8px; padding:0.5rem 1rem; color:#a78bfa; font-size:0.82rem; font-weight:600;">
                🤖 AI Writing Mentor — 24/7 Assistant
            </div>
            <div style="background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);
                        border-radius:8px; padding:0.5rem 1rem; color:#fbbf24; font-size:0.82rem; font-weight:600;">
                📈 Analytics &amp; Reports — Track your progress
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Stats row ─────────────────────────────────────────────────────────────────
sc1, sc2, sc3, sc4 = st.columns(4)
stats = [("50K+", "Essays Analyzed"), ("98%", "Accuracy Rate"), ("4.9★", "User Rating"), ("24/7", "AI Assistance")]
for col, (num, label) in zip([sc1, sc2, sc3, sc4], stats):
    with col:
        st.markdown(f'<div class="stat-hero"><div class="stat-hero-num">{num}</div>'
                    f'<div class="stat-hero-label">{label}</div></div>', unsafe_allow_html=True)

st.divider()

# ── Features ──────────────────────────────────────────────────────────────────
st.markdown('<div class="page-header" style="font-size:1.6rem">What IntelliScore AI Does</div>',
            unsafe_allow_html=True)

feats = [
    ("📊", "Accurate Scoring",    "XGBoost-powered scoring across grammar, vocabulary, coherence, and argument strength."),
    ("🔍", "Detailed Feedback",   "Identify exactly which features drove your score with explainable AI results."),
    ("🤖", "AI Writing Mentor",   "Chat with an intelligent mentor to improve grammar, vocabulary, and essay structure."),
    ("📈", "Analytics & Reports", "Track progress over time with visual dashboards, trend analysis, and downloadable reports."),
]
fc1, fc2, fc3, fc4 = st.columns(4, gap="small")
for col, (icon, title, desc) in zip([fc1, fc2, fc3, fc4], feats):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="min-height:160px;">
            <div class="feature-icon">{icon}</div>
            <div class="feat-title">{title}</div>
            <div class="feat-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-header" style="font-size:1.6rem">How It Works</div>', unsafe_allow_html=True)
steps = [
    ("1", "Upload",  "Upload your essay as PDF, DOCX, TXT, or a scanned image.",        "⬆️"),
    ("2", "Analyze", "NLP and ML models extract features and generate a detailed score.", "🔍"),
    ("3", "Review",  "See detailed feedback: grammar, vocabulary, coherence, and more.",  "📋"),
    ("4", "Improve", "Chat with the AI mentor to revise and strengthen your writing.",    "🚀"),
]
s1, s2, s3, s4 = st.columns(4, gap="small")
for col, (num, title, desc, icon) in zip([s1, s2, s3, s4], steps):
    with col:
        st.markdown(f"""
        <div class="glass-card" style="min-height:140px;">
            <div class="step-num">{num}</div>
            <div class="step-title">{icon} {title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
if not is_authenticated():
    cta1, cta2, _ = st.columns([1, 1, 3])
    with cta1:
        st.page_link("pages/2_Register.py", label="🚀 Get Started — It's Free")
    with cta2:
        st.page_link("pages/1_Login.py", label="🔐 Log In")
