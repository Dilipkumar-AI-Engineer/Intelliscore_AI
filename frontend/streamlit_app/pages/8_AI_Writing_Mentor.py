"""
AI Writing Mentor (Chatbot) page – IntelliScore AI  (Page 11 in reference image)

Uses Google Gemini when GEMINI_API_KEY is configured; falls back to
rule-based responses in offline / demo mode.
"""
import os

import streamlit as st

from utils.layout import render_sidebar
from utils.session import require_login

st.set_page_config(page_title="AI Writing Mentor – IntelliScore AI", page_icon="🤖", layout="wide")
require_login()
render_sidebar()

# ── Gemini setup (optional – graceful fallback if key missing) ────────────────
_GEMINI_AVAILABLE = False
_gemini_model = None

_api_key = os.environ.get("GEMINI_API_KEY", "")
if not _api_key:
    # Try reading from .env in the repo root (for local dev convenience)
    try:
        import pathlib
        env_path = pathlib.Path(__file__).resolve().parents[4] / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    _api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    except Exception:
        pass

if _api_key and _api_key != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=_api_key)
        _gemini_model = genai.GenerativeModel(
            model_name=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
            system_instruction=(
                "You are an expert AI writing coach and essay mentor. "
                "You help students improve their essays by giving clear, actionable, "
                "encouraging feedback. Focus on grammar, vocabulary, coherence, argument "
                "strength, and essay structure. Keep responses concise (3-6 bullet points "
                "or short paragraphs). Use markdown formatting."
            ),
        )
        _GEMINI_AVAILABLE = True
    except Exception:
        _GEMINI_AVAILABLE = False

# ── Session chat history ──────────────────────────────────────────────────────
if "mentor_messages" not in st.session_state:
    st.session_state.mentor_messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Hello! I'm your **AI Writing Mentor**. I can help you improve your essays, "
                "fix grammar issues, expand your vocabulary, and strengthen your arguments.\n\n"
                "Try asking me:\n"
                "- *How can I improve my conclusion?*\n"
                "- *Can you suggest synonyms for 'important'?*\n"
                "- *How do I make my essay more persuasive?*"
            ),
        }
    ]

st.markdown('<div class="page-header">🤖 AI Writing Mentor</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subheader">Your personal AI assistant for essay improvement</div>',
            unsafe_allow_html=True)

