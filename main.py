import os
from fastapi import FastAPI
from pydantic import BaseModel
from rag_pipeline import load_and_chunk_document, create_vector_store, load_vector_store, ask_question

app = FastAPI()

class Question(BaseModel):
    query: str

@app.post("/setup")
async def setup():
    pdf_path = "./data/rbi_kyc_directions.pdf"
    chunks = load_and_chunk_document(pdf_path)
    create_vector_store(chunks)
    return {"message": "Vector store created successfully!"}

@app.post("/ask")
async def ask(question: Question):
    vectorstore = load_vector_store()
    answer = ask_question(vectorstore, question.query)
    return {
        "question": question.query,
        "answer": answer
    }

@app.get("/health")
async def health():
    return {"status": "Banking RAG API is running!"}


