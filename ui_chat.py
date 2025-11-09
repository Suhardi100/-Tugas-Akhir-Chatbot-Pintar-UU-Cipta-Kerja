import streamlit as st
import datetime
import pytz
import app  # tetap memanggil semua logika dari app.py

# ================================
# 🌿 KONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Chatbot UU Cipta Kerja 🇮🇩",
    page_icon="🤖",
    layout="wide",
)

# ================================
# 🌿 GAYA CSS (tema hijau profesional + sidebar kuning)
# ================================
st.markdown("""
<style>
/* Background utama */
.stApp {
    background: linear-gradient(135deg, #0f5132 0%, #198754 100%);
    color: white !important;
}

/* Kontainer utama chat */
.chat-container {
    background-color: rgba(255, 255, 255, 0.10);
    border-radius: 16px;
    padding: 25px;
    margin-top: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

/* Header */
h2 {
    color: #d1f7c4 !important;
    text-align: center;
    font-weight: 700;
    font-family: "Segoe UI", sans-serif;
}

p.subtitle {
    text-align: center;
    font-size: 16px;
    color: #e7ffe0;
}

/* Chat bubble styling */
.chat-bubble-user {
    background-color: #e9f7ef;
    color: #0f5132;
    padding: 12px 18px;
    border-radius: 16px;
    margin-bottom: 10px;
    max-width: 80%;
    align-self: flex-end;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.chat-bubble-assistant {
    background-color: #d1e7dd;
    color: #0f5132;
    padding: 12px 18px;
    border-radius: 16px;
    margin-bottom: 10px;
    max-width: 80%;
    align-self: flex-start;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Timestamp */
.timestamp {
    font-size: 11px;
    color: #c9decf;
}

/* Chat input box */
[data-baseweb="input"] {
    background-color: #ffffff !important;
    color: #0f5132 !important;
}

/* Sidebar kuning */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #ffeb3b 0%, #fbc02d 100%);
    color: #333 !important;
    font-family: "Segoe UI", sans-serif;
}

.sidebar-header {
    text-align: center;
    font-weight: bold;
    color: #0f5132;
    font-size: 18px;
    margin-bottom: 10px;
}

.sidebar-item {
    background-color: rgba(255, 255, 255, 0.3);
    padding: 8px 10px;
    border-radius: 8px;
    margin-bottom: 6px;
    color: #0f5132;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ================================
# 🌿 SIDEBAR UNTUK RIWAYAT PROMPT
# ================================
with st.sidebar:
    st.markdown("<div class='sidebar-header'>📜 Riwayat Pertanyaan</div>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    user_prompts = [m["text"] for m in st.session_state.messages if m["role"] == "user"]

    if user_prompts:
        for i, q in enumerate(reversed(user_prompts), 1):
            st.markdown(f"<div class='sidebar-item'>{i}. {q}</div>", unsafe_allow_html=True)
    else:
        st.info("Belum ada pertanyaan yang diajukan.")

# ================================
# 🌿 HEADER UTAMA
# ================================
st.markdown("""
<h2>🤖 Chatbot UU Cipta Kerja (Agentic RAG)</h2>
<p class='subtitle'>Tanyakan apa pun seputar <b>UU No. 11 Tahun 2020</b> tentang Cipta Kerja</p>
""", unsafe_allow_html=True)

# ================================
# 💬 CHAT AREA
# ================================
chat_box = st.container()
with chat_box:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role, text, time = msg["role"], msg["text"], msg["time"]
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>Anda ({time})</b><br>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-assistant'><b>Asisten ({time})</b><br>{text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 💬 INPUT CHAT
# ================================
prompt = st.chat_input("💬 Ketik pertanyaan hukum Anda di sini...")

if prompt:
    # Zona waktu GMT+7
    tz = pytz.timezone("Asia/Jakarta")
    current_time = datetime.datetime.now(tz).strftime("%H:%M:%S")

    st.session_state.messages.append({"role": "user", "text": prompt, "time": current_time})

    with chat_box:
        st.markdown(f"<div class='chat-bubble-user'><b>Anda ({current_time})</b><br>{prompt}</div>", unsafe_allow_html=True)

    # Jalankan Agentic RAG dari app.py
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
        st.session_state.messages.append({
            "role": "assistant",
            "text": response_text,
            "time": current_time
        })

        with chat_box:
            st.markdown(f"<div class='chat-bubble-assistant'><b>Asisten ({current_time})</b><br>{response_text}</div>", unsafe_allow_html=True)
