# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Activate venv (Windows)
venv\Scripts\activate

# Start the server with hot-reload
uvicorn main:app --reload

# First time only — build the vector database (takes several minutes, batched 30 chunks/30s)
curl -X POST "http://127.0.0.1:8000/setup"

# Ask a question
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the KYC requirements?"}'

# Ask using a specific LLM provider (per-request override)
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the KYC requirements?", "provider": "anthropic"}'
```

Interactive API docs at `http://127.0.0.1:8000/docs`.

## Docker

```bash
# Build
docker build -t rag-banking-app .

# Run (mount chroma_db so /setup only needs to run once)
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=... \
  -v "${PWD}/chroma_db:/app/chroma_db" \
  rag-banking-app
```

## Architecture

Three-file design:

- **`providers.py`** — provider factory. `get_llm(provider)` and `get_embeddings(provider)` return LangChain-compatible objects for `gemini`, `anthropic`, or `openai`. Single place to add or change models.
- **`rag_pipeline.py`** — RAG logic. Reads `LLM_PROVIDER` / `EMBEDDING_PROVIDER` env vars at module load to create the default LLM and embedding model. Exposes `load_and_chunk_document`, `create_vector_store`, `load_vector_store`, and `ask_question`.
- **`main.py`** — FastAPI app. Three endpoints: `GET /health`, `POST /setup`, `POST /ask`.

### Data flow

```
/setup: PDF → PyPDFLoader → RecursiveCharacterTextSplitter (500 chars, 50 overlap)
        → embedding model → ChromaDB (./chroma_db, batches of 30 with 30s delay)

/ask:   query → load ChromaDB → retriever (k=3) → stuff-documents chain → LLM → answer
```

The module-level `llm` in `rag_pipeline.py` is reused across requests. If `provider` is passed to `ask_question()`, a one-off LLM instance is created just for that call.

## Provider & Environment Config

`.env` controls defaults:

```
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
LLM_PROVIDER=gemini        # gemini | anthropic | openai
EMBEDDING_PROVIDER=gemini  # gemini | openai  (Anthropic has no embedding model)
```

**Critical:** `EMBEDDING_PROVIDER` must stay consistent after running `/setup`. Changing it without deleting `chroma_db/` will cause dimension mismatches at query time.

## Key Constraints

- No tests exist in this repo — verify by running the server and hitting the endpoints manually.
- `requirements.txt` is UTF-16 encoded (Windows pip freeze artifact). Add new packages by running `pip install` directly in the venv rather than editing the file manually.
- The `chroma_db/` directory is gitignored. A fresh clone requires running `/setup` before `/ask` will work.
- The Dockerfile copies `providers.py` is not yet listed — add it alongside `main.py` and `rag_pipeline.py` if rebuilding the image.
