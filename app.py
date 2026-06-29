import os
import re
import base64
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

st.set_page_config(
    page_title="Free AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp, html, body, [data-testid="stAppViewContainer"] { background: #07080D !important; }
.main .block-container { max-width: 720px !important; padding-top: 0 !important; padding-bottom: 8rem !important; }
#MainMenu, footer, header { visibility: hidden; }

.header {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 0; margin-bottom: 2rem;
    background: #07080D; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.brand { display: flex; align-items: center; gap: 10px; }
.logo {
    width: 30px; height: 30px; border-radius: 8px;
    background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.18);
    display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.app-title { font-size: 15px; font-weight: 600; color: #D0D4E0; }
.status {
    font-size: 9px; font-weight: 600; color: #38A169;
    background: rgba(56,161,105,0.08); border: 1px solid rgba(56,161,105,0.18);
    border-radius: 20px; padding: 2px 8px; letter-spacing: 0.8px; text-transform: uppercase;
}

.chat-row { display: flex; width: 100%; margin-bottom: 1.5rem; gap: 10px; align-items: flex-start; }
.user-row { justify-content: flex-end; }

.avatar {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-size: 11px; font-weight: 600; margin-top: 3px;
    background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.2); color: #818CF8;
}

.bubble { max-width: 80%; font-size: 14.5px; line-height: 1.75; word-wrap: break-word; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.user-bubble { background: #111420; border: 1px solid rgba(255,255,255,0.055); color: #BFC6D6; border-radius: 16px 16px 3px 16px; padding: 0.65rem 1rem; }

.chat-img { max-width: 280px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); margin-top: 6px; display: block; }

.img-preview-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15);
    border-radius: 8px; padding: 4px 10px; font-size: 12px; color: #818CF8; margin-bottom: 6px;
}
.img-preview-pill img { width: 24px; height: 24px; border-radius: 4px; object-fit: cover; }

/* Chat input styling */
.stChatInputContainer {
    background: #0C0E17 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important; transition: border-color 0.2s !important;
}
.stChatInputContainer:focus-within { border-color: rgba(99,102,241,0.2) !important; }
.stChatInputContainer textarea { color: #C8CEDB !important; font-size: 14px !important; background: transparent !important; }

/* File uploader — show only the browse button, hide the rest */
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important; border: none !important; padding: 0 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
section[data-testid="stFileUploader"] > label { display: none !important; }

div[data-testid="stButton"] > button {
    background: transparent !important; border: 1px solid rgba(255,255,255,0.05) !important;
    color: #4A5568 !important; font-size: 11px !important; border-radius: 8px !important;
    padding: 3px 12px !important; transition: all 0.15s !important;
}
div[data-testid="stButton"] > button:hover { border-color: rgba(255,255,255,0.09) !important; color: #A0AEC0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not API_KEY:
    st.error("🔑 API key not found. Set OPENROUTER_API_KEY in secrets.")
    st.stop()

# ── Constants ─────────────────────────────────────────────────────────────────
TEXT_MODEL   = "openrouter/owl-alpha"
VISION_MODEL = "google/gemini-2.0-flash-exp:free"

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Be concise and clear. "
    "Use markdown formatting for structure."
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "pending_image" not in st.session_state: st.session_state.pending_image = None
if "img_history"   not in st.session_state: st.session_state.img_history   = {}

# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_image(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")

def build_api_messages(history: list) -> list:
    """Convert session messages to OpenRouter API format."""
    out = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history:
        out.append(m)
    return out

def render_user_bubble(text: str, image_data: dict = None):
    safe = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe)
    safe = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         safe)
    safe = re.sub(r'`(.+?)`',       r'<code>\1</code>',     safe)
    safe = safe.replace("\n", "<br>")
    img_html = ""
    if image_data:
        img_html = f'<img src="data:{image_data["mime"]};base64,{image_data["data"]}" class="chat-img">'
    st.markdown(
        f'<div class="chat-row user-row"><div class="bubble user-bubble">{safe}{img_html}</div></div>',
        unsafe_allow_html=True,
    )

def render_ai_bubble(text: str):
    col1, col2 = st.columns([0.04, 0.96])
    with col1:
        st.markdown('<div class="avatar">✦</div>', unsafe_allow_html=True)
    with col2:
        # Use st.markdown (safe renderer, handles code blocks, tables etc.)
        st.markdown(text)

def call_api(messages: list, has_image: bool) -> str:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
        default_headers={"HTTP-Referer": "https://free-ai.app", "X-Title": "Free AI"},
    )
    model = VISION_MODEL if has_image else TEXT_MODEL
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="brand">
        <div class="logo">🤖</div>
        <div class="app-title">Free AI</div>
    </div>
    <div class="status">Online</div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
if st.session_state.messages:
    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        if st.button("✕  Clear", key="clear_chat"):
            st.session_state.messages      = []
            st.session_state.pending_image = None
            st.session_state.img_history   = {}
            st.rerun()

for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Extract text from content (may be str or list for vision messages)
        if isinstance(msg["content"], list):
            text = next((i["text"] for i in msg["content"] if i.get("type") == "text"), "")
        else:
            text = msg["content"]
        render_user_bubble(text, image_data=st.session_state.img_history.get(id(msg)))
    elif msg["role"] == "assistant":
        render_ai_bubble(msg["content"])

# ── Image preview ─────────────────────────────────────────────────────────────
if st.session_state.pending_image:
    p = st.session_state.pending_image
    c1, c2 = st.columns([9, 1])
    with c1:
        st.markdown(
            f'<div class="img-preview-pill">'
            f'<img src="data:{p["mime"]};base64,{p["data"]}">'
            f'<span>🖼️ {p["name"]}</span></div>',
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("✕", key="remove_img"):
            st.session_state.pending_image = None
            st.rerun()

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📎 Attach image",
    type=["png", "jpg", "jpeg", "webp"],
    key="img_uploader",
    label_visibility="visible",
)
if uploaded is not None:
    current = st.session_state.pending_image
    if current is None or current.get("name") != uploaded.name:
        st.session_state.pending_image = {
            "data": encode_image(uploaded.getvalue()),
            "mime": uploaded.type,
            "name": uploaded.name,
        }
        st.rerun()

# ── Chat input ────────────────────────────────────────────────────────────────
has_image = st.session_state.pending_image is not None
hint = "Ask about this image…" if has_image else "Message Free AI…"

if user_input := st.chat_input(hint):
    pending = st.session_state.pending_image  # capture before clearing

    # Build the message
    if pending:
        user_msg = {
            "role": "user",
            "content": [
                {"type": "text",      "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:{pending['mime']};base64,{pending['data']}"}},
            ],
        }
    else:
        user_msg = {"role": "user", "content": user_input}

    st.session_state.messages.append(user_msg)
    if pending:
        st.session_state.img_history[id(user_msg)] = pending
    st.session_state.pending_image = None

    # Render immediately
    render_user_bubble(user_input, image_data=pending)

    # Call API
    try:
        api_msgs = build_api_messages(st.session_state.messages)
        ai_text  = call_api(api_msgs, has_image=pending is not None)
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        render_ai_bubble(ai_text)
    except Exception as e:
        st.error(f"Error: {e}")

    st.rerun()
