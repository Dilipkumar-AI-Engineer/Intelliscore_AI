"""
Essay Analysis / Results page – IntelliScore AI  (Page 8 in reference image)
"""
import plotly.graph_objects as go
import streamlit as st

from utils.api_client import APIError, analyze_essay, get_essay, list_essays
from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Essay Analysis – IntelliScore AI", page_icon="🔍", layout="wide")
require_login()
render_sidebar()

# ── Mock analysis data ────────────────────────────────────────────────────────
MOCK_ANALYSIS = {
    "overall_score": 86,
    "sub_scores": {
        "grammar":     {"score": 90, "label": "Grammar",     "out": 100, "color": "#34d399"},
        "vocabulary":  {"score": 85, "label": "Vocabulary",  "out": 100, "color": "#60a5fa"},
        "coherence":   {"score": 82, "label": "Coherence",   "out": 100, "color": "#a78bfa"},
        "argument":    {"score": 88, "label": "Argument",    "out": 100, "color": "#fbbf24"},
        "readability": {"score": 80, "label": "Readability", "out": 100, "color": "#f472b6"},
    },
    "badge": "Excellent",
    "strengths": [
        "Well-structured paragraphs",
        "Strong vocabulary usage",
        "Good use of transition words",
    ],
    "improvements": [
        "Reduce passive voice usage",
        "Improve conclusion strength",
        "Add more specific examples",
    ],
    "overview_text": (
        "The essay is well-structured and presents its main points clearly. "
        "Strong use of vocabulary and coherent arguments throughout. "
        "The introduction is compelling and the body paragraphs flow logically."
    ),
    "corrections": [
        {"type": "Grammar",     "text": "Subject-verb agreement",  "count": 2},
        {"type": "Spelling",    "text": "Misspelled words found",  "count": 1},
        {"type": "Punctuation", "text": "Missing Oxford commas",   "count": 3},
    ],
    "keywords": ["Artificial Intelligence", "Technology", "Society", "Education", "Future", "Innovation"],
    "ai_prob": 12,
    "similarity": 4,
}

MOCK_ESSAYS = [
    {"id": 1, "title": "The Impact of AI on Society",  "file_type": "pdf",  "word_count": 980,
     "overall_score": 86, "created_at": "2025-05-15T10:00:00"},
    {"id": 2, "title": "Climate Change and Policy",    "file_type": "docx", "word_count": 750,
     "overall_score": 74, "created_at": "2025-05-08T10:00:00"},
    {"id": 3, "title": "Education System Reform",      "file_type": "txt",  "word_count": 620,
     "overall_score": 91, "created_at": "2025-04-30T10:00:00"},
]

# ── Load essays ───────────────────────────────────────────────────────────────
try:
    essays = list_essays() or MOCK_ESSAYS
except Exception:
    essays = MOCK_ESSAYS

st.markdown('<div class="page-header">🔍 Essay Analysis / Results</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Select an essay to view its detailed AI evaluation</div>',
            unsafe_allow_html=True)

# ── Essay selector ────────────────────────────────────────────────────────────
top_left, top_right = st.columns([3, 1])
with top_left:
    labels = {f'{e["title"]} ({e["file_type"].upper()})': e["id"] for e in essays}
    selected = st.selectbox("Select Essay", list(labels.keys()), label_visibility="collapsed")
    essay_id = labels[selected]
with top_right:
    analyze_btn = st.button("🔍 Analyze Essay", use_container_width=True)
    dl_btn = st.button("⬇️ Download Report", use_container_width=True)

if analyze_btn:
    with st.spinner("Running AI analysis..."):
        try:
            analysis = analyze_essay(essay_id)
        except Exception:
            analysis = MOCK_ANALYSIS
        st.session_state[f"analysis_{essay_id}"] = analysis

analysis = st.session_state.get(f"analysis_{essay_id}", MOCK_ANALYSIS)

st.divider()

# ── Overall score + sub-scores ────────────────────────────────────────────────
score_col, subs_col = st.columns([1, 2], gap="medium")

with score_col:
    overall = analysis["overall_score"]
    badge   = analysis.get("badge", "Good")

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall,
        number={"font": {"color": "#ffffff", "size": 48, "family": "Inter"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#6b7280", "tickwidth": 1},
            "bar": {"color": "#a78bfa", "thickness": 0.3},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  50], "color": "rgba(239,68,68,0.15)"},
                {"range": [50, 75], "color": "rgba(251,191,36,0.15)"},
                {"range": [75,100], "color": "rgba(52,211,153,0.15)"},
            ],
            "threshold": {"line": {"color": "#34d399", "width": 3}, "value": overall},
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#c4c4d4"},
        height=240, margin=dict(l=20, r=20, t=30, b=10),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(f"""
    <div style="text-align:center;">
        <span style="font-size:0.85rem;color:#9ca3af;">Overall Score</span><br>
        <span style="background:rgba(52,211,153,0.15);color:#34d399;
                     border:1px solid rgba(52,211,153,0.3);
                     border-radius:20px;padding:3px 14px;font-size:0.85rem;font-weight:700;">
            ✅ {badge}
        </span>
    </div>
    """, unsafe_allow_html=True)

