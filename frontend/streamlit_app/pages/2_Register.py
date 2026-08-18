"""
Sign Up page – IntelliScore AI
"""
import streamlit as st
from utils.api_client import APIError, register
from utils.layout import render_sidebar
from utils.session import init_session_state, is_authenticated, log_in, demo_login

st.set_page_config(page_title="Sign Up – IntelliScore AI", page_icon="📝", layout="centered")
init_session_state()
render_sidebar()

if is_authenticated():
    st.success("You're already logged in.")
    st.page_link("pages/3_Dashboard.py", label="📊 Go to Dashboard")
    st.stop()

st.markdown("""
<style>
.signup-title {
    font-size:1.8rem; font-weight:800;
    background:linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    text-align:center; margin-bottom:0.2rem;
}
.signup-sub { color:#9ca3af; font-size:0.9rem; text-align:center; margin-bottom:1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="signup-title">Create Your Account</div>', unsafe_allow_html=True)
st.markdown('<div class="signup-sub">Join thousands of learners and educators.</div>',
            unsafe_allow_html=True)

with st.form("register_form"):
    full_name = st.text_input("Full Name *", placeholder="Enter your full name")
    email     = st.text_input("Email Address *", placeholder="Enter your email")
    
    pc, cc = st.columns(2)
    password = pc.text_input("Password *", type="password", placeholder="Create password")
    confirm  = cc.text_input("Confirm Password *", type="password", placeholder="Confirm password")

    role = st.radio("I am a", ["Student", "Teacher", "Admin"], horizontal=True)

    st.markdown("""
    <div style="font-size:0.78rem; color:#6b7280; margin-top:0.5rem;">
    By signing up you agree to our <span style="color:#a78bfa;">Terms of Service</span>
    and <span style="color:#a78bfa;">Privacy Policy</span>.
    </div>
    """, unsafe_allow_html=True)

    submitted = st.form_submit_button("🚀 Sign Up", use_container_width=True)

if submitted:
    if not full_name or not email or not password or not confirm:
        st.error("Please fill in all required fields.")
    elif password != confirm:
        st.error("Passwords do not match.")
    elif len(password) < 8:
        st.error("Password must be at least 8 characters.")
    else:
        try:
            result = register(email, password, full_name, role.lower())
            log_in(result["access_token"], result["user"])
            st.success(f"Account created! Welcome, {full_name}! 🎉")
            st.switch_page("pages/3_Dashboard.py")
        except APIError as e:
            # Demo mode: allow exploring when backend is offline
            demo_login()
            st.success(f"✅ Welcome, {full_name}! (Running in demo mode — backend offline)")
            st.switch_page("pages/3_Dashboard.py")

st.divider()
st.markdown('<div style="text-align:center;margin-bottom:0.5rem;"><span style="color:#9ca3af;font-size:0.82rem;">— or explore without registering —</span></div>', unsafe_allow_html=True)
if st.button("🎮 Try Demo (No Backend Required)", use_container_width=True, type="secondary"):
    demo_login()
    st.success("✅ Demo mode activated! Welcome, Dilip Kumar!")
    st.switch_page("pages/3_Dashboard.py")

st.divider()
st.caption("Already have an account?")
st.page_link("pages/1_Login.py", label="🔐 Log In")
