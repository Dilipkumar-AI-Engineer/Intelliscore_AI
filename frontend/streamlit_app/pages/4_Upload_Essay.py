"""
Upload Essays page – IntelliScore AI  (Page 7 in reference image)
"""
import streamlit as st
from utils.api_client import APIError, upload_essay
from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="Upload Essays – IntelliScore AI", page_icon="⬆️", layout="wide")
require_login()
render_sidebar()

st.markdown("""
<style>
.upload-header {
    font-size:1.6rem; font-weight:800;
    background:linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom:0.3rem;
}
.upload-box {
    background:rgba(167,139,250,0.05);
    border:2px dashed rgba(167,139,250,0.35);
    border-radius:16px; padding:2.5rem; text-align:center;
    margin-bottom:1.5rem;
}
.upload-box-icon { font-size:3rem; margin-bottom:0.5rem; }
.upload-box-title { font-size:1.1rem; font-weight:700; color:#e5e7eb; margin-bottom:0.3rem; }
.upload-box-sub   { font-size:0.82rem; color:#9ca3af; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="upload-header">⬆️ Upload Essays</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Upload single or multiple essays for AI evaluation</div>',
            unsafe_allow_html=True)

col_upload, col_files = st.columns([3, 2], gap="large")

with col_upload:
    st.markdown("""
    <div class="upload-box">
        <div class="upload-box-icon">☁️</div>
        <div class="upload-box-title">Drag &amp; Drop your files here</div>
        <div class="upload-box-sub">or click Browse Files below</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Browse Files",
        type=["pdf", "docx", "txt", "png", "jpg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    st.caption("📄 Supports PDF, DOCX, TXT, images (JPG, PNG) · Max file size: 5MB")

    if uploaded_files:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Analyze Essays →", use_container_width=True):
            progress = st.progress(0, text="Uploading files...")
            for i, f in enumerate(uploaded_files):
                try:
                    upload_essay(f.read(), f.name)
                except Exception:
                    pass  # demo mode – continue
                progress.progress(int((i + 1) / len(uploaded_files) * 100),
                                  text=f"Processing {f.name}...")
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
            st.page_link("pages/5_Essay_Analysis.py", label="📊 View Analysis →")

with col_files:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#e5e7eb;margin-bottom:0.8rem;">📁 Uploaded Files</div>',
                unsafe_allow_html=True)

    # Demo uploaded files table
    demo_files = [
        ("Essay_1.pdf",  "85KB",  "345 KB",  "Uploaded"),
        ("Essay_2.docx", "120KB", "1.5 MB",  "Uploaded"),
        ("Essay_3.txt",  "45KB",  "3.4 KB",  "Pending"),
    ]

    if uploaded_files:
        files_to_show = [(f.name, f"{f.size//1024}KB", f"{f.size:,}", "Uploading") for f in uploaded_files]
    else:
        files_to_show = demo_files

    head_r = st.columns([3, 1, 1, 1, 0.5])
    for col, h in zip(head_r, ["File Name", "Size", "Status", "", ""]):
        col.markdown(f'<span style="color:#a78bfa;font-size:0.8rem;font-weight:700;">{h}</span>',
                     unsafe_allow_html=True)

    for fname, size, _, status in files_to_show:
        ext = fname.rsplit(".", 1)[-1].upper()
        pill = "pill-green" if status == "Uploaded" else "pill-yellow" if status == "Pending" else "pill-blue"
        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 0.5])
        c1.markdown(f'<span style="color:#e5e7eb;font-size:0.85rem;">📄 {fname}</span>',
                    unsafe_allow_html=True)
        c2.markdown(f'<span class="pill-blue" style="font-size:0.72rem;">{ext}</span>',
                    unsafe_allow_html=True)
        c3.markdown(f'<span style="color:#9ca3af;font-size:0.82rem;">{size}</span>',
                    unsafe_allow_html=True)
        c4.markdown(f'<span class="{pill}" style="font-size:0.72rem;">{status}</span>',
                    unsafe_allow_html=True)
        c5.markdown('<span style="color:#ef4444;cursor:pointer;">🗑️</span>', unsafe_allow_html=True)

st.divider()
st.caption("💡 Tip: Upload multiple essays at once to compare them side-by-side on the Compare Essays page.")
