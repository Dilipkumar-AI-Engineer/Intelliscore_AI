"""
Essay Preview page – IntelliScore AI  (Page 14 in reference image)

Shows the full essay text in a rich viewer with formatting toolbar,
side-by-side with the score summary for the selected essay.
"""
import streamlit as st

from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Essay Preview – IntelliScore AI", page_icon="📄", layout="wide")
require_login()
render_sidebar()

# ── Sample essays for preview ─────────────────────────────────────────────────
SAMPLE_ESSAYS = {
    "Essay_1.pdf": {
        "title": "The Impact of Artificial Intelligence on Society",
        "overall": 86, "grammar": 90, "vocabulary": 85,
        "coherence": 82, "argument": 88, "readability": 80,
        "badge": "Excellent",
        "text": """The Impact of Artificial Intelligence on Society

Artificial Intelligence (AI) is transforming the world at an unprecedented pace. It is reshaping the way we live, work, and communicate. From healthcare to education, AI is everywhere.

One of the major benefits of AI is automation. It helps in reducing human effort and increases efficiency. For example, chatbots provide 24/7 customer support. Self-driving cars are another example of AI in transportation.

To conclude, the rapid advancement of AI has transformed our lives in countless ways. As we move forward, it is essential to use technology responsibly and ensure it benefits society as a whole.

However, AI also has some disadvantages. It may lead to job loss as machines can do tasks faster and better. There are also concerns about privacy and data security.

Furthermore, AI systems can perpetuate bias if trained on biased data. This can lead to unfair outcomes in hiring, lending, and law enforcement.

Despite these challenges, the benefits of AI far outweigh the drawbacks when properly governed. With the right policies and ethical frameworks, AI can be a powerful tool for human progress.

In conclusion, AI presents both remarkable opportunities and serious challenges for society. It is up to us — policymakers, technologists, and citizens alike — to ensure its development benefits humanity as a whole.""",
    },
    "Essay_2.docx": {
        "title": "Climate Change and Policy",
        "overall": 74, "grammar": 68, "vocabulary": 74,
        "coherence": 80, "argument": 72, "readability": 75,
        "badge": "Good",
        "text": """Climate Change and Policy

Climate change is one of the most pressing issues of our time. Global temperatures are rising, sea levels are increasing, and extreme weather events are becoming more frequent. It is imperative that governments, businesses, and individuals work together to address this crisis.

Policy interventions are critical in mitigating the effects of climate change. Carbon taxes, renewable energy subsidies, and strict emissions regulations are some of the tools at the disposal of policymakers. The Paris Agreement represents a landmark international effort to coordinate global climate action.

However, the effectiveness of climate policy depends largely on political will and international cooperation. Developing nations often face unique challenges in balancing economic growth with environmental sustainability.

In conclusion, addressing climate change requires a comprehensive and coordinated global response. Only through sustained political commitment and public awareness can we hope to mitigate the worst effects of this global crisis.""",
    },
    "Essay_3.txt": {
        "title": "Education System Reform",
        "overall": 91, "grammar": 95, "vocabulary": 88,
        "coherence": 90, "argument": 93, "readability": 89,
        "badge": "Outstanding",
        "text": """Education System Reform

The education system is the foundation of any progressive society. Yet, many educational systems around the world remain outdated, failing to prepare students for the demands of the 21st century. Comprehensive reform is not just desirable — it is essential.

One critical area of reform is curriculum design. Traditional curricula emphasize rote memorization over critical thinking and problem-solving. Modern education must prioritize skills such as creativity, collaboration, and digital literacy.

Teacher training and professional development also require significant attention. Educators must be equipped with the latest pedagogical strategies and technologies to effectively engage a new generation of learners.

Equity is another paramount concern. Educational quality should not be determined by geography or socioeconomic status. Governments must invest in infrastructure, resources, and support systems to ensure equal access to quality education for all students.

Finally, assessment methods must evolve. Standardized testing fails to capture the full range of student abilities and often creates undue pressure. Portfolio-based and competency-based assessments offer more holistic measures of student achievement.

In conclusion, education reform is a multi-faceted challenge that requires vision, commitment, and collaboration across all stakeholders. The future of our societies depends on our willingness to transform education today.""",
    },
}

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown('<div class="page-header">📄 Essay Preview</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Read, review, and annotate your full essay</div>',
            unsafe_allow_html=True)

