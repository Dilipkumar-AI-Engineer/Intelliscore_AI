"""
Session state helpers.

Concept: Streamlit's `st.session_state` is a per-browser-session dict
that persists across page navigation WITHIN one running app (but resets
if the server restarts, or in a new browser tab). We store the JWT and
basic user info here after login -- every other page reads from here to
check "is someone logged in?" without re-calling the API on every
navigation.
"""

import streamlit as st


def init_session_state():
    """Call at the top of every page -- ensures keys exist before use."""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user" not in st.session_state:
        st.session_state.user = None


def is_authenticated() -> bool:
    return st.session_state.get("access_token") is not None


def log_in(access_token: str, user: dict):
    st.session_state.access_token = access_token
    st.session_state.user = user


def log_out():
    st.session_state.access_token = None
    st.session_state.user = None


def require_login():
    """
    Call at the top of any page that should be inaccessible when logged
    out. Shows a message and halts page execution (st.stop()) rather
    than letting the rest of the page render and hit auth errors.
    """
    init_session_state()
    if not is_authenticated():
        st.warning("Please log in to view this page.")
        st.page_link("pages/1_Login.py", label="Go to Login", icon="🔐")
        st.stop()
