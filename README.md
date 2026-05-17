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
| Google Gemini AI | LLM and embeddings (default provider) |
| Anthropic Claude | Alternative LLM provider |
| OpenAI GPT-4o | Alternative LLM and embedding provider |
| ChromaDB | Vector database for semantic search |
| FastAPI | REST API framework |
| Uvicorn | ASGI web server |
| PyPDF | PDF document loading |
| Pydantic | Request validation and data modeling |
| Docker | Containerisation and deployment |

---

## Architecture

```
RBI KYC PDF Document
        ↓
[1. LOAD]    PyPDFLoader reads and extracts text
        ↓
[2. CHUNK]   Split into 500 character chunks with 50 char overlap
        ↓
[3. EMBED]   Convert chunks to vectors using configured embedding provider
        ↓
[4. STORE]   Save vectors in ChromaDB (persisted to disk)

─── Setup happens once ───────────────────────────────────

User Question via API
        ↓
[5. SEARCH]  Semantic similarity search finds top 3 relevant chunks
        ↓
[6. GENERATE] Configured LLM generates answer grounded in retrieved chunks
        ↓
Precise, document-grounded answer returned
```

### Multi-Provider Design

```
providers.py          ← Factory: get_llm(provider) / get_embeddings(provider)
rag_pipeline.py       ← RAG logic, reads LLM_PROVIDER / EMBEDDING_PROVIDER env vars
main.py               ← FastAPI endpoints, optional per-request provider override
```

Supported providers:

| Provider | LLM | Embeddings |
|---|---|---|
| `gemini` | Gemini 2.5 Flash | Gemini Embedding 001 |
| `anthropic` | Claude Sonnet 4.6 | ❌ (use gemini or openai) |
| `openai` | GPT-4o | text-embedding-3-small |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check if API is running |
| POST | `/setup` | Load PDF, create embeddings, save to ChromaDB |
| POST | `/ask` | Ask a compliance question |

### Example Requests

```bash
# Default — uses LLM_PROVIDER from .env
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What documents are required for video KYC?"}'

# Per-request provider override
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What documents are required for video KYC?", "provider": "anthropic"}'
```

### Example Response

```json
{
    "question": "What documents are required for video KYC?",
    "answer": "For Video KYC (V-CIP), the customer must present their original Officially Valid Document (OVD) during the live video interaction...",
    "provider": "gemini"
}
```

---

## Getting Started

### Option 1 — Run With Docker (Recommended)

**Pull and run from Docker Hub:**
```bash
docker pull nanduks8/rag-banking-app:v1

docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_gemini_api_key_here \
  -v /your/local/path/chroma_db:/app/chroma_db \
  nanduks8/rag-banking-app:v1
```

**Windows PowerShell:**
```bash
docker run -p 8000:8000 `
  -e GOOGLE_API_KEY=your_gemini_api_key_here `
  -v "${PWD}/chroma_db:/app/chroma_db" `
  nanduks8/rag-banking-app:v1
```

Then visit `http://localhost:8000/docs` for the interactive API documentation.

**First time only** — run the `/setup` endpoint to build the vector database:
```bash
curl -X POST "http://127.0.0.1:8000/setup"
```

**Why the volume mount `-v`?**
ChromaDB data is persisted to your local machine via volume mounting. This means you only need to run `/setup` once — even after container restarts, the vector database is loaded from your local folder automatically.

---

### Option 2 — Run Locally

#### Prerequisites
- Python 3.9+
- API key for at least one provider (Gemini is the default)

#### Installation

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
            langchain-anthropic langchain-openai \
            google-generativeai chromadb pypdf fastapi uvicorn \
            python-dotenv langchain-text-splitters langchain-classic
```

#### Configuration

Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here   # optional
OPENAI_API_KEY=your_openai_key_here         # optional

# LLM used for answer generation: gemini | anthropic | openai
LLM_PROVIDER=gemini

# Embedding model (must stay consistent after /setup): gemini | openai
EMBEDDING_PROVIDER=gemini
```

