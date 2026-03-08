# RBI KYC Compliance Assistant 🏦

An AI-powered RAG (Retrieval Augmented Generation) application that provides precise, document-grounded answers to KYC compliance questions based on official RBI Master Directions.

---

## The Problem

When banking staff or clients search for KYC compliance information online, they get generic answers that may be outdated, inaccurate, or not specific to RBI regulations. In a regulated banking environment, generic answers are not good enough — compliance requires precision.

## The Solution

This assistant ingests the official **RBI KYC Master Directions PDF** and answers questions directly from that document. Instead of searching the internet for generic answers, it retrieves the exact relevant sections from the official RBI source and generates precise, accurate responses grounded in real regulatory content.

---

## Demo

**Question:** What are the KYC requirements for opening a bank account?

**Answer:**
```
KYC requirements for opening a bank account include:
- Proof of Identity (Mandatory)
- Proof of Address (Mandatory)
- Proof of possession of Aadhaar number or any Officially Valid Document (OVD)
- KYC Identifier with explicit consent to download records from CKYCR
- Permanent Account Number (PAN) or Form No. 60
```

**Question:** What are the rules for video KYC verification?

**Answer:**
```
The rules for video KYC verification (V-CIP) are:
- Customer consent must be recorded in an auditable and alteration-proof manner
- V-CIP infrastructure must prevent connections from IP addresses outside India
- Video recordings must contain live GPS coordinates and date-time stamp
- It must be a seamless, secure, live, informed-consent based audio-visual interaction
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | RAG pipeline orchestration |
| Google Gemini AI | Language model for answer generation |
| ChromaDB | Vector database for semantic search |
| FastAPI | REST API framework |
| Uvicorn | ASGI web server |
| PyPDF | PDF document loading |
| Pydantic | Request validation and data modeling |

---

## Architecture

```
RBI KYC PDF Document
        ↓
[1. LOAD]    PyPDFLoader reads and extracts text
        ↓
[2. CHUNK]   Split into 500 character chunks with 50 char overlap
        ↓
[3. EMBED]   Convert chunks to vectors using Gemini Embeddings
        ↓
[4. STORE]   Save vectors in ChromaDB (persisted to disk)

─── Setup happens once ───────────────────────────────────

User Question via API
        ↓
[5. SEARCH]  Semantic similarity search finds top 3 relevant chunks
        ↓
[6. GENERATE] Gemini AI generates answer grounded in retrieved chunks
        ↓
Precise, document-grounded answer returned
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check if API is running |
| POST | `/setup` | Load PDF, create embeddings, save to ChromaDB |
| POST | `/ask` | Ask a compliance question |

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What documents are required for video KYC?"}'
```

### Example Response

```json
{
    "question": "What documents are required for video KYC?",
    "answer": "For Video KYC (V-CIP), the customer must present their original Officially Valid Document (OVD) during the live video interaction..."
}
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- Google Gemini API key (free at aistudio.google.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/nandu8/rag-banking-compliance-assistant.git
cd rag-banking-compliance-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install langchain langchain-community langchain-google-genai \
            google-generativeai chromadb pypdf fastapi uvicorn \
            python-dotenv langchain-text-splitters langchain-classic
```

### Configuration

Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Add Your Document

Place the RBI KYC Master Directions PDF in the `data/` folder:
```
data/rbi_kyc.pdf
```

Download from: [RBI Official Website](https://www.rbi.org.in)

### Run The Application

```bash
# Start the server
uvicorn main:app --reload

# First time only - setup the vector database
curl -X POST "http://127.0.0.1:8000/setup"

# Ask questions
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the KYC requirements?"}'
```

Visit `http://127.0.0.1:8000/docs` for the interactive API documentation.

---

## Key Design Decisions

**Why RAG over a standard LLM?**
Standard LLMs give generic answers based on internet training data. RAG grounds every answer in the actual RBI document — critical for compliance accuracy in a regulated banking environment.

**Why ChromaDB?**
Lightweight, runs locally, no infrastructure overhead. In a production banking environment this would be replaced with a scalable vector database like Pinecone or pgvector with proper access controls.

**Why low temperature (0.3)?**
Banking compliance requires factual precision, not creative responses. Low temperature keeps Gemini's answers accurate and consistent.

**Honest AI — no hallucination:**
When the answer isn't in the document, the system says so rather than making up an answer. This is critical in a compliance context.

---

## Future Improvements

- Integrate into existing banking chatbot systems via webhook
- Add support for multiple RBI documents (FEMA, PMLA guidelines)
- Implement role-based access control for different user types
- Add audit logging for compliance tracking
- Build a frontend UI for non-technical banking staff
- Deploy on Kubernetes/OpenShift for production banking environment

---

## Banking Context

This project was built with the regulated banking environment in mind:
- **Data privacy** — API keys managed via environment variables, never hardcoded
- **Input validation** — Pydantic models validate all incoming requests
- **Honest responses** — System acknowledges when information is not available rather than hallucinating
- **Audit ready** — Clean, documented codebase suitable for compliance review

---

## Author

Built as part of an AI engineering portfolio project demonstrating RAG implementation in a regulated banking context.