with subs_col:
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#9ca3af;margin-bottom:0.8rem;">Sub-Scores</div>',
                unsafe_allow_html=True)
    sub_keys = list(analysis["sub_scores"].items())
    row1 = sub_keys[:3]
    row2 = sub_keys[3:]
    for row in [row1, row2]:
        cols = st.columns(len(row))
        for col, (key, sub) in zip(cols, row):
            score = sub["score"]
            clr   = sub.get("color", "#a78bfa")
            label = sub["label"]
            out   = sub.get("out", 100)
            with col:
                st.markdown(f"""
                <div class="sub-score-card">
                    <div class="sub-score-value" style="color:{clr};">{score}</div>
                    <div style="font-size:0.65rem;color:#6b7280;font-weight:500;">/{out}</div>
                    <div class="sub-score-label">{label}</div>
                    <div style="margin-top:0.5rem;background:rgba(255,255,255,0.06);
                                border-radius:4px;height:4px;overflow:hidden;">
                        <div style="width:{score}%;height:100%;background:{clr};border-radius:4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

st.divider()

# ── Tabs: Overview / Detailed / Corrections / Suggestions / AI Detection / Similarity ──
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📋 Overview", "🗂️ Detailed Analysis", "✏️ Corrections", "💡 Suggestions", "🤖 AI Detection", "🔗 Similarity"]
)

with tab1:
    t_left, t_right = st.columns([3, 2], gap="medium")
    with t_left:
        st.markdown("**Essay Summary**")
        st.markdown(f'<div class="glass-card"><p style="color:#d1d5db;line-height:1.8;">{analysis["overview_text"]}</p></div>',
                    unsafe_allow_html=True)
        st.markdown("<br>**Top Keywords**")
        kw_html = " ".join(
            f'<span style="background:rgba(167,139,250,0.15);color:#a78bfa;'
            f'border:1px solid rgba(167,139,250,0.3);border-radius:20px;'
            f'padding:3px 10px;font-size:0.78rem;font-weight:600;margin:2px;display:inline-block;">{kw}</span>'
            for kw in analysis["keywords"]
        )
        st.markdown(kw_html, unsafe_allow_html=True)
    with t_right:
        # Radar chart
        cats   = ["Grammar", "Vocabulary", "Coherence", "Argument", "Readability"]
        vals   = [analysis["sub_scores"][k.lower()]["score"] for k in cats]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            fill="toself", name="Score",
            line=dict(color="#a78bfa", width=2),
            fillcolor="rgba(167,139,250,0.15)",
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=9, color="#6b7280"),
                                gridcolor="rgba(255,255,255,0.08)"),
                angularaxis=dict(tickfont=dict(size=10, color="#9ca3af"),
                                 gridcolor="rgba(255,255,255,0.08)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af", family="Inter"),
            height=280, margin=dict(l=30, r=30, t=30, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_r, use_container_width=True)

        st.markdown("**Key Strengths**")
        for s in analysis["strengths"]:
            st.markdown(f'<div style="color:#34d399;font-size:0.85rem;">✅ {s}</div>', unsafe_allow_html=True)
        st.markdown("<br>**Areas to Improve**")
        for s in analysis["improvements"]:
            st.markdown(f'<div style="color:#fbbf24;font-size:0.85rem;">⚠️ {s}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("**Detailed criterion-level breakdown**")
    for key, sub in analysis["sub_scores"].items():
        sc = sub["score"]
        col_a, col_b = st.columns([1, 5])
        col_a.markdown(f'<div style="font-size:1.4rem;font-weight:800;color:{sub["color"]};">{sc}</div>'
                       f'<div style="font-size:0.75rem;color:#6b7280;">{sub["label"]}</div>',
                       unsafe_allow_html=True)
        col_b.markdown(f"""
        <div style="margin-top:0.3rem;">
            <div style="background:rgba(255,255,255,0.06);border-radius:6px;height:10px;overflow:hidden;">
                <div style="width:{sc}%;height:100%;background:{sub['color']};border-radius:6px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

with tab3:
    st.markdown("**Grammar & Style Corrections**")
    for c in analysis["corrections"]:
        st.markdown(f'<div style="background:rgba(239,68,68,0.08);border-left:3px solid #ef4444;'
                    f'border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;">'
                    f'<span style="color:#ef4444;font-weight:700;">{c["type"]}</span> · '
                    f'<span style="color:#d1d5db;">{c["text"]}</span> · '
                    f'<span style="color:#6b7280;font-size:0.8rem;">{c["count"]} found</span></div>',
                    unsafe_allow_html=True)

with tab4:
    st.markdown("**Writing Suggestions**")
    for i, sug in enumerate(analysis["improvements"], 1):
        st.markdown(f'<div style="background:rgba(96,165,250,0.07);border-left:3px solid #60a5fa;'
                    f'border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.5rem;color:#d1d5db;">'
                    f'<strong style="color:#60a5fa;">{i}.</strong> {sug}</div>',
                    unsafe_allow_html=True)

with tab5:
    ai_prob = analysis.get("ai_prob", 12)
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:3rem;font-weight:900;color:{'#34d399' if ai_prob < 30 else '#fbbf24' if ai_prob < 60 else '#ef4444'};">{ai_prob}%</div>
        <div style="color:#9ca3af;margin-top:0.3rem;">Probability of AI-Generated Content</div>
        <div style="margin-top:0.7rem;">
            <span style="font-size:0.85rem;color:#{'34d399' if ai_prob < 30 else 'fbbf24'};">
                {'✅ Likely Human-Written' if ai_prob < 30 else '⚠️ Possibly AI-Assisted'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab6:
    sim = analysis.get("similarity", 4)
    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <div style="font-size:3rem;font-weight:900;color:{'#34d399' if sim < 15 else '#fbbf24' if sim < 30 else '#ef4444'};">{sim}%</div>
        <div style="color:#9ca3af;margin-top:0.3rem;">Similarity with existing documents</div>
        <div style="margin-top:0.7rem;">
            <span style="font-size:0.85rem;color:#34d399;">✅ Highly Original Content</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
