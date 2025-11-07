import streamlit as st
import datetime
import app  # ⬅️ memanggil semua definisi dari app.py tanpa import fungsi tertentu

# ================================
# 💬 UI Chatbot Style
# ================================
st.set_page_config(page_title="Chatbot UU Cipta Kerja 🇮🇩", layout="wide")

st.markdown("""
<h2 style='text-align: center;'>🤖 Chatbot UU Cipta Kerja (Agentic RAG)</h2>
<p style='text-align: center;'>Tanyakan apa pun seputar UU No. 11 Tahun 2020 tentang Cipta Kerja</p>
<hr>
""", unsafe_allow_html=True)

# Simpan riwayat chat di session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    role, text, time = msg["role"], msg["text"], msg["time"]
    with st.chat_message(role):
        st.markdown(f"**{role.upper()} ({time})**")
        st.write(text)

# Input chat
prompt = st.chat_input("Ketik pertanyaan hukum Anda di sini...")

if prompt:
    # Tambahkan pesan user
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "text": prompt, "time": current_time})

    with st.chat_message("user"):
        st.markdown(f"**USER ({current_time})**")
        st.write(prompt)

    # Jalankan Agentic RAG dari app.py
    with st.chat_message("assistant"):
        with st.spinner("Sedang menganalisis dengan Agentic RAG..."):
            try:
                state = {"question": prompt}
                result = app.runnable_graph.invoke(state)
                answer = result.get("answer", "Tidak ada jawaban ditemukan.")
                reasoning = result.get("reasoning", "")
                response_text = f"{answer}\n\n🧠 **Analisis Tools:** {reasoning}"
            except Exception as e:
                response_text = f"⚠️ Terjadi kesalahan: {e}"

            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "assistant",
                "text": response_text,
                "time": current_time
            })
            st.markdown(f"**ASSISTANT ({current_time})**")
            st.write(response_text)
