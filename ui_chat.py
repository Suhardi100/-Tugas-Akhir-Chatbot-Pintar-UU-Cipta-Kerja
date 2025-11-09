import streamlit as st
import datetime
import pytz
import app  # memanggil semua logika dari app.py

# ================================
# 🌿 KONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Chatbot UU Cipta Kerja 🇮🇩",
    page_icon="🤖",
    layout="wide",
)

# ================================
# 🌿 INISIALISASI SESSION STATE
# ================================
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_name: [messages]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Percakapan Baru"
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.chats[st.session_state.current_chat] = []

# ================================
# 🌿 CSS
# ================================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f5132 0%, #198754 100%); color: white; }
.chat-container {
    background-color: rgba(255, 255, 255, 0.10);
    border-radius: 16px; padding: 25px; margin-top: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
h2 { color: #d1f7c4 !important; text-align: center; font-weight: 700; font-family: "Segoe UI", sans-serif; }
p.subtitle { text-align: center; font-size: 16px; color: #e7ffe0; }
.chat-bubble-user {
    background-color: #e9f7ef; color: #0f5132; padding: 12px 18px; border-radius: 16px;
    margin-bottom: 10px; max-width: 80%; align-self: flex-end;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.chat-bubble-assistant {
    background-color: #d1e7dd; color: #0f5132; padding: 12px 18px; border-radius: 16px;
    margin-bottom: 10px; max-width: 80%; align-self: flex-start;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.timestamp { font-size: 11px; color: #c9decf; }
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #ffeb3b 0%, #fbc02d 100%);
    color: #333 !important; font-family: "Segoe UI", sans-serif;
}
.sidebar-header { text-align: center; font-weight: bold; color: #0f5132; font-size: 18px; margin-bottom: 10px; }
.sidebar-item {
    background-color: rgba(255, 255, 255, 0.3); padding: 8px 10px;
    border-radius: 8px; margin-bottom: 6px; color: #0f5132; font-size: 14px; cursor: pointer;
}
.sidebar-item:hover { background-color: rgba(255, 255, 255, 0.6); }
.new-chat-btn {
    background-color: #0f5132; color: white; border: none; border-radius: 8px;
    padding: 8px 10px; cursor: pointer; font-weight: bold; margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================================
# 🌿 SIDEBAR
# ================================
with st.sidebar:
    st.markdown("<div class='sidebar-header'>💬 Riwayat Percakapan</div>", unsafe_allow_html=True)

    if st.button("➕ Chat Baru", use_container_width=True):
        new_name = f"Percakapan {len(st.session_state.chats) + 1}"
        st.session_state.current_chat = new_name
        st.session_state.chats[new_name] = []
        st.rerun()

    for name in st.session_state.chats.keys():
        if st.button(name, use_container_width=True):
            st.session_state.current_chat = name
            st.rerun()

# ================================
# 🌿 HEADER
# ================================
st.markdown("""
<h2>🤖 Chatbot UU Cipta Kerja (Agentic RAG)</h2>
<p class='subtitle'>Tanyakan apa pun seputar <b>UU No. 11 Tahun 2020</b> tentang Cipta Kerja</p>
""", unsafe_allow_html=True)

# ================================
# 🌿 CHAT AREA
# ================================
chat_box = st.container()
messages = st.session_state.chats[st.session_state.current_chat]

with chat_box:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in messages:
        role, text, time = msg["role"], msg["text"], msg["time"]
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>Anda ({time})</b><br>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-assistant'><b>Asisten ({time})</b><br>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 💬 INPUT CHAT
# ================================
prompt = st.chat_input("Ketik pertanyaan hukum Anda di sini...")

if prompt:
    tz = pytz.timezone("Asia/Jakarta")
    current_time = datetime.datetime.now(tz).strftime("%H:%M:%S")

    # Simpan prompt user
    messages.append({"role": "user", "text": prompt, "time": current_time})

    # Jalankan model dari app.py
    with st.spinner("🔍 Sedang menganalisis dengan Agentic RAG..."):
        try:
            state = {"question": prompt}
            result = app.runnable_graph.invoke(state)
            answer = result.get("answer", "Tidak ada jawaban ditemukan.")
            reasoning = result.get("reasoning", "")
            response_text = f"{answer}\n\n🧠 <b>Analisis Tools:</b> {reasoning}"
        except Exception as e:
            response_text = f"⚠️ Terjadi kesalahan: {e}"

    current_time = datetime.datetime.now(tz).strftime("%H:%M:%S")
    messages.append({"role": "assistant", "text": response_text, "time": current_time})

    # Simpan ke dalam sesi
    st.session_state.chats[st.session_state.current_chat] = messages

    st.rerun()
