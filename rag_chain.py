from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import config
from prompts import rag_prompt


_embeddings = HuggingFaceEmbeddings(
    model_name=config.EMBEDDING_MODEL_NAME
)


def load_vectorstore() -> FAISS:
    vectorstore = FAISS.load_local(
        config.VECTOR_DB_DIR,
        _embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore


def get_retriever(k: int = 4):
    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever


def format_docs(docs: list) -> str:
    if not docs:
        return ""

    formatted_blocks = []

    for doc in docs:
        reference = build_source_reference(doc.metadata)
        block = f"[{reference}]\n{doc.page_content}"
        formatted_blocks.append(block)

    return "\n\n---\n\n".join(formatted_blocks)


def build_source_reference(metadata: dict) -> str:
    source = (
        "The Bhagavadgītā or The Song Divine "
        "(With Sanskrit Text and English Translation), "
        "Gita Press, Gorakhpur"
    )

    chapter = metadata.get("chapter_number")
    verse = metadata.get("verse_number")
    page = metadata.get("page_number")

    if chapter and verse:
        return f"{source}, Chapter {chapter}, Verse {verse}"

    if chapter:
        return f"{source}, Chapter {chapter}"

    if page is not None:
        return f"{source}, page {page}"

    return source


def build_rag_chain(api_key: str, k: int = 4):
    retriever = get_retriever(k=k)

    llm = ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=api_key,
        temperature=0.3,
    )

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask_question(
    question: str,
    api_key: str,
    k: int = 4,
) -> dict:
    retriever = get_retriever(k=k)
    source_documents = retriever.invoke(question)

    chain = build_rag_chain(api_key, k=k)
    answer = chain.invoke(question)

    formatted_sources = []
    seen = set()

    for doc in source_documents:
        reference = build_source_reference(doc.metadata)

        if reference not in seen:
            formatted_sources.append(reference)
            seen.add(reference)

    return {
        "answer": answer,
        "source_documents": source_documents,
        "formatted_sources": formatted_sources,
    }