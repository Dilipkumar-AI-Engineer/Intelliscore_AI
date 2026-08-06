"""
Shared sidebar navigation shell.

Concept: Streamlit auto-generates a sidebar page list from the pages/
folder, but it's plain text links with no branding, icons, or active-state
styling. We hide that default (`[data-testid="stSidebarNav"] {display:none}`)
and render our own, matching the reference mockup's dark branded sidebar
with icon navigation.

Call render_sidebar() near the top of every page, after st.set_page_config().
"""

import streamlit as st

from utils.session import is_authenticated, log_out

SIDEBAR_CSS = """
<style>
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1633 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
.sidebar-brand {
    font-size: 1.35rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 0.25rem;
}
.sidebar-user {
    color: #c4c4d4;
    font-size: 0.85rem;
    padding-bottom: 1rem;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] {
    border-radius: 10px;
    margin-bottom: 2px;
}
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
    background: rgba(167, 139, 250, 0.12);
}
</style>
"""

# (page_path, icon, label) -- shown only to authenticated users.
AUTHENTICATED_NAV = [
    ("pages/3_Dashboard.py", "📊", "Dashboard"),
    ("pages/4_Upload_Essay.py", "⬆️", "Upload Essays"),
    ("pages/5_Essay_Analysis.py", "🔍", "Essay Analysis"),
]


def render_sidebar():
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">📝 IntelliScore AI</div>', unsafe_allow_html=True)

        if is_authenticated():
            user = st.session_state.user
            st.markdown(
                f'<div class="sidebar-user">👤 {user["full_name"]}<br/>'
                f'<span style="opacity:0.7">{user["role"].capitalize()}</span></div>',
                unsafe_allow_html=True,
            )
            for path, icon, label in AUTHENTICATED_NAV:
                st.page_link(path, label=label, icon=icon)
            st.divider()
            if st.button("🚪 Log Out", use_container_width=True):
                log_out()
                st.switch_page("Home.py")
        else:
            st.page_link("Home.py", label="Home", icon="🏠")
            st.page_link("pages/1_Login.py", label="Log In", icon="🔐")
            st.page_link("pages/2_Register.py", label="Register", icon="📝")

        st.divider()
        st.caption("More pages (Compare, AI Mentor, Analytics, Reports, Settings) are coming in upcoming modules.")
