import streamlit as st
import os
from dotenv import load_dotenv
from src.rag import (
    load_documents,
    text_splitter,
    loading_vector_database,
    retriever_from_vector_database,
    generate_answer,
)

from langchain_community.vectorstores import FAISS

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nobel Medicine RAG Chatbot",
    page_icon="🏅",
    layout="centered",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global ─────────────────────────────────────────────── */
    .block-container { max-width: 780px; }

    /* ── Header ─────────────────────────────────────────────── */
    .app-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
    }
    .app-header h1 {
        font-size: 2rem;
        background: linear-gradient(135deg, #c9a227, #d4af37, #f5d76e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .app-header p {
        opacity: 0.7;
        font-size: 0.95rem;
    }

    /* ── Divider ────────────────────────────────────────────── */
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #d4af37, transparent);
        border: none;
        margin: 0.5rem 0 1rem;
    }

    /* ── Suggestion chips ───────────────────────────────────── */
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="app-header">
        <h1>🏅 Nobel Medicine RAG Chatbot</h1>
        <p>Ask anything about Nobel Prize–winning discoveries in Physiology or Medicine</p>
    </div>
    <div class="gold-divider"></div>
    """,
    unsafe_allow_html=True,
)


# ── Load / build the FAISS index (cached across reruns) ──────────────────────
@st.cache_resource(show_spinner=False)

def get_vector_db():
    document = load_documents()
    chunk = text_splitter(document, chunk_size=1000, overlap=200)
    with st.spinner("🔬 Loading knowledge base — this may take a minute on first run…"):
        # Lưu ý: Đảm bảo hàm này không cần tham số đầu vào, hoặc đã cấu hình mặc định trong src.rag
        return loading_vector_database(chunk)

db = get_vector_db()
retriever = retriever_from_vector_database(db, k=3, score_threshold=0.2)

# ── Session state: chat history ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render past messages ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🏅"):
        st.markdown(msg["content"])

# ── Suggested questions (only shown when history is empty) ───────────────────
if not st.session_state.messages:
    SUGGESTIONS = [
        "Who won the Nobel Prize in Medicine in 2023?",
        "What did Svante Pääbo discover?",
        "Tell me about the discovery of penicillin.",
        "Which laureates worked on immunology?",
    ]
    cols = st.columns(2)
    for idx, q in enumerate(SUGGESTIONS):
        if cols[idx % 2].button(q, key=f"sug_{idx}", use_container_width=True):
            st.session_state._pending_question = q
            st.rerun()

# ── Resolve a suggestion click into the chat input ───────────────────────────
pending = st.session_state.pop("_pending_question", None)
user_input = st.chat_input("Ask a question about Nobel Prize medicine…")
question = pending or user_input

# ── Handle user question ─────────────────────────────────────────────────────
if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant", avatar="🏅"):
        with st.spinner("Searching the archives…"):
            try:
                answer = generate_answer(retriever, question)
            except Exception as e:
                answer = f"⚠️ Something went wrong: `{e}`"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown(
        "This chatbot uses **Retrieval-Augmented Generation** (RAG) to answer "
        "questions about Nobel Prize–winning medical discoveries.\n\n"
        "Sources include Nobel lectures and press releases."
    )
    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Built with Streamlit · LangChain · Gemini · FAISS")
