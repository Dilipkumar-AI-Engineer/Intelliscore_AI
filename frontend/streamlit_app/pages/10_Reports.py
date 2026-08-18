"""
Reports page – IntelliScore AI  (Page 13 in reference image)
"""
import plotly.graph_objects as go
import streamlit as st

from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Reports – IntelliScore AI", page_icon="📄", layout="wide")
require_login()
render_sidebar()

st.markdown('<div class="page-header">📄 Reports</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Generate and download detailed essay evaluation reports</div>',
            unsafe_allow_html=True)

left_col, right_col = st.columns([1, 2], gap="large")

ESSAY_OPTIONS = [
    "Essay_1.pdf", "Essay_2.docx", "Essay_3.pdf", "Essay_4.txt", "Essay_5.pdf"
]

REPORT_TYPES = [
    "Comprehensive Report",
    "Overall Score Report",
    "Compare Essays Report",
    "BluePrint",
    "Similarity Analysis",
]

with left_col:
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.6rem;">Select Essays</div>',
                unsafe_allow_html=True)
    selected_essays = st.multiselect(
        "Essays", ESSAY_OPTIONS, default=ESSAY_OPTIONS[:3],
        label_visibility="collapsed",
    )

    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin:0.8rem 0 0.4rem;">Report Options</div>',
                unsafe_allow_html=True)
    report_type = st.radio("Report Type", REPORT_TYPES, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    col_word, col_pdf = st.columns(2)
    with col_word:
        if st.button("⬇️ Download DOCX", use_container_width=True):
            st.success("📄 DOCX report generated!")
    with col_pdf:
        if st.button("⬇️ Download PDF", use_container_width=True):
            st.success("📄 PDF report generated!")

with right_col:
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.6rem;">Report Preview</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div style="text-align:center;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:1.2rem;margin-bottom:1.2rem;">
            <div style="font-size:0.9rem;font-weight:700;color:#a78bfa;letter-spacing:0.06em;">IntelliScore AI</div>
            <div style="font-size:1.25rem;font-weight:800;color:#e5e7eb;margin-top:0.3rem;">Essay Evaluation Report</div>
            <div style="font-size:0.78rem;color:#9ca3af;margin-top:0.2rem;">Student: Dilip Kumar &nbsp;|&nbsp; Date: Aug 2025</div>
        </div>
        <div style="display:flex;align-items:center;gap:1.5rem;margin-bottom:1.2rem;">
            <div style="text-align:center;background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(79,70,229,0.15));
                        border:2px solid rgba(167,139,250,0.3);border-radius:50%;
                        width:90px;height:90px;display:flex;flex-direction:column;
                        align-items:center;justify-content:center;flex-shrink:0;">
                <div style="font-size:2rem;font-weight:900;color:#a78bfa;">86</div>
                <div style="font-size:0.65rem;color:#9ca3af;margin-top:-3px;">Overall</div>
            </div>
            <div style="flex:1;">
                <div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Score Breakdown</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem;font-size:0.82rem;">
                    <span style="color:#9ca3af;">Grammar</span><span style="color:#34d399;font-weight:700;">90/100</span>
                    <span style="color:#9ca3af;">Vocabulary</span><span style="color:#60a5fa;font-weight:700;">85/100</span>
                    <span style="color:#9ca3af;">Coherence</span><span style="color:#a78bfa;font-weight:700;">82/100</span>
                    <span style="color:#9ca3af;">Argument</span><span style="color:#fbbf24;font-weight:700;">88/100</span>
                    <span style="color:#9ca3af;">Readability</span><span style="color:#f472b6;font-weight:700;">80/100</span>
                </div>
            </div>
        </div>
        <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);
                    border-radius:8px;padding:0.8rem;font-size:0.82rem;color:#9ca3af;line-height:1.7;">
            <strong style="color:#34d399;">Excellent Essay.</strong> Well-structured with strong vocabulary usage 
            and coherent argumentation. Minor improvements needed in passive voice reduction 
            and conclusion strength. Overall performance is outstanding.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Radar chart in preview
    st.markdown("<br>", unsafe_allow_html=True)
    cats = ["Grammar", "Vocabulary", "Coherence", "Argument", "Readability"]
    vals = [90, 85, 82, 88, 80]
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
        height=250, margin=dict(l=50, r=50, t=20, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_r, use_container_width=True)
