import plotly.graph_objects as go
import streamlit as st

from utils.api_client import APIError, list_essays
from utils.session import log_out, require_login

st.set_page_config(page_title="Dashboard - IntelliScore AI", page_icon="📊", layout="wide")
require_login()  # halts execution here if not logged in

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    </style>
    """,
    unsafe_allow_html=True,
)

user = st.session_state.user

col1, col2 = st.columns([4, 1])
with col1:
    st.title(f"Welcome back, {user['full_name']} 👋")
    st.caption(f"{user['email']} · {user['role'].capitalize()}")
with col2:
    if st.button("Log Out", use_container_width=True):
        log_out()
        st.rerun()

st.divider()

try:
    essays = list_essays()
except APIError as e:
    st.error(f"Could not load your essays: {e}")
    essays = []

analyzed_essays = [e for e in essays if e.get("overall_score") is not None]

# ---------- Stats ----------
total_essays = len(essays)
total_words = sum(e["word_count"] for e in essays)
avg_words = round(total_words / total_essays, 0) if total_essays else 0
avg_score = round(sum(e["overall_score"] for e in analyzed_essays) / len(analyzed_essays), 1) if analyzed_essays else None
highest_score = round(max((e["overall_score"] for e in analyzed_essays), default=0), 1) if analyzed_essays else None

stat_cols = st.columns(4)
stat_cols[0].metric("Total Essays", total_essays)
stat_cols[1].metric("Average Score", f"{avg_score}/100" if avg_score is not None else "—")
stat_cols[2].metric("Highest Score", f"{highest_score}/100" if highest_score is not None else "—")
stat_cols[3].metric("Total Words Analyzed", f"{total_words:,}")

st.divider()

# ---------- Score trend chart ----------
if len(analyzed_essays) >= 1:
    st.subheader("Score Trend")
    sorted_essays = sorted(analyzed_essays, key=lambda e: e["created_at"])
    fig = go.Figure(
        go.Scatter(
            x=[e["created_at"][:10] for e in sorted_essays],
            y=[e["overall_score"] for e in sorted_essays],
            mode="lines+markers",
            line=dict(color="#a78bfa", width=3),
            marker=dict(color="#60a5fa", size=8),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#c4c4d4"},
        yaxis=dict(range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

# ---------- Quick actions ----------
st.subheader("Quick Actions")
action_cols = st.columns(3)
with action_cols[0]:
    st.page_link("pages/4_Upload_Essay.py", label="Upload New Essay", icon="⬆️")
with action_cols[1]:
    st.page_link("pages/5_Essay_Analysis.py", label="Analyze an Essay", icon="📊")

st.divider()

# ---------- Recent essays ----------
st.subheader("Your Essays")
if not essays:
    st.info("You haven't uploaded any essays yet.")
    st.page_link("pages/4_Upload_Essay.py", label="Upload your first essay", icon="⬆️")
else:
    for essay in essays:
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{essay['title']}**")
            cols[1].caption(f"{essay['file_type'].upper()}")
            cols[2].caption(f"{essay['word_count']} words")
            score_display = f"{essay['overall_score']}/100" if essay.get("overall_score") is not None else "Not analyzed"
            cols[3].caption(score_display)
