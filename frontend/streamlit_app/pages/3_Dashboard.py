"""
Dashboard Home – IntelliScore AI  (Page 6 in reference image)
"""
import random
from datetime import datetime, timedelta

import plotly.graph_objects as go
import streamlit as st

from utils.api_client import APIError, list_essays
from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Dashboard – IntelliScore AI", page_icon="📊", layout="wide")
require_login()
render_sidebar()

# ── Mock data helpers ────────────────────────────────────────────────────────
def _mock_essays():
    titles = [
        "The Impact of AI on Society", "Climate Change and Policy",
        "Education System Reform", "Digital Privacy Rights",
        "Future of Renewable Energy",
    ]
    essays = []
    base_date = datetime(2025, 5, 1)
    for i, title in enumerate(titles):
        score = random.randint(70, 98)
        essays.append({
            "id": i + 1, "title": title,
            "file_type": ["pdf", "docx", "txt"][i % 3],
            "word_count": random.randint(500, 1500),
            "overall_score": score,
            "created_at": (base_date + timedelta(days=i * 7)).strftime("%Y-%m-%dT10:00:00"),
        })
    return essays

def _load_essays():
    try:
        data = list_essays()
        return data if data else _mock_essays()
    except Exception:
        return _mock_essays()

# ── Load data ────────────────────────────────────────────────────────────────
essays = _load_essays()
analyzed = [e for e in essays if e.get("overall_score") is not None]

user = st.session_state.user
name = user.get("full_name", "User") if user else "User"

# ── Page header ──────────────────────────────────────────────────────────────
st.markdown(f'<div class="page-header">Welcome back, {name} 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Here\'s what\'s happening with your essays</div>',
            unsafe_allow_html=True)

# ── Quick stats ──────────────────────────────────────────────────────────────
total     = len(essays)
avg_score = round(sum(e["overall_score"] for e in analyzed) / len(analyzed), 1) if analyzed else 0
highest   = max((e["overall_score"] for e in analyzed), default=0)
recent_n  = 18   # mock recent activity count

sc1, sc2, sc3, sc4 = st.columns(4, gap="small")
for col, num, label, delta in [
    (sc1, total,     "Total Essays",     "+2 this week"),
    (sc2, avg_score, "Average Score",    "+1.2 pts"),
    (sc3, highest,   "Highest Score",    "Personal best"),
    (sc4, recent_n,  "Recent Activity",  "Last 7 days"),
]:
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{num}</div>
            <div class="stat-label">{label}</div>
            <div style="font-size:0.72rem;color:#34d399;margin-top:0.4rem;">↑ {delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Score Trend chart ────────────────────────────────────────────────────────
trend_col, activity_col = st.columns([3, 2], gap="medium")

with trend_col:
    st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.6rem;">📈 Score Trend</div>',
                unsafe_allow_html=True)
    sorted_essays = sorted(analyzed, key=lambda e: e["created_at"])
    dates  = [e["created_at"][:10] for e in sorted_essays]
    scores = [e["overall_score"]   for e in sorted_essays]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores, mode="lines+markers",
        line=dict(color="#a78bfa", width=3, shape="spline"),
        marker=dict(color="#60a5fa", size=9, line=dict(color="#ffffff", width=2)),
        fill="tozeroy",
        fillcolor="rgba(167,139,250,0.08)",
        name="Score",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af", family="Inter"),
        yaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=11)),
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=11)),
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with activity_col:
    st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.6rem;">⚡ Recent Activity '
                '<a href="#" style="font-size:0.78rem;color:#a78bfa;float:right;font-weight:500;">View All</a></div>',
                unsafe_allow_html=True)
    activities = [
        ("📝", "AI Writing Mentor", "ClimateChange.pdf analyzed", "May 18, 2025", "#60a5fa"),
        ("📊", "Essay Analysis",    "Climate Change Ideas", "May 15, 2025", "#34d399"),
        ("⚖️", "Compare Essays",    "Education System Essay", "Mar 16, 2025", "#a78bfa"),
    ]
    for icon, tag, title, date, clr in activities:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                    border-radius:10px;padding:0.75rem 1rem;margin-bottom:0.5rem;
                    border-left:3px solid {clr};">
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <span style="font-size:1.1rem;">{icon}</span>
                <div>
                    <div style="font-size:0.78rem;font-weight:600;color:{clr};">{tag}</div>
                    <div style="font-size:0.88rem;font-weight:600;color:#e5e7eb;">{title}</div>
                    <div style="font-size:0.72rem;color:#6b7280;">{date}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Recent essays table ───────────────────────────────────────────────────────
st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">📚 Your Essays</div>',
            unsafe_allow_html=True)

header_cols = st.columns([3, 1, 1, 1, 1])
for col, h in zip(header_cols, ["Title", "Type", "Words", "Score", "Action"]):
    col.markdown(f'<span style="color:#a78bfa;font-size:0.8rem;font-weight:700;">{h}</span>',
                 unsafe_allow_html=True)

for essay in essays[:6]:
    score = essay.get("overall_score")
    pill_class = "pill-green" if (score or 0) >= 80 else "pill-yellow" if (score or 0) >= 60 else "pill-blue"
    r1, r2, r3, r4, r5 = st.columns([3, 1, 1, 1, 1])
    r1.markdown(f'<span style="color:#e5e7eb;font-weight:600;">{essay["title"]}</span>', unsafe_allow_html=True)
    r2.markdown(f'<span class="pill-blue">{essay["file_type"].upper()}</span>', unsafe_allow_html=True)
    r3.markdown(f'<span style="color:#9ca3af;">{essay["word_count"]}</span>', unsafe_allow_html=True)
    r4.markdown(f'<span class="{pill_class}">{score}/100</span>' if score else '<span class="pill-yellow">Pending</span>',
                unsafe_allow_html=True)
    r5.page_link("pages/5_Essay_Analysis.py", label="Analyze →")

st.divider()
qa1, qa2, qa3 = st.columns(3)
with qa1:
    st.page_link("pages/4_Upload_Essay.py", label="⬆️ Upload New Essay")
with qa2:
    st.page_link("pages/7_Compare_Essays.py", label="⚖️ Compare Essays")
with qa3:
    st.page_link("pages/9_Analytics.py", label="📈 View Analytics")
