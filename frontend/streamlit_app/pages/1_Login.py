"""
Login page – IntelliScore AI
"""
import streamlit as st
from utils.api_client import APIError, login
from utils.layout import render_sidebar
from utils.session import init_session_state, is_authenticated, log_in, demo_login

st.set_page_config(page_title="Log In – IntelliScore AI", page_icon="🔐", layout="centered")
init_session_state()
render_sidebar()

if is_authenticated():
    st.success("You're already logged in.")
    st.page_link("pages/3_Dashboard.py", label="📊 Go to Dashboard")
    st.stop()

st.markdown("""
<style>
.login-card {
    max-width: 420px; margin: 2rem auto;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 20px; padding: 2.5rem 2rem;
    backdrop-filter: blur(12px);
}
.login-title {
    font-size:1.8rem; font-weight:800;
    background:linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; margin-bottom:0.3rem;
}
.login-sub { color:#9ca3af; font-size:0.9rem; text-align:center; margin-bottom:1.5rem; }
.social-btn {
    display:flex; align-items:center; justify-content:center; gap:0.5rem;
    background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12);
    border-radius:10px; padding:0.65rem; color:#e5e7eb;
    font-size:0.9rem; font-weight:600; cursor:pointer;
    transition:background 0.2s;
}
.social-btn:hover { background:rgba(255,255,255,0.1); }
.or-divider { color:#6b7280; text-align:center; margin:1rem 0; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-title">Welcome Back! 👋</div>', unsafe_allow_html=True)
st.markdown('<div class="login-sub">Sign in to your IntelliScore account</div>', unsafe_allow_html=True)

# Tab-style: Login / Login with OTP
tab_email, tab_otp = st.tabs(["Login", "Login with OTP"])

with tab_email:
    with st.form("login_form"):
        email    = st.text_input("Email Address", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        c1, c2   = st.columns(2)
        remember = c1.checkbox("Remember me", value=True)
        submitted = st.form_submit_button("🔐 Log In", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
        else:
            try:
                result = login(email, password)
                log_in(result["access_token"], result["user"])
                st.success(f"Welcome back, {result['user']['full_name']}! 🎉")
                st.page_link("pages/3_Dashboard.py", label="📊 Continue to Dashboard")
            except APIError as e:
                st.error(str(e))

    st.markdown('<div class="or-divider">— or continue with —</div>', unsafe_allow_html=True)
    g_col, m_col = st.columns(2)
    with g_col:
        st.markdown('<div class="social-btn">🔵 Google</div>', unsafe_allow_html=True)
    with m_col:
        st.markdown('<div class="social-btn">🟦 Microsoft</div>', unsafe_allow_html=True)

with tab_otp:
    otp_email = st.text_input("Email Address", placeholder="Enter your email", key="otp_email")
    if st.button("Send OTP", use_container_width=True, key="send_otp"):
        st.info("📧 OTP sent to your email (demo mode).")
    otp_code = st.text_input("Enter OTP", placeholder="6-digit code", key="otp_code")
    if st.button("Verify & Login", use_container_width=True, key="verify_otp"):
        st.warning("OTP verification requires backend integration.")

st.divider()
st.markdown('<div style="text-align:center;margin-bottom:0.5rem;"><span style="color:#9ca3af;font-size:0.82rem;">— or explore without an account —</span></div>', unsafe_allow_html=True)
if st.button("🎮 Try Demo (No Backend Required)", use_container_width=True, type="secondary"):
    demo_login()
    st.success("✅ Demo mode activated! Welcome, Dilip Kumar!")
    st.switch_page("pages/3_Dashboard.py")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.caption("Don't have an account?")
    st.page_link("pages/2_Register.py", label="📝 Sign Up")
with c2:
    st.caption("Forgot your password?")
    st.page_link("pages/0_Forgot_Password.py", label="🔑 Reset Password")
