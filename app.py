import os
import streamlit as st
from typing import TypedDict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.tools import Tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langsmith import traceable

# ================================
# 🔧 Konfigurasi Awal
# ================================
os.environ["TAVILY_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__YourLangSmithKeyHere"
os.environ["LANGCHAIN_PROJECT"] = "UU-CiptaKerja-AgenticRAG"

# ================================
# 🔮 Setup Google Gemini
# ================================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-live",
    temperature=0.1,
    google_api_key="AIzaSyA-d2ZH44cAZrqxN7MwNirQlLEE5SaQYtc"
)

# ================================
# 🧰 Tools Bahasa Indonesia
# ================================
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="id"))
arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())
tavily_tool_instance = TavilySearchResults(k=3)

tools = {
    "Wikipedia": Tool(
        name="Wikipedia",
        func=wikipedia_tool.run,
        description="Gunakan untuk konsep hukum umum atau istilah legal dalam Bahasa Indonesia"
    ),
    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description="Gunakan untuk referensi akademik tentang hukum, teori, dan penelitian"
    ),
    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description="Gunakan untuk berita hukum terbaru, peraturan Indonesia, dan putusan pengadilan"
    )
}

# ================================
# 📚 Load Dokumen UU Cipta Kerja
# ================================
loader = PyPDFLoader("uu_ciptakerja.pdf")
documents = loader.load()

# ================================
# 🧩 Define Agent State
# ================================
class AgentState(TypedDict):
    question: str
    docs: Optional[List[str]]
    external_docs: Optional[List[str]]
    answer: Optional[str]
    relevant: Optional[bool]
    answered: Optional[bool]
    selected_tools: Optional[List[str]]
    reasoning: Optional[str]

# ================================
# 🧠 Node: Tool Selection
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:
    q = state["question"]
    prompt = f"""
    Kamu adalah asisten hukum cerdas. Tentukan tools terbaik untuk menjawab pertanyaan berikut:

    Pertanyaan: {q}

    Tools tersedia:
    1. Wikipedia - konsep hukum umum (Bahasa Indonesia)
    2. arXiv - penelitian hukum akademik
    3. TavilySearch - berita dan hukum terbaru di Indonesia
    4. PDF_Documents - dokumen UU Cipta Kerja

    Analisis:
    - Apakah tentang hukum terkini Indonesia? → TavilySearch
    - Apakah teori hukum akademik? → arXiv
    - Apakah konsep hukum dasar? → Wikipedia
    - Apakah isi UU Cipta Kerja? → PDF_Documents

    Format:
    TOOLS: tool1,tool2
    REASONING: alasan
    """
    result = llm.invoke(prompt)
    lines = result.content.strip().split("\n")
    tools_selected, reasoning = [], ""
    for line in lines:
        if line.startswith("TOOLS:"):
            tools_selected = [t.strip() for t in line.replace("TOOLS:", "").split(",")]
        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()
    return {**state, "selected_tools": tools_selected, "reasoning": reasoning}

# ================================
# 🔍 Node: Multi Source Retrieval
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:
    q = state["question"]
    selected = state.get("selected_tools", [])
    internal_docs = [f"Isi UU Cipta Kerja terkait: {q}"]
    external_docs = []

    for tool_name in selected:
        if tool_name in tools:
            try:
                external_docs.append(tools[tool_name].run(q))
            except Exception as e:
                external_docs.append(f"{tool_name} gagal: {str(e)}")

    return {**state, "docs": internal_docs, "external_docs": external_docs}

# ================================
# 🧮 Node: Grade Relevance
# ================================
@traceable
def enhanced_grade_node(state: AgentState) -> AgentState:
    q = state["question"]
    all_docs = state.get("docs", []) + state.get("external_docs", [])
    prompt = f"""
    Evaluasi relevansi dokumen berikut untuk pertanyaan hukum ini:

    Pertanyaan: {q}
    Dokumen: {all_docs}

    Apakah cukup relevan untuk menjawab pertanyaan? (ya/tidak)
    """
    res = llm.invoke(prompt)
    return {**state, "relevant": "ya" in res.content.lower()}

# ================================
# 🧩 Node: Generate Final Answer
# ================================
@traceable
def enhanced_generation_node(state: AgentState) -> AgentState:
    q = state["question"]
    context = "\n".join(state.get("docs", []) + state.get("external_docs", []))
    prompt = f"""
    Kamu adalah asisten hukum ahli Indonesia.
    Gabungkan informasi dari berbagai sumber berikut untuk menjawab pertanyaan secara komprehensif.

    Pertanyaan: {q}
    Konteks: {context}

    Jawab dengan bahasa Indonesia formal, dan sebutkan sumber (UU, Wikipedia, Tavily, dll).
    """
    res = llm.invoke(prompt)
    return {**state, "answer": res.content.strip()}

# ================================
# 🔁 Node: Answer Check
# ================================
@traceable
def answer_check_node(state: AgentState) -> AgentState:
    q = state["question"]
    ans = state.get("answer", "")
    prompt = f"Apakah jawaban ini sudah menjawab pertanyaan?\nPertanyaan: {q}\nJawaban: {ans}\nBalas hanya 'ya' atau 'tidak'."
    res = llm.invoke(prompt)
    return {**state, "answered": "ya" in res.content.lower()}

# ================================
# 🔧 Workflow Graph (LangGraph)
# ================================
workflow = StateGraph(AgentState)
workflow.add_node("ToolSelection", tool_selection_node)
workflow.add_node("Retrieve", multi_source_retrieve_node)
workflow.add_node("Grade", enhanced_grade_node)
workflow.add_node("Generate", enhanced_generation_node)
workflow.add_node("Evaluate", answer_check_node)

workflow.set_entry_point("ToolSelection")
workflow.add_edge("ToolSelection", "Retrieve")
workflow.add_edge("Retrieve", "Grade")
workflow.add_edge("Grade", "Generate")
workflow.add_edge("Generate", "Evaluate")
workflow.add_conditional_edges(
    "Evaluate",
    lambda s: "Yes" if s["answered"] else "No",
    {"Yes": END, "No": "Retrieve"}
)
runnable_graph = workflow.compile()

# ================================
# 💬 Streamlit Frontend
# ================================
st.set_page_config(page_title="Chatbot UU Cipta Kerja 🇮🇩", layout="wide")

st.title("📘 Chatbot UU Cipta Kerja (Agentic RAG)")
st.write("Tanyakan apa pun seputar UU No. 11 Tahun 2020 tentang Cipta Kerja")

query = st.text_area("Masukkan pertanyaan Anda:", placeholder="Contoh: Apa isi Pasal tentang ketenagakerjaan?")
if st.button("Jalankan Analisis"):
    with st.spinner("Sedang menganalisis..."):
        state = {"question": query}
        result = runnable_graph.invoke(state)
        st.success("✅ Jawaban Ditemukan")
        st.markdown("### **Jawaban:**")
        st.write(result["answer"])
        st.markdown("### **Alasan Pemilihan Tools:**")
        st.write(result.get("reasoning", ""))
