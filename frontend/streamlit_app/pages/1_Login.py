import streamlit as st

from utils.api_client import APIError, login
from utils.session import init_session_state, is_authenticated, log_in

st.set_page_config(page_title="Log In - IntelliScore AI", page_icon="🔐", layout="centered")
init_session_state()

st.title("🔐 Log In")

if is_authenticated():
    st.success("You're already logged in.")
    st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Log In", use_container_width=True)

if submitted:
    if not email or not password:
        st.error("Please enter both email and password.")
    else:
        try:
            result = login(email, password)
            log_in(result["access_token"], result["user"])
            st.success(f"Welcome back, {result['user']['full_name']}!")
            st.page_link("pages/3_Dashboard.py", label="Continue to Dashboard", icon="📊")
        except APIError as e:
            st.error(str(e))

st.divider()
st.caption("Don't have an account?")
st.page_link("pages/2_Register.py", label="Register here", icon="📝")
