import streamlit as st

from utils.api_client import APIError, register
from utils.session import init_session_state, is_authenticated

st.set_page_config(page_title="Register - IntelliScore AI", page_icon="📝", layout="centered")
init_session_state()

st.title("📝 Create Your Account")

if is_authenticated():
    st.success("You're already logged in.")
    st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

with st.form("register_form"):
    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    role = st.selectbox("I am a...", ["student", "teacher", "administrator"])
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    st.caption("Password must be at least 8 characters, with at least one letter and one number.")
    submitted = st.form_submit_button("Register", use_container_width=True)

if submitted:
    if not all([full_name, email, password, confirm_password]):
        st.error("Please fill in all fields.")
    elif password != confirm_password:
        st.error("Passwords do not match.")
    else:
        try:
            register(email=email, password=password, full_name=full_name, role=role)
            st.success("Account created! You can now log in.")
            st.page_link("pages/1_Login.py", label="Continue to Login", icon="🔐")
        except APIError as e:
            st.error(str(e))

st.divider()
st.caption("Already have an account?")
st.page_link("pages/1_Login.py", label="Log in here", icon="🔐")
