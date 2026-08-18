"""
Detailed Analysis page – IntelliScore AI  (Page 9 in reference image)
"""
import plotly.graph_objects as go
import streamlit as st

from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Detailed Analysis – IntelliScore AI", page_icon="🗂️", layout="wide")
require_login()
render_sidebar()

st.markdown('<div class="page-header">🗂️ Detailed Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Deep-dive into grammar, structure, and style metrics</div>',
            unsafe_allow_html=True)

CRITERIA = [
    ("Grammar",     90, "#34d399", "Excellent grammar with minimal errors detected."),
    ("Vocabulary",  85, "#60a5fa", "Rich vocabulary with good word diversity."),
    ("Coherence",   82, "#a78bfa", "Logical flow maintained throughout the essay."),
    ("Argument",    88, "#fbbf24", "Strong arguments supported with evidence."),
    ("Readability", 80, "#f472b6", "Clear and accessible writing style."),
]

GRAMMAR_ISSUES = [
    {"issue": "Subject-verb agreement", "count": 2, "severity": "Medium"},
    {"issue": "Article usage errors",   "count": 1, "severity": "Low"},
    {"issue": "Passive voice overuse",  "count": 3, "severity": "High"},
    {"issue": "Punctuation mistakes",  "count": 2, "severity": "Medium"},
]

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">Criteria Scores</div>',
                unsafe_allow_html=True)

    # Donut overall
    fig_donut = go.Figure(go.Indicator(
        mode="gauge+number",
        value=86,
        number={"font": {"color": "#ffffff", "size": 44, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#6b7280"},
            "bar": {"color": "#a78bfa", "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  50], "color": "rgba(239,68,68,0.1)"},
                {"range": [50, 75], "color": "rgba(251,191,36,0.1)"},
                {"range": [75,100], "color": "rgba(52,211,153,0.1)"},
            ],
        },
    ))
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#c4c4d4"},
        height=200, margin=dict(l=10, r=10, t=20, b=10),
    )
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown('<div style="text-align:center;"><span style="background:rgba(52,211,153,0.15);'
                'color:#34d399;border:1px solid rgba(52,211,153,0.3);border-radius:20px;'
                'padding:3px 14px;font-size:0.82rem;font-weight:700;">✅ Excellent</span></div>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    for name, score, clr, note in CRITERIA:
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:0.5rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            <div>
                <div style="color:#e5e7eb;font-weight:600;font-size:0.9rem;">{name}</div>
                <div style="color:#6b7280;font-size:0.72rem;">{note}</div>
            </div>
            <div style="background:rgba(255,255,255,0.06);border-radius:8px;
                        padding:4px 10px;font-weight:800;font-size:1rem;color:{clr};">{score}</div>
        </div>
        """, unsafe_allow_html=True)

with right_col:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">Grammar Analysis</div>',
                unsafe_allow_html=True)

    # Horizontal bar chart
    issue_names  = [i["issue"]  for i in GRAMMAR_ISSUES]
    issue_counts = [i["count"]  for i in GRAMMAR_ISSUES]
    colors = ["#ef4444" if i["severity"] == "High" else "#fbbf24" if i["severity"] == "Medium" else "#34d399"
              for i in GRAMMAR_ISSUES]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=issue_counts, y=issue_names, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=issue_counts, textposition="inside", textfont=dict(color="white", size=12),
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af", family="Inter"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=10, color="#e5e7eb")),
        height=200, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Grammar issue table
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Top Grammar Issues</div>',
                unsafe_allow_html=True)
    for issue in GRAMMAR_ISSUES:
        sev_clr = "#ef4444" if issue["severity"] == "High" else "#fbbf24" if issue["severity"] == "Medium" else "#34d399"
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:0.5rem 0.8rem;margin-bottom:0.3rem;
                    background:rgba(255,255,255,0.03);border-radius:8px;
                    border-left:3px solid {sev_clr};">
            <span style="color:#d1d5db;font-size:0.875rem;">{issue['issue']}</span>
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <span style="background:rgba(255,255,255,0.08);color:#e5e7eb;
                             border-radius:6px;padding:1px 8px;font-size:0.78rem;">{issue['count']}</span>
                <span style="color:{sev_clr};font-size:0.75rem;font-weight:600;">{issue['severity']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Radar chart
    st.markdown("<br>")
    cats = [c[0] for c in CRITERIA]
    vals = [c[1] for c in CRITERIA]
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself", line=dict(color="#a78bfa", width=2),
        fillcolor="rgba(167,139,250,0.12)",
    ))
    fig_r.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=8, color="#6b7280"),
                            gridcolor="rgba(255,255,255,0.08)"),
            angularaxis=dict(tickfont=dict(size=10, color="#9ca3af"), gridcolor="rgba(255,255,255,0.08)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af", family="Inter"),
        height=260, margin=dict(l=30, r=30, t=20, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_r, use_container_width=True)

st.divider()
navl, navr = st.columns(2)
with navl:
    st.page_link("pages/5_Essay_Analysis.py", label="← Back to Analysis")
with navr:
    st.page_link("pages/10_Reports.py", label="📄 Generate Report →")
