import os
import re
import base64
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# API Key
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

# Page config
st.set_page_config(
    page_title="Free AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS
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
.title { font-size: 15px; font-weight: 600; color: #D0D4E0; }
.status {
    font-size: 9px; font-weight: 600; color: #38A169;
    background: rgba(56,161,105,0.08); border: 1px solid rgba(56,161,105,0.18);
    border-radius: 20px; padding: 2px 8px;
}

.chat-row { display: flex; width: 100%; margin-bottom: 1.5rem; gap: 10px; align-items: flex-start; }
.user-row { justify-content: flex-end; }

.avatar {
    width: 26px; height: 26px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-size: 11px; font-weight: 600; margin-top: 3px;
}
.avatar-ai { background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.2); color: #818CF8; }

.bubble { max-width: 80%; font-size: 14.5px; line-height: 1.75; word-wrap: break-word; }
.user-bubble { background: #111420; border: 1px solid rgba(255,255,255,0.055); color: #BFC6D6; border-radius: 16px 16px 3px 16px; padding: 0.65rem 1rem; }
.ai-bubble { background: transparent; color: #8A95A3; padding: 0.1rem 0; }
.ai-bubble p { margin: 0 0 0.5rem; color: #8A95A3; }
.ai-bubble strong { color: #C0C8D8; font-weight: 600; }
.ai-bubble em { color: #6E7D8C; }
.ai-bubble ul, .ai-bubble ol { margin: 0.35rem 0 0.35rem 1.15rem; padding: 0; }
.ai-bubble li { margin-bottom: 4px; color: #8A95A3; }
.ai-bubble code { background: #0D0F18; border: 1px solid rgba(255,255,255,0.07); padding: 2px 6px; border-radius: 5px; font-size: 12.5px; color: #7EB8D4; }
.ai-bubble pre { background: #0A0C14; border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.9rem 1.1rem; overflow-x: auto; margin: 0.75rem 0; }
.ai-bubble pre code { background: none; border: none; padding: 0; color: #9BAFC0; }

.chat-img { max-width: 280px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); margin-top: 6px; }

.input-container {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top, #07080D 80%, transparent);
    padding: 1.5rem 0 1rem; z-index: 99;
}
.input-box {
    max-width: 720px; margin: 0 auto;
    display: flex; align-items: flex-end; gap: 8px;
}

[data-testid="stChatInput"] { display: none !important; }
[data-testid="stFileUploader"] { display: none !important; }

div[data-testid="stButton"] > button {
    background: transparent !important; border: 1px solid rgba(255,255,255,0.05) !important;
    color: #4A5568 !important; font-size: 11px !important; border-radius: 8px !important;
    padding: 3px 12px !important;
}
div[data-testid="stButton"] > button:hover { border-color: rgba(255,255,255,0.09) !important; color: #A0AEC0 !important; }
</style>
""", unsafe_allow_html=True)

# Check API key
if not API_KEY:
    st.error("API key not found. Please set OPENROUTER_API_KEY in secrets.")
    st.stop()

# System prompt
SYSTEM_PROMPT = """You are a helpful AI assistant. Be concise and clear. Use markdown formatting."""

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
<div class="header">
    <div class="brand">
        <div class="logo">🤖</div>
        <div class="title">Free AI</div>
    </div>
    <div class="status">Online</div>
</div>
""", unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        text = msg["content"]
        safe_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', safe_text)
        safe_text = safe_text.replace("\n", "<br>")
        st.markdown(f'<div class="chat-row user-row"><div class="bubble user-bubble">{safe_text}</div></div>', unsafe_allow_html=True)
    else:
        col1, col2 = st.columns([0.04, 0.96])
        with col1:
            st.markdown('<div class="avatar avatar-ai"></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="bubble ai-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# Spacer
st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.06, 0.86, 0.08])

with col1:
    uploaded = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], key="img_upload", label_visibility="collapsed")

with col2:
    user_input = st.text_input("Type a message...", key="user_input", label_visibility="collapsed")

with col3:
    send = st.button("Send", key="send_btn")

st.markdown('</div>', unsafe_allow_html=True)

# Process input
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})

    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY
        )

        messages_with_system = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=messages_with_system
        )

        ai_response = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        st.error(f"Error: {str(e)}")

    st.rerun()
