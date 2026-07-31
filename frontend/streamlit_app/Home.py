"""
Streamlit entrypoint.

Streamlit's convention: the file you run with `streamlit run` is the
"main" page, and anything in a sibling `pages/` folder becomes an
auto-generated sidebar page (e.g. pages/1_Dashboard.py, pages/2_Upload.py).
We'll populate `pages/` starting in Module 7. For now this just proves
the frontend process boots and can (eventually) reach the backend.
"""

import streamlit as st

st.set_page_config(
    page_title="IntelliScore AI",
    page_icon="📝",
    layout="wide",
)

st.title("IntelliScore AI")
st.caption("Explainable AI Platform for Automated Essay Evaluation")
st.success("Frontend scaffolding is running. Backend, auth, and pages come in later modules.")
