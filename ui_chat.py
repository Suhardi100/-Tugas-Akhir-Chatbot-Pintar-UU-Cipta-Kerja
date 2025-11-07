import streamlit as st
from app import agent_main  # import fungsi utama dari app.py (misalnya agent_main(question))

# ----------------------------
# SETTING TAMPILAN
# ----------------------------
st.set_page_config(
    page_title="Indonesian Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# CSS agar mirip ChatGPT
st.markdown("""
    <style>
    .chat-message {
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    .user-message {
        background-color: #DCF8C6;
        align-self: flex-end;
        text-align: right;
    }
    .bot-message {
        background-color: #F1F0F0;
        align-self: flex-start;
        text-align: left;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 80px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# STATE UNTUK CHAT HISTORY
# ----------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("⚖️ Legal Research Assistant (Indonesia)")
st.markdown("Tanyakan apapun tentang hukum Indonesia, undang-undang, atau putusan pengadilan.")

# ----------------------------
# TAMPILKAN CHAT
# ----------------------------
chat_container = st.container()
with chat_container:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message">{msg["content"]}</div>', unsafe_allow_html=True)

# ----------------------------
# INPUT BAWAH
# ----------------------------
user_input = st.chat_input("Ketik pertanyaan hukum Anda...")

if user_input:
    # Tambahkan pertanyaan ke history
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Jalankan logika utama dari app.py
    try:
        with st.spinner("Sedang menganalisis..."):
            bot_response = agent_main(user_input)  # Fungsi dari app.py
    except Exception as e:
        bot_response = f"⚠️ Terjadi kesalahan: {str(e)}"

    # Tambahkan jawaban ke history
    st.session_state["messages"].append({"role": "assistant", "content": bot_response})

    # Refresh tampilan
    st.rerun()
