import os
import time
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from providers import get_llm, get_embeddings

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini")

# Created once at startup; per-request override is supported via ask_question(provider=...)
llm = get_llm(LLM_PROVIDER)

prompt = ChatPromptTemplate.from_template("""
You are a banking compliance assistant.
Use the following context to answer the question accurately.
If you don't know the answer, say you don't know.
Keep answers concise and factual.

Context: {context}
Question: {input}
""")


def _get_embeddings():
    return get_embeddings(EMBEDDING_PROVIDER)


def load_and_chunk_document(pdf_path):
    print("Loading PDF...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print(f"PDF loaded. Total pages: {len(documents)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    return chunks


def create_vector_store(chunks):
    print("Creating embeddings and storing in ChromaDB...")

    embeddings = _get_embeddings()

    batch_size = 30
    vectorstore = None

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1}...")
        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory="./chroma_db"
            )
        else:
            vectorstore.add_documents(batch)
        time.sleep(30)

    print("Vector store created and saved successfully!")
    return vectorstore


def load_vector_store():
    print("Loading existing vector store...")

    embeddings = _get_embeddings()

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    print("Vector store loaded successfully!")
    return vectorstore


def ask_question(vectorstore, question, provider: str = None):
    try:
        logging.info(f"Question received: {question}")

        active_llm = get_llm(provider) if provider else llm

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        document_chain = create_stuff_documents_chain(active_llm, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({"input": question})

        logging.info("Answer generated successfully")
        return response["answer"]

    except Exception as e:
        logging.error(f"Error generating answer: {e}")
        raise
