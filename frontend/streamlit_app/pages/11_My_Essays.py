"""
My Essays page – IntelliScore AI  (Page 11 extended / sidebar item)
"""
import streamlit as st
from datetime import datetime, timedelta
from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="My Essays – IntelliScore AI", page_icon="📚", layout="wide")
require_login()
render_sidebar()

st.markdown('<div class="page-header">📚 My Essays</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Manage and review all your uploaded essays</div>',
            unsafe_allow_html=True)

# Search + filters row
s_col, f_col, sort_col, upload_col = st.columns([3, 1.5, 1.5, 1])
with s_col:
    search = st.text_input("Search essays...", placeholder="🔍  Search by title or type...",
                           label_visibility="collapsed")
with f_col:
    status_filter = st.selectbox("Status", ["All", "Analyzed", "Uploaded", "Pending"],
                                 label_visibility="collapsed")
with sort_col:
    sort_by = st.selectbox("Sort by", ["Date (Newest)", "Score (High)", "Score (Low)", "Title"],
                           label_visibility="collapsed")
with upload_col:
    st.page_link("pages/4_Upload_Essay.py", label="⬆️ Upload")

st.markdown("<br>", unsafe_allow_html=True)

# ── Mock essays data ──────────────────────────────────────────────────────────
base_date = datetime(2025, 5, 1)
ESSAYS = [
    {"title": "The Impact of AI on Society",    "type": "PDF",  "size": "345 KB", "words": 980,
     "score": 86, "status": "Analyzed", "date": base_date - timedelta(days=0)},
    {"title": "Climate Change and Policy",       "type": "DOCX", "size": "1.2 MB", "words": 750,
     "score": 74, "status": "Analyzed", "date": base_date - timedelta(days=7)},
    {"title": "Education System Reform",         "type": "TXT",  "size": "3.4 KB", "words": 620,
     "score": 91, "status": "Analyzed", "date": base_date - timedelta(days=14)},
    {"title": "Digital Privacy Rights",          "type": "PDF",  "size": "890 KB", "words": 1100,
     "score": None, "status": "Uploaded", "date": base_date - timedelta(days=21)},
    {"title": "Future of Renewable Energy",      "type": "DOCX", "size": "2.1 MB", "words": 1350,
     "score": None, "status": "Pending",  "date": base_date - timedelta(days=25)},
]

# Apply search filter
filtered = [e for e in ESSAYS
            if (not search or search.lower() in e["title"].lower() or search.lower() in e["type"].lower())
            and (status_filter == "All" or e["status"] == status_filter)]

# Summary row
sc1, sc2, sc3 = st.columns(3, gap="small")
analyzed_list = [e for e in ESSAYS if e["score"] is not None]
sc1.metric("Total Essays",     len(ESSAYS))
sc2.metric("Analyzed",         len(analyzed_list))
sc3.metric("Avg Score",        f"{sum(e['score'] for e in analyzed_list)/len(analyzed_list):.1f}" if analyzed_list else "—")

st.markdown("<br>", unsafe_allow_html=True)

# Table header
hc = st.columns([3, 0.8, 0.8, 0.8, 0.8, 1, 1, 1])
for col, h in zip(hc, ["Title", "Type", "Size", "Words", "Score", "Date", "Status", "Actions"]):
    col.markdown(f'<span style="color:#a78bfa;font-size:0.78rem;font-weight:700;">{h}</span>',
                 unsafe_allow_html=True)

for essay in filtered:
    score = essay["score"]
    pill = "pill-green" if (score or 0) >= 80 else "pill-yellow" if (score or 0) >= 60 else "pill-blue"
    status_pill = "pill-green" if essay["status"] == "Analyzed" else "pill-yellow" if essay["status"] == "Pending" else "pill-blue"
    score_text = f'{score}/100' if score else "—"
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([3, 0.8, 0.8, 0.8, 0.8, 1, 1, 1])
    c1.markdown(f'<span style="color:#e5e7eb;font-size:0.85rem;font-weight:600;">📄 {essay["title"]}</span>',
                unsafe_allow_html=True)
    c2.markdown(f'<span class="pill-blue" style="font-size:0.7rem;">{essay["type"]}</span>', unsafe_allow_html=True)
    c3.markdown(f'<span style="color:#9ca3af;font-size:0.82rem;">{essay["size"]}</span>', unsafe_allow_html=True)
    c4.markdown(f'<span style="color:#9ca3af;font-size:0.82rem;">{essay["words"]}</span>', unsafe_allow_html=True)
    c5.markdown(f'<span class="{pill}" style="font-size:0.72rem;">{score_text}</span>', unsafe_allow_html=True)
    c6.markdown(f'<span style="color:#9ca3af;font-size:0.78rem;">{essay["date"].strftime("%b %d, %Y")}</span>',
                unsafe_allow_html=True)
    c7.markdown(f'<span class="{status_pill}" style="font-size:0.72rem;">{essay["status"]}</span>',
                unsafe_allow_html=True)
    with c8:
        if score:
            st.page_link("pages/5_Essay_Analysis.py", label="📊")
        else:
            st.page_link("pages/5_Essay_Analysis.py", label="🔍 Analyze")

st.divider()
st.caption(f"Showing {len(filtered)} of {len(ESSAYS)} essays")