st.markdown("""
<style>
.toolbar-wrap {
    display: flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 10px; padding: 0.5rem 0.8rem;
    margin-bottom: 0.8rem; flex-wrap: wrap;
}
.tb-btn {
    background: rgba(167,139,250,0.12);
    border: 1px solid rgba(167,139,250,0.25);
    color: #a78bfa; border-radius: 6px;
    padding: 3px 10px; font-size: 0.82rem;
    font-weight: 700; cursor: pointer;
    transition: background 0.2s;
}
.tb-btn:hover { background: rgba(167,139,250,0.25); }
.tb-sep { color: rgba(255,255,255,0.2); margin: 0 2px; }
.essay-body {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(167,139,250,0.18);
    border-radius: 14px; padding: 2rem 2.2rem;
    line-height: 1.85; color: #d1d5db;
    font-size: 0.95rem; min-height: 500px;
    white-space: pre-wrap;
}
.essay-body h1 { font-size: 1.35rem; font-weight: 800; color: #e5e7eb; margin-bottom: 1rem; }
.score-mini-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 12px; padding: 0.9rem 1rem;
    margin-bottom: 0.55rem; display: flex;
    justify-content: space-between; align-items: center;
}
.score-mini-label { color: #9ca3af; font-size: 0.82rem; font-weight: 500; }
.score-mini-val { font-weight: 700; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ── Essay selector ────────────────────────────────────────────────────────────
top_l, top_r = st.columns([4, 1])
with top_l:
    sel_name = st.selectbox(
        "Select Essay", list(SAMPLE_ESSAYS.keys()), label_visibility="collapsed"
    )
with top_r:
    if st.button("← Back to Results", use_container_width=True):
        st.switch_page("pages/5_Essay_Analysis.py")

essay = SAMPLE_ESSAYS[sel_name]

# ── Layout: viewer (left) + score panel (right) ───────────────────────────────
viewer_col, score_col = st.columns([3, 1], gap="large")

with viewer_col:
    # Formatting toolbar (cosmetic – Streamlit can't directly apply rich text,
    # so this is a visual toolbar to match the reference design)
    st.markdown("""
    <div class="toolbar-wrap">
        <span class="tb-btn">B</span>
        <span class="tb-btn"><i>I</i></span>
        <span class="tb-btn"><u>U</u></span>
        <span class="tb-sep">|</span>
        <span class="tb-btn">≡</span>
        <span class="tb-btn">☰</span>
        <span class="tb-btn">⚙</span>
        <span class="tb-sep">|</span>
        <span class="tb-btn">🔍 Find</span>
        <span class="tb-btn">⬅ Undo</span>
        <span class="tb-btn">➡ Redo</span>
        <span class="tb-sep">|</span>
        <span class="tb-btn">Aa Normal</span>
        <span style="margin-left:auto;color:#6b7280;font-size:0.75rem;">
            {wc} words · {sc} sentences
        </span>
    </div>
    """.format(
        wc=len(essay["text"].split()),
        sc=essay["text"].count(".") + essay["text"].count("!") + essay["text"].count("?"),
    ), unsafe_allow_html=True)

    # Essay body
    paragraphs = essay["text"].strip().split("\n\n")
    body_html = ""
    for i, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        if i == 0:
            body_html += f'<h2 style="font-size:1.25rem;font-weight:800;color:#e5e7eb;margin-bottom:1rem;">{para}</h2>'
        else:
            body_html += f'<p style="margin-bottom:1rem;">{para}</p>'

    st.markdown(f'<div class="essay-body">{body_html}</div>', unsafe_allow_html=True)

with score_col:
    overall = essay["overall"]
    badge = essay["badge"]
    badge_clr = "#34d399" if overall >= 80 else "#fbbf24" if overall >= 60 else "#ef4444"

    # Overall score circle
    st.markdown(f"""
    <div style="text-align:center;padding:1.4rem;background:linear-gradient(135deg,rgba(124,58,237,0.12),rgba(79,70,229,0.08));
                border:1px solid rgba(167,139,250,0.25);border-radius:16px;margin-bottom:1rem;">
        <div style="font-size:3.5rem;font-weight:900;
                    background:linear-gradient(135deg,#a78bfa,#60a5fa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {overall}
        </div>
        <div style="color:#9ca3af;font-size:0.8rem;">Overall Score</div>
        <div style="margin-top:0.6rem;">
            <span style="background:rgba({
                '52,211,153' if overall>=80 else '251,191,36' if overall>=60 else '239,68,68'
            },0.15);color:{badge_clr};border:1px solid rgba({
                '52,211,153' if overall>=80 else '251,191,36' if overall>=60 else '239,68,68'
            },0.3);border-radius:20px;padding:3px 14px;font-size:0.8rem;font-weight:700;">
                {'✅' if overall>=80 else '⚠️'} {badge}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.85rem;font-weight:700;color:#9ca3af;margin-bottom:0.5rem;">Score Breakdown</div>',
                unsafe_allow_html=True)

    criteria = [
        ("Grammar",    essay["grammar"],    "#34d399"),
        ("Vocabulary", essay["vocabulary"], "#60a5fa"),
        ("Coherence",  essay["coherence"],  "#a78bfa"),
        ("Argument",   essay["argument"],   "#fbbf24"),
        ("Readability",essay["readability"],"#f472b6"),
    ]
    for label, score, clr in criteria:
        st.markdown(f"""
        <div class="score-mini-card">
            <span class="score-mini-label">{label}</span>
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <div style="width:55px;background:rgba(255,255,255,0.06);border-radius:4px;height:4px;overflow:hidden;">
                    <div style="width:{score}%;height:100%;background:{clr};border-radius:4px;"></div>
                </div>
                <span class="score-mini-val" style="color:{clr};">{score}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons
    if st.button("🔍 Full Analysis", use_container_width=True):
        st.switch_page("pages/5_Essay_Analysis.py")
    if st.button("📊 Detailed View", use_container_width=True):
        st.switch_page("pages/6_Detailed_Analysis.py")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📄 Download Report", use_container_width=True):
        st.success("📄 Report prepared for download!")

st.divider()
nav_l, nav_r = st.columns(2)
with nav_l:
    st.page_link("pages/5_Essay_Analysis.py", label="← Back to Analysis")
with nav_r:
    st.page_link("pages/10_Reports.py", label="📄 Generate Report →")
