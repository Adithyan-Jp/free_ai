import os
import re
import base64
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")

st.set_page_config(
    page_title="Aether AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp, html, body, [data-testid="stAppViewContainer"] { background: #07080D !important; }
.main .block-container { max-width: 720px !important; padding-top: 0 !important; padding-bottom: 8rem !important; }
#MainMenu, footer, header { visibility: hidden; }

.aether-header {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 0; margin-bottom: 2rem;
    background: #07080D; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.aether-brand { display: flex; align-items: center; gap: 10px; }
.aether-logo {
    width: 30px; height: 30px; border-radius: 8px;
    background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.18);
    display: flex; align-items: center; justify-content: center; font-size: 14px;
}
.aether-title { font-size: 15px; font-weight: 600; color: #D0D4E0; letter-spacing: -0.2px; }
.aether-badge {
    font-size: 9px; font-weight: 600; color: #38A169;
    background: rgba(56,161,105,0.08); border: 1px solid rgba(56,161,105,0.18);
    border-radius: 20px; padding: 2px 8px; letter-spacing: 0.8px; text-transform: uppercase;
}

.chat-row { display: flex; width: 100%; margin-bottom: 1.5rem; gap: 10px; align-items: flex-start; }
.chat-row.user-row { justify-content: flex-end; }

.avatar {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-size: 11px; font-weight: 600; margin-top: 3px;
}
.avatar.ai { background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.2); color: #818CF8; }

.bubble { max-width: 80%; font-size: 14.5px; line-height: 1.75; word-wrap: break-word; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.bubble.user-bubble { background: #111420; border: 1px solid rgba(255,255,255,0.055); color: #BFC6D6; border-radius: 16px 16px 3px 16px; padding: 0.65rem 1rem; }
.bubble.assistant-bubble { background: transparent; color: #7E8A99; padding: 0.1rem 0; }
.bubble.assistant-bubble p { margin: 0 0 0.5rem; color: #8A95A3; }
.bubble.assistant-bubble p:last-child { margin-bottom: 0; }
.bubble.assistant-bubble strong { color: #C0C8D8; font-weight: 600; }
.bubble.assistant-bubble em { color: #6E7D8C; font-style: italic; }
.bubble.assistant-bubble ul, .bubble.assistant-bubble ol { margin: 0.35rem 0 0.35rem 1.15rem; padding: 0; }
.bubble.assistant-bubble li { margin-bottom: 4px; color: #8A95A3; }
.bubble.assistant-bubble h1, .bubble.assistant-bubble h2, .bubble.assistant-bubble h3 { color: #C0C8D8; font-weight: 600; margin: 0.8rem 0 0.35rem; }
.bubble.assistant-bubble h1 { font-size: 17px; }
.bubble.assistant-bubble h2 { font-size: 15px; }
.bubble.assistant-bubble h3 { font-size: 14px; }
.bubble.assistant-bubble code { background: #0D0F18; border: 1px solid rgba(255,255,255,0.07); padding: 2px 6px; border-radius: 5px; font-family: "Fira Code", "JetBrains Mono", monospace; font-size: 12.5px; color: #7EB8D4; }
.bubble.assistant-bubble pre { background: #0A0C14; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.9rem 1.1rem; overflow-x: auto; margin: 0.75rem 0; }
.bubble.assistant-bubble pre code { background: none; border: none; padding: 0; color: #9BAFC0; font-size: 12.5px; }
.bubble.assistant-bubble blockquote { border-left: 2px solid rgba(99,102,241,0.3); margin: 0.5rem 0; padding-left: 0.9rem; color: #6E7D8C; }
.bubble.assistant-bubble hr { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 0.75rem 0; }
.bubble.assistant-bubble table { border-collapse: collapse; width: 100%; font-size: 13px; margin: 0.5rem 0; }
.bubble.assistant-bubble th, .bubble.assistant-bubble td { border: 1px solid rgba(255,255,255,0.07); padding: 6px 10px; text-align: left; }
.bubble.assistant-bubble th { color: #C0C8D8; background: rgba(255,255,255,0.03); }

.chat-img { max-width: 280px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); margin-top: 6px; display: block; }

/* Chat input area with paperclip */
.chat-input-container {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top, #07080D 80%, transparent);
    padding: 1.5rem 0 1rem;
    z-index: 99;
}
.chat-input-wrapper {
    max-width: 720px; margin: 0 auto;
    display: flex; align-items: flex-end; gap: 8px;
}
.chat-input-box {
    flex: 1;
    background: #0C0E17;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 0.5rem 0.75rem;
    transition: border-color 0.2s;
}
.chat-input-box:focus-within {
    border-color: rgba(99,102,241,0.2);
}
.chat-input-box textarea {
    background: transparent !important;
    border: none !important;
    color: #C8CEDB !important;
    font-size: 14px !important;
    resize: none !important;
    box-shadow: none !important;
    padding: 0.25rem 0 !important;
    min-height: 24px !important;
    max-height: 120px !important;
}
.chat-input-box textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

.paperclip-btn {
    width: 40px; height: 40px;
    background: #0C0E17;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: all 0.15s;
    color: #4A5568;
    font-size: 18px;
    flex-shrink: 0;
}
.paperclip-btn:hover {
    border-color: rgba(99,102,241,0.2);
    color: #818CF8;
    background: rgba(99,102,241,0.05);
}
.paperclip-btn.has-image {
    border-color: rgba(99,102,241,0.3);
    color: #818CF8;
    background: rgba(99,102,241,0.08);
}

.send-btn {
    width: 40px; height: 40px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: all 0.15s;
    color: #818CF8;
    font-size: 16px;
    flex-shrink: 0;
}
.send-btn:hover {
    background: rgba(99,102,241,0.18);
    border-color: rgba(99,102,241,0.3);
}

/* Image preview pill */
.img-preview-container {
    max-width: 720px; margin: 0 auto 0.5rem;
    display: flex; align-items: center; gap: 8px;
}
.img-preview-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.15);
    border-radius: 10px; padding: 6px 12px; font-size: 12px; color: #818CF8;
}
.img-preview-pill img { width: 32px; height: 32px; border-radius: 6px; object-fit: cover; }
.img-remove-btn {
    background: none; border: none; color: #4A5568; cursor: pointer;
    font-size: 16px; padding: 2px 6px; border-radius: 4px; transition: color 0.15s;
}
.img-remove-btn:hover { color: #E53E3E; }

/* Hide default streamlit chat input */
[data-testid="stChatInput"] { display: none !important; }

div[data-testid="stButton"] > button {
    background: transparent !important; border: 1px solid rgba(255,255,255,0.05) !important;
    color: #4A5568 !important; font-size: 11px !important; border-radius: 8px !important;
    padding: 3px 12px !important; letter-spacing: 0.3px; transition: all 0.15s !important;
}
div[data-testid="stButton"] > button:hover { border-color: rgba(255,255,255,0.09) !important; color: #A0AEC0 !important; }

/* File uploader hidden */
[data-testid="stFileUploader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not API_KEY:
    st.error("🔑 OpenRouter API key not found.")
    st.stop()

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = {
    "text":      "openrouter/owl-alpha",
    "reasoning": "openrouter/owl-alpha",
    "coding":    "openrouter/owl-alpha",
    "vision":    "google/gemini-2.0-flash-exp:free",
}

SYSTEM_PROMPT = (
    "You are Aether, an elite AI intelligence engine powered by OpenRouter Owl Alpha. "
    "Be concise and precise. Use markdown for structure: bold key terms, "
    "use bullet points for lists, and fenced code blocks for code. "
    "Never pad responses with filler phrases."
)
CODING_SYSTEM_PROMPT = (
    "You are Aether Code, an expert programming assistant powered by OpenRouter Owl Alpha. "
    "Write clean, well-documented code. Always include type hints and docstrings. "
    "Explain your reasoning briefly before showing code. Use best practices."
)
VISION_SYSTEM_PROMPT = (
    "You are Aether Vision, an AI that can see and understand images. "
    "Describe images accurately and concisely. Be precise about details you observe."
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = [{"role": "system", "content": SYSTEM_PROMPT}]
if "mode"          not in st.session_state: st.session_state.mode          = "text"
if "pending_image" not in st.session_state: st.session_state.pending_image = None
if "img_history"   not in st.session_state: st.session_state.img_history   = {}
if "chat_input"    not in st.session_state: st.session_state.chat_input    = ""
if "uploader_key"  not in st.session_state: st.session_state.uploader_key  = 0

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_model(mode, has_image=False):
    return MODELS["vision"] if has_image else MODELS[mode]

def get_system_prompt(mode, has_image=False):
    if has_image:   return VISION_SYSTEM_PROMPT
    if mode == "coding": return CODING_SYSTEM_PROMPT
    return SYSTEM_PROMPT

def encode_image(file_bytes):
    return base64.b64encode(file_bytes).decode("utf-8")

def build_user_message(text, image_b64=None, mime_type="image/png"):
    if image_b64:
        return {"role": "user", "content": [
            {"type": "text",      "text": text or "What do you see in this image?"},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
        ]}
    return {"role": "user", "content": text}

def render_message(role, content, image_data=None):
    display_text = content
    if isinstance(content, list):
        parts = [i["text"] for i in content if i.get("type") == "text"]
        display_text = " ".join(parts) if parts else ""

    if role == "user":
        safe = (str(display_text)
                .replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
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
    else:
        col1, col2 = st.columns([0.04, 0.96])
        with col1:
            st.markdown('<div class="avatar ai" style="margin-top:6px">✦</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(display_text)

def stream_response(messages, model_id):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
        default_headers={"HTTP-Referer": "https://aether-ai.app", "X-Title": "Aether AI"},
    )
    col1, col2 = st.columns([0.04, 0.96])
    with col1:
        st.markdown('<div class="avatar ai" style="margin-top:6px">✦</div>', unsafe_allow_html=True)
    with col2:
        ph = st.empty()
        accumulated = ""
        with client.chat.completions.create(model=model_id, messages=messages, stream=True) as stream:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    accumulated += chunk.choices[0].delta.content
                    ph.markdown(accumulated + "▋")
        ph.markdown(accumulated)
    return accumulated

def process_message():
    user_input = st.session_state.chat_input.strip()
    if not user_input and not st.session_state.pending_image:
        return

    pending = st.session_state.pending_image

    if pending:
        user_msg = build_user_message(user_input, image_b64=pending["data"], mime_type=pending["mime"])
        st.session_state.messages[0] = {"role": "system", "content": get_system_prompt(st.session_state.mode, has_image=True)}
    else:
        user_msg = build_user_message(user_input)

    st.session_state.messages.append(user_msg)

    if pending:
        st.session_state.img_history[id(user_msg)] = pending

    st.session_state.pending_image = None
    st.session_state.chat_input = ""
    st.session_state.uploader_key += 1

    st.session_state["_trigger_send"] = True

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aether-header">
    <div class="aether-brand">
        <div class="aether-logo">✨</div>
        <div class="aether-title">Aether</div>
    </div>
    <div class="aether-badge">Online</div>
</div>
""", unsafe_allow_html=True)

# ── Mode selector ─────────────────────────────────────────────────────────────
modes = ["text", "reasoning", "coding"]
mode_labels = {"text": "💬 Text", "reasoning": "🧠 Reasoning", "coding": "💻 Coding"}

cols = st.columns(len(modes))
for i, m in enumerate(modes):
    if cols[i].button(mode_labels[m], key=f"mode_{m}", use_container_width=True):
        st.session_state.mode = m
        st.session_state.messages[0] = {"role": "system", "content": get_system_prompt(m)}
        st.rerun()

mode = st.session_state.mode

# ── Chat history ──────────────────────────────────────────────────────────────
non_system = [m for m in st.session_state.messages if m["role"] != "system"]

if non_system:
    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        if st.button("✕  Clear", key="clear_chat"):
            st.session_state.messages      = [{"role": "system", "content": get_system_prompt(mode)}]
            st.session_state.pending_image = None
            st.session_state.img_history   = {}
            st.rerun()
    for msg in non_system:
        render_message(msg["role"], msg["content"],
                       image_data=st.session_state.img_history.get(id(msg)))

# ── Spacer for fixed bottom input ─────────────────────────────────────────────
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

# ── Handle send trigger ───────────────────────────────────────────────────────
if st.session_state.get("_trigger_send"):
    st.session_state["_trigger_send"] = False

    # Render last user message
    last_user_msg = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_msg = msg
            break

    if last_user_msg:
        img_data = st.session_state.img_history.get(id(last_user_msg))
        render_message("user", last_user_msg["content"], image_data=img_data)

        has_image = img_data is not None
        model_id = get_model(mode, has_image=has_image)

        try:
            ai_text = stream_response(st.session_state.messages, model_id)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
        except Exception as exc:
            st.error(f"Error: {exc}")

        st.rerun()

# ── Image preview (above input) ───────────────────────────────────────────────
if st.session_state.pending_image:
    p = st.session_state.pending_image
    st.markdown(f"""
    <div class="img-preview-container">
        <div class="img-preview-pill">
            <img src="data:{p["mime"]};base64,{p["data"]}">
            <span>{p["name"]}</span>
        </div>
        <button class="img-remove-btn" onclick="window.parent.postMessage({{type: 'streamlit:removeImage'}}, '*')">✕</button>
    </div>
    """, unsafe_allow_html=True)

    # Hidden button for remove functionality
    if st.button("Remove Image", key="remove_img_hidden", help="Remove attached image"):
        st.session_state.pending_image = None
        st.rerun()

# ── Custom chat input with paperclip ──────────────────────────────────────────
has_image = st.session_state.pending_image is not None

# Hidden file uploader
uploaded = st.file_uploader(
    "📎",
    type=["png", "jpg", "jpeg", "webp", "gif"],
    key=f"img_uploader_{st.session_state.uploader_key}",
    label_visibility="hidden",
)

if uploaded is not None:
    b64 = encode_image(uploaded.getvalue())
    st.session_state.pending_image = {"data": b64, "mime": uploaded.type, "name": uploaded.name}
    st.session_state.uploader_key += 1
    st.rerun()

# Custom input area
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

# Paperclip button (triggers file uploader)
paperclip_class = "paperclip-btn has-image" if has_image else "paperclip-btn"
paperclip_emoji = "📎" if not has_image else "✅"

col_clip, col_input, col_send = st.columns([0.06, 0.84, 0.08])

with col_clip:
    # Use a button that triggers the hidden file uploader via JavaScript
    if st.button(paperclip_emoji, key="paperclip", help="Attach image"):
        # Trigger click on hidden file uploader
        st.markdown(f"""
        <script>
            setTimeout(() => {{
                const uploader = document.querySelector('[data-testid="stFileUploader"] input[type="file"]');
                if (uploader) uploader.click();
            }}, 100);
        </script>
        """, unsafe_allow_html=True)

with col_input:
    user_text = st.text_area(
        "Message",
        value=st.session_state.chat_input,
        key="chat_input",
        placeholder="Ask about this image…" if has_image else "Message Aether…",
        label_visibility="collapsed",
        height=68,
    )

with col_send:
    send_pressed = st.button("➤", key="send_btn", help="Send message")

st.markdown('</div>', unsafe_allow_html=True)

# Handle send
if send_pressed and (st.session_state.chat_input.strip() or st.session_state.pending_image):
    process_message()
    st.rerun()
