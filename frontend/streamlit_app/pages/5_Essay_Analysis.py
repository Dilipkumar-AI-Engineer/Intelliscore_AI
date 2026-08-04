import plotly.graph_objects as go
import streamlit as st

from utils.api_client import APIError, analyze_essay, get_essay, list_essays
from utils.session import require_login

st.set_page_config(page_title="Essay Analysis - IntelliScore AI", page_icon="📊", layout="wide")
require_login()

# Consistent with Home.py's dark gradient theme.
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
    .score-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
    }
    .score-card .value { font-size: 2rem; font-weight: 700; color: #60a5fa; }
    .score-card .label { color: #c4c4d4; font-size: 0.9rem; }
    .score-card .explain { color: #8888a0; font-size: 0.78rem; margin-top: 0.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Essay Analysis")

# ---------- Essay selector ----------
try:
    essays = list_essays()
except APIError as e:
    st.error(f"Could not load essays: {e}")
    st.stop()

if not essays:
    st.info("You haven't uploaded any essays yet.")
    st.page_link("pages/4_Upload_Essay.py", label="Upload an essay", icon="⬆️")
    st.stop()

essay_labels = {f"{e['title']} ({e['file_type'].upper()})": e["id"] for e in essays}
selected_label = st.selectbox("Select an essay to analyze", list(essay_labels.keys()))
essay_id = essay_labels[selected_label]

essay = get_essay(essay_id)

col_a, col_b = st.columns([3, 1])
with col_a:
    st.caption(f"{essay['word_count']} words · Uploaded {essay['created_at'][:10]}")
with col_b:
    analyze_clicked = st.button("🔍 Analyze Essay", use_container_width=True)

# ---------- Run analysis ----------
if analyze_clicked:
    with st.spinner("Running NLP feature extraction and scoring..."):
        try:
            st.session_state[f"analysis_{essay_id}"] = analyze_essay(essay_id)
        except APIError as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

analysis = st.session_state.get(f"analysis_{essay_id}")

if analysis is None:
    if essay.get("overall_score") is not None:
        # Already analyzed previously -- re-fetch full detail via a fresh analyze
        # call is unnecessary; but we don't cache full features across sessions,
        # so prompt to re-run for the detailed view.
        st.info(f"Previously analyzed -- Overall Score: {essay['overall_score']}/100. Click 'Analyze Essay' to see the full breakdown again.")
    else:
        st.info("Click 'Analyze Essay' to generate a score and detailed breakdown.")
    st.stop()

# ---------- Overall score gauge ----------
overall = analysis["overall_score"]
sub_scores = analysis["sub_scores"]
features = analysis["features"]

gauge_col, cards_col = st.columns([1, 2])

with gauge_col:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=overall,
            number={"suffix": "/100", "font": {"color": "#ffffff", "size": 40}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#c4c4d4"},
                "bar": {"color": "#a78bfa"},
                "bgcolor": "rgba(255,255,255,0.05)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(239,68,68,0.25)"},
                    {"range": [50, 75], "color": "rgba(251,191,36,0.25)"},
                    {"range": [75, 100], "color": "rgba(34,197,94,0.25)"},
                ],
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#c4c4d4"},
        height=300,
        margin=dict(l=20, r=20, t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Overall Score: XGBoost model prediction (Module 3). "
        "⚠️ Trained on synthetic data -- see project notes."
    )

with cards_col:
    score_cols = st.columns(3)
    labels = {
        "grammar": "Grammar",
        "vocabulary": "Vocabulary",
        "coherence": "Coherence",
        "argument": "Argument",
        "readability": "Readability",
    }
    for i, (key, label) in enumerate(labels.items()):
        detail = sub_scores[key]
        with score_cols[i % 3]:
            st.markdown(
                f"""<div class="score-card">
                    <div class="value">{detail['score']:.0f}</div>
                    <div class="label">{label}</div>
                    <div class="explain">{detail['explanation']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            st.write("")

st.divider()

# ---------- Detailed analysis tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["Grammar & Style", "Vocabulary", "Structure", "Keywords"])

with tab1:
    passive = features["passive_voice"]
    spelling = features["spelling"]
    st.subheader("Passive Voice")
    st.write(f"{passive['passive_sentence_count']} of {passive['total_sentences']} sentences ({passive['passive_ratio_percent']}%) are passive voice.")
    for sent in passive["flagged_sentences"]:
        st.warning(f"**{sent['sentence']}**\n\n💡 {sent['suggestion']}")

    st.subheader("Spelling")
    if spelling["misspelled_count"] == 0:
        st.success("No spelling issues detected.")
    else:
        for item in spelling["misspelled_words"]:
            st.write(f"❌ **{item['word']}** → suggested: *{item['suggested_correction']}*")

with tab2:
    diversity = features["lexical_diversity"]
    repeated = features["repeated_words"]
    st.metric("Unique Words", diversity["unique_words"])
    st.metric("Vocabulary Richness (Root TTR)", diversity["root_ttr"])

    st.subheader("Repeated Words")
    if not repeated["overused_words"]:
        st.success("No excessive word repetition detected.")
    else:
        for word in repeated["overused_words"]:
            synonyms = ", ".join(word["synonyms"]) if word["synonyms"] else "none found"
            st.write(f"🔁 **{word['word']}** used {word['count']}x -- try: *{synonyms}*")

with tab3:
    pos = features["pos_distribution"]["distribution"]
    import plotly.express as px

    pos_labels = list(pos.keys())
    pos_values = [v["count"] for v in pos.values()]
    fig_pos = px.bar(
        x=pos_values, y=pos_labels, orientation="h",
        labels={"x": "Count", "y": ""},
        color_discrete_sequence=["#a78bfa"],
    )
    fig_pos.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#c4c4d4"}, height=350,
    )
    st.subheader("Part-of-Speech Distribution")
    st.plotly_chart(fig_pos, use_container_width=True)

    st.subheader("Transitions Used")
    trans = features["transitions"]
    st.write(f"{trans['total_transitions_found']} transition word(s) found ({trans['transitions_per_sentence']} per sentence)")
    for phrase in trans["phrases_found"]:
        st.write(f"• *{phrase['phrase']}* ({phrase['category'].replace('_', ' ')})")

with tab4:
    st.subheader("Top Keywords (TF-IDF)")
    for kw in features["keywords"][:10]:
        st.write(f"**{kw['term']}** -- {kw['score']}")

    st.subheader("Named Entities")
    if not features["named_entities"]:
        st.info("No named entities detected.")
    for ent in features["named_entities"]:
        st.write(f"**{ent['text']}** -- {ent['explanation']}")
