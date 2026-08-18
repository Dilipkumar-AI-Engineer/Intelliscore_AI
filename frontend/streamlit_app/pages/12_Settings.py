"""
Profile & Settings page – IntelliScore AI  (Page 15 in reference image)
"""
import streamlit as st
from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Settings – IntelliScore AI", page_icon="⚙️", layout="wide")
require_login()
render_sidebar()

st.markdown('<div class="page-header">⚙️ Profile & Settings</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Manage your account, preferences, and notifications</div>',
            unsafe_allow_html=True)

user = st.session_state.user or {}
tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🎨 Preferences", "🔔 Notifications", "🔒 Security"])

# ── Profile tab ───────────────────────────────────────────────────────────────
with tab1:
    left, right = st.columns([1, 2], gap="large")
    with left:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem;background:rgba(255,255,255,0.03);
                    border:1px solid rgba(167,139,250,0.2);border-radius:16px;">
            <div style="width:90px;height:90px;border-radius:50%;
                        background:linear-gradient(135deg,#7c3aed,#4f46e5);
                        display:flex;align-items:center;justify-content:center;
                        font-size:2.5rem;margin:0 auto 0.8rem;border:3px solid rgba(167,139,250,0.3);">
                👤
            </div>
            <div style="font-size:1rem;font-weight:700;color:#e5e7eb;">Dilip Kumar</div>
            <div style="font-size:0.8rem;color:#a78bfa;margin-top:0.2rem;">Student</div>
            <div style="font-size:0.75rem;color:#6b7280;margin-top:0.2rem;">dilip@college.edu</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📸 Change Picture", use_container_width=True):
            st.info("Photo upload coming soon!")

    with right:
        with st.form("profile_form"):
            c1, c2 = st.columns(2)
            full_name   = c1.text_input("Full Name",    value=user.get("full_name", "Dilip Kumar"))
            email       = c2.text_input("Email",        value=user.get("email", "dilip@college.edu"))
            role        = c1.selectbox("Role",          ["Student", "Teacher", "Admin"],
                                       index=["student","teacher","admin"].index(user.get("role","student")))
            institution = c2.text_input("Institution",  value="ABC Engineering College")
            bio = st.text_area("Bio", value="Engineering student passionate about AI and writing.",
                               height=80)
            saved = st.form_submit_button("💾 Save Changes", use_container_width=True)
        if saved:
            st.success("✅ Profile updated successfully!")

# ── Preferences tab ───────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">Display Preferences</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        theme   = st.selectbox("Theme",    ["Dark (Default)", "Light", "Auto"])
        lang    = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"])
    with c2:
        tz      = st.selectbox("Timezone", ["Asia/Kolkata (IST)", "UTC", "US/Eastern"])
        date_fmt = st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])

    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin:1rem 0 0.6rem;">Analysis Defaults</div>',
                unsafe_allow_html=True)
    auto_analyze  = st.toggle("Auto-analyze on upload", value=True)
    show_tips     = st.toggle("Show writing tips in analysis", value=True)
    ai_detect     = st.toggle("Enable AI Detection check", value=True)
    similarity    = st.toggle("Enable Similarity check", value=False)

    if st.button("💾 Save Preferences", use_container_width=True):
        st.success("✅ Preferences saved!")

# ── Notifications tab ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">Email Notifications</div>',
                unsafe_allow_html=True)
    notif_items = [
        ("Analysis Complete",       "Get notified when essay analysis is done",         True),
        ("Weekly Progress Report",  "Receive your weekly writing progress summary",      True),
        ("AI Mentor Responses",     "Notifications for AI Writing Mentor replies",       False),
        ("New Feature Updates",     "Learn about new IntelliScore AI features",          True),
        ("Tips & Writing Advice",   "Receive personalized writing improvement tips",     False),
    ]
    for label, desc, default in notif_items:
        col_text, col_toggle = st.columns([4, 1])
        with col_text:
            st.markdown(f'<div style="color:#e5e7eb;font-weight:600;font-size:0.9rem;">{label}</div>'
                        f'<div style="color:#9ca3af;font-size:0.78rem;">{desc}</div>',
                        unsafe_allow_html=True)
        with col_toggle:
            st.toggle("", value=default, key=f"notif_{label[:10]}")
        st.markdown("")

    if st.button("💾 Save Notifications", use_container_width=True):
        st.success("✅ Notification settings saved!")

# ── Security tab ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">Change Password</div>',
                unsafe_allow_html=True)
    with st.form("password_form"):
        old_pw  = st.text_input("Current Password", type="password", placeholder="Enter current password")
        c1, c2  = st.columns(2)
        new_pw  = c1.text_input("New Password",     type="password", placeholder="New password")
        conf_pw = c2.text_input("Confirm Password", type="password", placeholder="Confirm new password")
        change  = st.form_submit_button("🔒 Change Password", use_container_width=True)
    if change:
        if not old_pw or not new_pw or not conf_pw:
            st.error("Please fill in all fields.")
        elif new_pw != conf_pw:
            st.error("New passwords do not match.")
        elif len(new_pw) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            st.success("✅ Password changed successfully!")

    st.divider()
    st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#e5e7eb;margin-bottom:0.5rem;">Two-Factor Authentication</div>',
                unsafe_allow_html=True)
    two_fa = st.toggle("Enable 2FA", value=False)
    if two_fa:
        st.info("📱 2FA setup will be sent to your registered email.")

    st.divider()
    st.markdown('<div style="color:#ef4444;font-size:0.95rem;font-weight:700;margin-bottom:0.5rem;">⚠️ Danger Zone</div>',
                unsafe_allow_html=True)
    if st.button("🗑️ Delete My Account", type="secondary"):
        st.warning("Account deletion is irreversible. Please contact support to proceed.")
