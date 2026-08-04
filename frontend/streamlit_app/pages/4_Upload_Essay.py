import streamlit as st

from utils.api_client import APIError, upload_essay
from utils.session import require_login

st.set_page_config(page_title="Upload Essay - IntelliScore AI", page_icon="⬆️", layout="centered")
require_login()

st.title("⬆️ Upload an Essay")
st.caption("Supported formats: PDF, DOCX, TXT, PNG, JPG (images are read via OCR)")

uploaded_file = st.file_uploader(
    "Drag and drop or browse a file", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.write(f"**{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

    if st.button("Analyze Essay", use_container_width=True):
        with st.spinner("Uploading and extracting text... (image uploads take a few seconds longer, since OCR runs on CPU)"):
            try:
                file_bytes = uploaded_file.getvalue()
                result = upload_essay(file_bytes, uploaded_file.name)
                st.success(f"Uploaded successfully! {result['word_count']} words extracted.")
                st.page_link("pages/3_Dashboard.py", label="View in Dashboard", icon="📊")
            except APIError as e:
                st.error(f"Upload failed: {e}")
