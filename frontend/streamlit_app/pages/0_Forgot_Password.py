"""
Forgot Password page – IntelliScore AI
"""
import streamlit as st
from utils.layout import render_sidebar
from utils.session import init_session_state

st.set_page_config(page_title="Forgot Password – IntelliScore AI", page_icon="🔑", layout="centered")
init_session_state()
render_sidebar()

st.markdown("""
<style>
.fp-icon {
    text-align:center; font-size:4rem; margin-bottom:0.5rem;
}
.fp-title {
    font-size:1.8rem; font-weight:800;
    background:linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; margin-bottom:0.3rem;
}
.fp-desc {
    color:#9ca3af; font-size:0.9rem; text-align:center;
    margin-bottom:1.5rem; line-height:1.6;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="fp-icon">🔑</div>', unsafe_allow_html=True)
st.markdown('<div class="fp-title">Forgot Password?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="fp-desc">No worries! Enter your email and we\'ll send you a reset link.</div>',
    unsafe_allow_html=True
)

with st.form("forgot_form"):
    email = st.text_input("Email Address", placeholder="Enter your email")
    submitted = st.form_submit_button("📧 Send Reset Link", use_container_width=True)

if submitted:
    if not email:
        st.error("Please enter your email address.")
    else:
        st.success(f"✅ Password reset link sent to **{email}** (check your inbox).")

st.divider()
st.caption("Remember your password?")
st.page_link("pages/1_Login.py", label="🔐 Log In")
