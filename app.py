import os
import streamlit as st

import config
from rag_chain import ask_question

st.set_page_config(page_title="GitaVaani", page_icon="🪔", layout="centered")

st.title("🪔 GitaVaani")
st.caption("Scripture-grounded answers from the Bhagavad Gita")

api_key = ""

with st.sidebar:
    st.header("⚙️ Settings")

    manual_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Get a free key at aistudio.google.com — your key, your usage, never stored.",
    )
    if manual_key:
        st.session_state["manual_api_key"] = manual_key
    api_key = st.session_state.get("manual_api_key", "")

    st.divider()

    top_k = st.slider(
        "🔢 Chunks to retrieve",
        min_value=2,
        max_value=8,
        value=config.DEFAULT_TOP_K,
    )
    st.sidebar.caption(
        "How many scripture passages are pulled from the database for each "
        "question. More chunks = more context, but also more text sent to "
        "the AI model."
    )

    show_passages = st.checkbox("📄 Show retrieved passages")
    st.sidebar.caption(
        "When checked, shows the exact raw scripture chunks retrieved for "
        "your last question, before formatting."
    )

    st.divider()

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.sidebar.caption(
        "Clears the conversation shown on screen. Does not change the "
        "underlying scripture database."
    )

index_file = os.path.join(config.VECTOR_DB_DIR, "index.faiss")
if not os.path.isfile(index_file):
    st.error("Vector database not found. Please run: python ingest.py")
    st.stop()

if not api_key:
    st.warning("Please enter your Gemini API key in the sidebar to start chatting.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption("📚 Sources: " + ", ".join(message["sources"]))


user_question = st.chat_input("Ask a spiritual or life question...")

if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("assistant"):
        with st.spinner("Reflecting on the scripture..."):
            try:
                result = ask_question(
                    question=user_question,
                    api_key=api_key,
                    k=top_k,
                )
                answer = result["answer"]
                sources = result["formatted_sources"]
                source_documents = result["source_documents"]

                if not source_documents:
                    answer = (
                        "The provided scripture context does not contain "
                        "enough information to answer this confidently."
                    )

                st.markdown(answer)

                if sources:
                    st.caption("📚 Sources: " + ", ".join(sources))

                if show_passages and source_documents:
                    with st.expander("Retrieved Passages"):
                        for doc in source_documents:
                            st.markdown(f"**{doc.metadata.get('source', 'Bhagavad Gita')}**")
                            st.text(doc.page_content)
                            st.divider()

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as e:
                st.error("Gemini API call failed. Check your API key and internet connection.")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "⚠️ Something went wrong answering that question.",
                        "sources": [],
                    }
                )
