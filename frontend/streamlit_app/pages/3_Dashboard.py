import streamlit as st

from utils.api_client import APIError, list_essays
from utils.session import log_out, require_login

st.set_page_config(page_title="Dashboard - IntelliScore AI", page_icon="📊", layout="wide")
require_login()  # halts execution here if not logged in

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

# ---------- Stats ----------
total_essays = len(essays)
total_words = sum(e["word_count"] for e in essays)
avg_words = round(total_words / total_essays, 0) if total_essays else 0

stat_cols = st.columns(3)
stat_cols[0].metric("Total Essays", total_essays)
stat_cols[1].metric("Total Words Analyzed", f"{total_words:,}")
stat_cols[2].metric("Average Words / Essay", f"{avg_words:,.0f}")

st.divider()

# ---------- Quick actions ----------
st.subheader("Quick Actions")
action_cols = st.columns(3)
with action_cols[0]:
    st.page_link("pages/4_Upload_Essay.py", label="Upload New Essay", icon="⬆️")

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
            cols[3].caption(essay["created_at"][:10])