# ── AI status badge ───────────────────────────────────────────────────────────
if _GEMINI_AVAILABLE:
    st.markdown(
        '<span style="background:rgba(52,211,153,0.15);color:#34d399;border:1px solid rgba(52,211,153,0.3);'
        'border-radius:20px;padding:3px 14px;font-size:0.78rem;font-weight:600;">'
        '✅ Gemini AI Connected</span>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<span style="background:rgba(251,191,36,0.12);color:#fbbf24;border:1px solid rgba(251,191,36,0.3);'
        'border-radius:20px;padding:3px 14px;font-size:0.78rem;font-weight:600;">'
        '⚡ Smart Demo Mode  (add GEMINI_API_KEY to .env for full AI)</span>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick suggestion chips ────────────────────────────────────────────────────
st.markdown('<div style="font-size:0.82rem;color:#9ca3af;margin-bottom:0.5rem;">Quick suggestions:</div>',
            unsafe_allow_html=True)

chips = [
    "How can I improve my conclusion?",
    "Suggest synonyms for 'important'",
    "Make my essay more persuasive",
    "Fix grammar mistakes",
    "Improve essay structure",
]
chip_cols = st.columns(len(chips))
for col, chip in zip(chip_cols, chips):
    if col.button(chip, key=f"chip_{chip[:15]}"):
        st.session_state.mentor_messages.append({"role": "user", "content": chip})
        if _GEMINI_AVAILABLE and _gemini_model:
            try:
                resp = _gemini_model.generate_content(chip)
                reply = resp.text
            except Exception as e:
                reply = f"⚠️ Gemini error: {e}\n\n*(Falling back to demo response)*\n\nFocus on clarity, structure, and evidence for stronger writing!"
        else:
            # Fallback responses
            fallback = {
                "How can I improve my conclusion?": (
                    "To improve your conclusion:\n\n"
                    "1. **Restate your thesis** in different words\n"
                    "2. **Summarize key points** without introducing new information\n"
                    "3. **End with impact** – a thought-provoking statement or call to action\n"
                    "4. **Avoid starting** with 'In conclusion' – try 'Ultimately' or 'Therefore'\n\n"
                    "Would you like me to rewrite your conclusion as an example?"
                ),
            }
            reply = fallback.get(
                chip,
                f"Great question about '*{chip}*'! Focus on clarity, coherence, and compelling arguments. "
                "Support every claim with evidence and maintain a consistent tone throughout. "
                "Would you like specific examples?"
            )
        st.session_state.mentor_messages.append({"role": "assistant", "content": reply})
        st.rerun()

st.divider()

# ── Chat messages ─────────────────────────────────────────────────────────────
chat_container = st.container(height=430)
with chat_container:
    for msg in st.session_state.mentor_messages:
        with st.chat_message(msg["role"],
                             avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
user_input = st.chat_input("Type your question or paste text for feedback...")

AI_RESPONSES = {
    "synonym": "Here are some powerful synonyms:\n- **Important** → *crucial, pivotal, significant, essential, critical*\n- **Good** → *excellent, outstanding, remarkable, exemplary*\n- **Show** → *demonstrate, illustrate, reveal, exhibit*",
    "grammar": "**Grammar Quick Fixes:**\n1. ✅ Use active voice: *'The AI analyzes essays'* not *'Essays are analyzed by AI'*\n2. ✅ Vary sentence length for rhythm\n3. ✅ Avoid run-on sentences – use semicolons or periods\n4. ✅ Check subject-verb agreement carefully\n\nPaste a specific sentence and I'll fix it for you!",
    "structure": "**Ideal Essay Structure:**\n\n📌 **Introduction** (10%)\n- Hook sentence → Background → Thesis\n\n📌 **Body Paragraphs** (80%)\n- Topic sentence → Evidence → Analysis → Transition\n\n📌 **Conclusion** (10%)\n- Restate thesis → Summarize → Closing thought",
    "default": "That's a great writing question! Here are some key principles:\n\n1. **Clarity** – Write to express, not to impress\n2. **Coherence** – Each paragraph should flow logically\n3. **Evidence** – Support every claim with facts or examples\n4. **Voice** – Maintain a consistent tone throughout\n\nWould you like me to analyze a specific section of your essay?",
}

if user_input:
    st.session_state.mentor_messages.append({"role": "user", "content": user_input})

    if _GEMINI_AVAILABLE and _gemini_model:
        with st.spinner("🤖 Gemini is thinking..."):
            try:
                resp = _gemini_model.generate_content(user_input)
                reply = resp.text
            except Exception as e:
                reply = f"⚠️ Gemini error: {e}\n\nPlease try again or check your API key."
    else:
        user_lower = user_input.lower()
        if any(w in user_lower for w in ["synonym", "word", "vocabulary"]):
            reply = AI_RESPONSES["synonym"]
        elif any(w in user_lower for w in ["grammar", "fix", "error", "mistake"]):
            reply = AI_RESPONSES["grammar"]
        elif any(w in user_lower for w in ["structure", "organize", "paragraph"]):
            reply = AI_RESPONSES["structure"]
        else:
            reply = AI_RESPONSES["default"]

    st.session_state.mentor_messages.append({"role": "assistant", "content": reply})
    st.rerun()

st.divider()
if st.button("🗑️ Clear Chat History", type="secondary"):
    st.session_state.mentor_messages = st.session_state.mentor_messages[:1]
    st.rerun()
