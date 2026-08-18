"""
Analytics page – IntelliScore AI  (Page 12 in reference image)
"""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Analytics – IntelliScore AI", page_icon="📈", layout="wide")
require_login()
render_sidebar()

st.markdown('<div class="page-header">📈 Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Comprehensive performance insights and progress tracking</div>',
            unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
kc1, kc2, kc3, kc4, kc5 = st.columns(5, gap="small")
kpis = [
    ("35",   "Total Essays",   "+5",   "#a78bfa"),
    ("84.2", "Average Score",  "+2.1", "#60a5fa"),
    ("95",   "Highest Score",  "↑",    "#34d399"),
    ("45",   "Lowest Score",   "—",    "#fbbf24"),
    ("5",    "AI-Flagged",     "-2",   "#f472b6"),
]
for col, (val, label, delta, clr) in zip([kc1, kc2, kc3, kc4, kc5], kpis):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:0.65rem;font-weight:700;color:{clr};text-align:right;
                        text-transform:uppercase;letter-spacing:0.06em;">This Month</div>
            <div class="stat-number" style="font-size:2rem;">{val}</div>
            <div class="stat-label">{label}</div>
            <div style="font-size:0.75rem;color:#34d399;margin-top:0.3rem;">↑ {delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts row ────────────────────────────────────────────────────────────────
pie_col, radar_col = st.columns([1, 1], gap="large")

with pie_col:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Score Distribution</div>',
                unsafe_allow_html=True)
    labels = ["0–20", "21–40", "41–60", "61–80", "81–100"]
    values = [1, 2, 4, 8, 20]
    colors = ["#ef4444", "#f59e0b", "#eab308", "#60a5fa", "#a78bfa"]
    fig_pie = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        textfont=dict(size=11, color="white"),
    ))
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#9ca3af", family="Inter"),
        height=300, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(orientation="v", x=1.0, y=0.5, font=dict(size=10, color="#9ca3af")),
        annotations=[dict(text=f"<b>35</b><br><span style='font-size:10px'>Essays</span>",
                          x=0.5, y=0.5, font_size=16, font_color="#e5e7eb", showarrow=False)],
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Legend pills
    for label, val, clr in zip(labels, values, colors):
        pct = round(val / sum(values) * 100)
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:3px 0;font-size:0.8rem;color:#9ca3af;">
            <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                               background:{clr};margin-right:6px;"></span>{label}</span>
            <span style="color:#e5e7eb;font-weight:600;">{pct}% ({val})</span>
        </div>
        """, unsafe_allow_html=True)

with radar_col:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Component Averages</div>',
                unsafe_allow_html=True)
    cats   = ["Grammar", "Vocabulary", "Coherence", "Argument", "Readability"]
    avgs   = [87, 82, 79, 85, 78]
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=avgs + [avgs[0]], theta=cats + [cats[0]],
        fill="toself", line=dict(color="#60a5fa", width=2.5),
        fillcolor="rgba(96,165,250,0.12)", name="Avg",
    ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=8, color="#6b7280"),
                            gridcolor="rgba(255,255,255,0.08)"),
            angularaxis=dict(tickfont=dict(size=11, color="#9ca3af"), gridcolor="rgba(255,255,255,0.08)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af", family="Inter"),
        height=320, margin=dict(l=50, r=50, t=20, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig_r, use_container_width=True)

    # Per-component mini table
    for cat, avg in zip(cats, avgs):
        clr = "#34d399" if avg >= 85 else "#60a5fa" if avg >= 75 else "#fbbf24"
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:4px 0;font-size:0.82rem;">
            <span style="color:#9ca3af;">{cat}</span>
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <div style="width:80px;background:rgba(255,255,255,0.06);border-radius:4px;height:5px;overflow:hidden;">
                    <div style="width:{avg}%;height:100%;background:{clr};border-radius:4px;"></div>
                </div>
                <span style="color:{clr};font-weight:700;font-size:0.85rem;">{avg}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Monthly trend ─────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Monthly Score Trend</div>',
            unsafe_allow_html=True)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
scores = [68, 72, 75, 78, 82, 79, 85, 84]
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=months, y=scores, mode="lines+markers",
    line=dict(color="#a78bfa", width=3, shape="spline"),
    marker=dict(color="#60a5fa", size=8, line=dict(color="white", width=1.5)),
    fill="tozeroy", fillcolor="rgba(167,139,250,0.07)",
))
fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#9ca3af", family="Inter"),
    yaxis=dict(range=[0, 110], gridcolor="rgba(255,255,255,0.06)"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
    height=220, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
)
st.plotly_chart(fig_line, use_container_width=True)
