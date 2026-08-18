"""
Compare Essays page – IntelliScore AI  (Page 10 in reference image)
"""
import plotly.graph_objects as go
import streamlit as st

from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Compare Essays – IntelliScore AI", page_icon="⚖️", layout="wide")
require_login()
render_sidebar()

st.markdown('<div class="page-header">⚖️ Compare Essays</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Compare performance across multiple essays side-by-side</div>',
            unsafe_allow_html=True)

# ── Mock comparison data ──────────────────────────────────────────────────────
ESSAYS = [
    {"name": "Essay_1.pdf",  "overall": 86, "grammar": 90, "vocabulary": 85, "coherence": 82, "readability": 80},
    {"name": "Essay_2.docx", "overall": 74, "grammar": 68, "vocabulary": 74, "coherence": 80, "readability": 75},
    {"name": "Essay_3.pdf",  "overall": 65, "grammar": 63, "vocabulary": 60, "coherence": 67, "readability": 62},
    {"name": "Essay_4.txt",  "overall": 91, "grammar": 95, "vocabulary": 88, "coherence": 90, "readability": 89},
    {"name": "Essay_5.pdf",  "overall": 45, "grammar": 42, "vocabulary": 48, "coherence": 44, "readability": 50},
]

top_r, top_btn = st.columns([5, 1])
with top_btn:
    st.button("➕ Add More Essays", use_container_width=True)

# ── Comparison Table ──────────────────────────────────────────────────────────
st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.6rem;">Essay Comparison Table</div>',
            unsafe_allow_html=True)

cols = st.columns([3, 1.2, 1.2, 1.2, 1.2, 1.2])
headers = ["Essay Name", "Overall", "Grammar", "Vocabulary", "Coherence", "Readability"]
for col, h in zip(cols, headers):
    col.markdown(f'<span style="color:#a78bfa;font-size:0.8rem;font-weight:700;">{h}</span>',
                 unsafe_allow_html=True)

def score_pill(sc):
    clr = "#34d399" if sc >= 80 else "#fbbf24" if sc >= 60 else "#ef4444"
    return (f'<span style="background:rgba(255,255,255,0.06);border-radius:6px;'
            f'padding:3px 10px;font-weight:700;font-size:0.88rem;color:{clr};">{sc}</span>')

for e in ESSAYS:
    c1, c2, c3, c4, c5, c6 = st.columns([3, 1.2, 1.2, 1.2, 1.2, 1.2])
    c1.markdown(f'<span style="color:#e5e7eb;font-size:0.88rem;">📄 {e["name"]}</span>', unsafe_allow_html=True)
    c2.markdown(score_pill(e["overall"]),    unsafe_allow_html=True)
    c3.markdown(score_pill(e["grammar"]),    unsafe_allow_html=True)
    c4.markdown(score_pill(e["vocabulary"]), unsafe_allow_html=True)
    c5.markdown(score_pill(e["coherence"]),  unsafe_allow_html=True)
    c6.markdown(score_pill(e["readability"]),unsafe_allow_html=True)

st.divider()

# ── Grouped Bar Chart ─────────────────────────────────────────────────────────
st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Overall Score Comparison</div>',
            unsafe_allow_html=True)

bar_colors = ["#a78bfa", "#60a5fa", "#34d399", "#fbbf24", "#f472b6"]
names  = [e["name"] for e in ESSAYS]
scores = [e["overall"] for e in ESSAYS]

fig_bar = go.Figure()
for i, (name, sc, clr) in enumerate(zip(names, scores, bar_colors)):
    fig_bar.add_trace(go.Bar(
        x=[name], y=[sc], name=name.split(".")[0],
        marker=dict(color=clr, opacity=0.85, line=dict(width=0)),
        text=[sc], textposition="outside",
        textfont=dict(color="white", size=12),
    ))

avg_score = sum(scores) / len(scores)
fig_bar.add_hline(y=avg_score, line_dash="dot", line_color="rgba(255,255,255,0.3)",
                  annotation_text=f"Avg: {avg_score:.0f}", annotation_font_color="#9ca3af")

fig_bar.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af", family="Inter"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11, color="#e5e7eb")),
    yaxis=dict(range=[0, 110], gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=10)),
    height=320, margin=dict(l=10, r=10, t=20, b=10),
    showlegend=False, barmode="group",
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()
# Summary stats
sm1, sm2, sm3, sm4 = st.columns(4)
sm1.metric("Best Essay",    f"{ESSAYS[3]['name']} ({ESSAYS[3]['overall']}/100)")
sm2.metric("Avg Score",     f"{avg_score:.1f}/100")
sm3.metric("Lowest Score",  f"{min(scores)}/100")
sm4.metric("Improvement",   f"+{max(scores)-min(scores)} pts range")