#### Add Your Document

Place the RBI KYC Master Directions PDF in the `data/` folder:
```
data/rbi_kyc_directions.pdf
```

Download from: [RBI Official Website](https://www.rbi.org.in)

#### Run The Application

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

### Option 3 — Build Docker Image Locally

```bash
# Clone the repository
git clone https://github.com/nandu8/rag-banking-compliance-assistant.git
cd rag-banking-compliance-assistant

# Build the image
docker build -t rag-banking-app .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_gemini_api_key_here \
  -v "${PWD}/chroma_db:/app/chroma_db" \
  rag-banking-app
```

---

## Project Structure

```
rag-banking-compliance-assistant/
│
├── main.py              ← FastAPI application and API endpoints
├── rag_pipeline.py      ← RAG pipeline logic (load, chunk, embed, retrieve)
├── providers.py         ← LLM and embedding provider factory (Gemini / Claude / OpenAI)
├── Dockerfile           ← Container configuration
├── .dockerignore        ← Files excluded from Docker image
├── requirements.txt     ← Python dependencies
├── .env                 ← API keys and provider config (never committed to Git)
├── .gitignore           ← Files excluded from Git
└── data/
    └── rbi_kyc_directions.pdf  ← RBI KYC Master Directions document
```

---

## Key Design Decisions

**Why RAG over a standard LLM?**
Standard LLMs give generic answers based on internet training data. RAG grounds every answer in the actual RBI document — critical for compliance accuracy in a regulated banking environment.

**Why a provider abstraction?**
`providers.py` centralises all provider-specific initialisation. Switching models or adding a new provider requires changes in exactly one place. The LangChain interface (`BaseChatModel`, `Embeddings`) means the rest of the pipeline is provider-agnostic.

**Why ChromaDB?**
Lightweight, runs locally, no infrastructure overhead. In a production banking environment this would be replaced with a scalable vector database like Pinecone or pgvector with proper access controls and high availability.

**Why low temperature (0.3)?**
Banking compliance requires factual precision, not creative responses. Low temperature keeps answers accurate and consistent regardless of provider.

**Honest AI — no hallucination:**
When the answer isn't in the document, the system says so rather than making up an answer. This is critical in a compliance context.

**Why Docker?**
Containerisation ensures the application runs identically across development, testing, and production environments. API keys are passed as environment variables — never baked into the image. Volume mounting ensures ChromaDB data persists across container restarts without requiring expensive re-embedding.

**Why volume mounting for ChromaDB?**
Embedding 566 document chunks requires multiple API calls and takes several minutes. Persisting the vector database via volume mounting means this expensive operation only happens once — subsequent container restarts load existing embeddings instantly.

---

## Future Improvements

- Integrate into existing banking chatbot systems via webhook
- Add support for multiple RBI documents (FEMA, PMLA guidelines)
- Implement role-based access control for different user types
- Add audit logging for compliance tracking
- Build a React/TypeScript frontend UI for non-technical banking staff
- Deploy on Kubernetes/OpenShift for production banking environment
- Add CI/CD pipeline for automated testing and deployment
- Implement model evaluation framework for answer quality monitoring

---

## Banking Context

This project was built with the regulated banking environment in mind:
- **Data privacy** — API keys managed via environment variables, never hardcoded or baked into Docker images
- **Input validation** — Pydantic models validate all incoming requests, rejecting malformed data automatically
- **Honest responses** — System acknowledges when information is not available rather than hallucinating
- **Audit ready** — Clean, documented codebase suitable for compliance review
- **Portable deployment** — Docker containerisation ensures consistent behaviour across environments

---

## Author

Built as part of an AI engineering portfolio project demonstrating multi-provider RAG implementation in a regulated banking context.

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-nanduks8%2Frag--banking--app-blue)](https://hub.docker.com/r/nanduks8/rag-banking-app)
[![GitHub](https://img.shields.io/badge/GitHub-nandu8-black)](https://github.com/nandu8)
