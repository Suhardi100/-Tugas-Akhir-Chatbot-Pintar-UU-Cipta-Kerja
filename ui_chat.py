import streamlit as st
import datetime
import pytz
import app  # tetap memanggil logika utama dari app.py

# ================================
# 🌿 KONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Chatbot UU Cipta Kerja 🇮🇩",
    page_icon="🤖",
    layout="wide",
)

# ================================
# 🌿 CSS PROFESIONAL + ANIMASI HALUS
# ================================
st.markdown("""
<style>
/* ================================
   🌿 UMUM
================================ */
.stApp {
    background: linear-gradient(135deg, #0b3d2e 0%, #198754 100%);
    color: #f8f9fa !important;
    font-family: "Segoe UI", sans-serif;
    animation: fadeIn 0.8s ease-in-out;
}
@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity: 1;}
}

/* ================================
   🌿 HEADER
================================ */
h2 {
    text-align: center;
    font-weight: 700;
    color: #d1f7c4 !important;
    margin-bottom: 5px;
    animation: fadeIn 1.2s ease-in-out;
}
p.subtitle {
    text-align: center;
    font-size: 15px;
    color: #e8ffe0;
    margin-bottom: 25px;
}

/* ================================
   🌿 CHAT AREA
================================ */
.chat-container {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    animation: fadeIn 0.8s ease-in-out;
}

/* Bubble animasi halus */
@keyframes bubbleFade {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: translateY(0);}
}
.chat-bubble-user, .chat-bubble-assistant {
  animation: bubbleFade 0.4s ease-in-out;
}

/* Bubble pengguna */
.chat-bubble-user {
    background: #d1e7dd;
    color: #0f5132;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 12px;
    max-width: 80%;
    margin-left: auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

/* Bubble asisten */
.chat-bubble-assistant {
    background: #f8f9fa;
    color: #0f5132;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 12px;
    max-width: 80%;
    margin-right: auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}

/* ================================
   🌿 SIDEBAR
================================ */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #fff176 0%, #fbc02d 100%);
    color: #1b4332;
}
.sidebar-header {
    text-align: center;
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 15px;
}

/* Item sidebar */
.sidebar-item {
    background-color: rgba(255,255,255,0.5);
    padding: 8px 10px;
    border-radius: 10px;
    margin-bottom: 6px;
    color: #0f5132;
    font-size: 14px;
    transition: all 0.3s ease;
    animation: bubbleFade 0.4s ease-in-out;
}
.sidebar-item:hover {
    background-color: rgba(255,255,255,0.8);
    cursor: pointer;
    transform: scale(1.02);
}

/* Tombol Chat Baru */
.chat-new-btn button {
    background-color: #c0392b !important;
    color: black !important;
    font-weight: bold;
    border-radius: 10px;
    transition: 0.3s;
}
.chat-new-btn button:hover {
    background-color: #e74c3c !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ================================
# 🌿 INISIALISASI SESSION STATE
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "all_prompts" not in st.session_state:
    st.session_state.all_prompts = []

# ================================
# 🌿 SIDEBAR — RIWAYAT CHAT
# ================================
with st.sidebar:
    st.markdown("<div class='sidebar-header'>📜 Riwayat Pertanyaan</div>", unsafe_allow_html=True)

    # Tombol Chat Baru
    with st.container():
        st.markdown('<div class="chat-new-btn">', unsafe_allow_html=True)
        if st.button("🆕 Mulai Chat Baru", use_container_width=True):
            if st.session_state.messages:
                st.session_state.chat_history.append(st.session_state.messages.copy())
            st.session_state.messages = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Klik riwayat untuk menampilkan ulang
    if st.session_state.all_prompts:
        for i, q in enumerate(reversed(st.session_state.all_prompts), 1):
            short_q = (q[:60] + "...") if len(q) > 60 else q
            if st.button(f"🗂️ {short_q}", key=f"prompt_{i}", use_container_width=True):
                # Cari di chat_history yang punya prompt ini
                for chat in st.session_state.chat_history:
                    if chat and chat[0]["text"] == q:
                        st.session_state.messages = chat.copy()
                        st.rerun()
    else:
        st.info("Belum ada pertanyaan yang diajukan.")

# ================================
# 🌿 HEADER
# ================================
st.markdown("""
<h2>🤖 Chatbot UU Cipta Kerja (Agentic RAG)</h2>
<p class='subtitle'>Tanyakan apa pun seputar <b>UU No. 11 Tahun 2020</b> tentang Cipta Kerja</p>
""", unsafe_allow_html=True)

# ================================
# 💬 AREA CHAT
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
    tz = pytz.timezone("Asia/Jakarta")
    current_time = datetime.datetime.now(tz).strftime("%H:%M:%S")

    # Tampilkan langsung prompt user
    st.session_state.messages.append({"role": "user", "text": prompt, "time": current_time})
    st.session_state.all_prompts.append(prompt)
    st.rerun()

    # Jalankan Agentic RAG
    try:
        with st.spinner("🔍 Sedang menganalisis dengan Agentic RAG..."):
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

    # Simpan ke history untuk bisa diakses ulang
    st.session_state.chat_history.append(st.session_state.messages.copy())
    st.rerun()
