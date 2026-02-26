# RAG Chatbot — Backend

Backend API for a **Retrieval-Augmented Generation (RAG)** chatbot. It loads documents from a data directory, builds a FAISS vector index over chunked and embedded text, and answers user questions by retrieving relevant chunks and generating answers via an Ollama LLM.

- **Architecture** — High-level design, data flow, and how components interact (see [Architecture and data flow](#architecture-and-data-flow) and [Module reference](#module-reference)).
- **Setup steps** — Prerequisites, installation, configuration, and how to run the app (see [Prerequisites](#prerequisites) through [Running the application](#running-the-application)).
- **Design decisions** — Rationale for key technical choices (see [Design decisions](#design-decisions)).
- **Potential improvements** — Brief note on enhancements possible with additional time (see [Potential improvements with additional time](#potential-improvements-with-additional-time)).

---

## Table of contents

- [Overview](#overview)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup steps](#setup-steps)
- [Configuration](#configuration)
- [Architecture and data flow](#architecture-and-data-flow)
- [Design decisions](#design-decisions)
- [Module reference](#module-reference)
- [API reference](#api-reference)
- [Running the application](#running-the-application)
- [Ingest and vector store](#ingest-and-vector-store)
- [Extending the backend](#extending-the-backend)
- [Potential improvements with additional time](#potential-improvements-with-additional-time)

---

## Overview

- **Stack:** FastAPI, LangChain, FAISS (vector search), Ollama (embeddings + chat LLM).
- **Input:** Documents under a configurable `data` directory (e.g. PDFs). Loaded, chunked, embedded, and stored in a persistent FAISS index.
- **Chat:** User query → embed → retrieve top‑k chunks → build context → LLM generates answer from context only.
- **Two chat implementations:**  
  - `**/chat`** — `RAGSearch`: LangChain `ChatOllama` + same vector store.  
  - `**/chatv2`** — `RagPipeline`: raw `ollama.chat()` + same vector store (different prompt/model wiring).

Greetings and meta questions (e.g. “Hi”, “Who are you?”) are detected and answered with a fixed friendly message without calling the vector store or LLM.

---

## Project structure

```
backend/
├── app.py                 # FastAPI app entry; mounts router.
├── main.py                # Script entry (e.g. load docs, build store, run RAGSearch).
├── pyproject.toml         # Project and dependencies (uv).
├── requirements.txt       # Pip-style dependencies.
├── README.md              # This file.
├── .env                   # Optional; env vars for config (see Configuration).
├── data/                  # Default directory for source documents (e.g. PDFs).
├── faiss_store/           # Created at runtime: FAISS index + metadata pickle.
│   ├── faiss.index
│   └── metadata.pkl
└── src/
    ├── __init__.py
    ├── api/
    │   ├── routes.py      # HTTP endpoints: health, chat, chatv2, ingest.
    │   └── schemas.py     # Pydantic models for request/response.
    ├── settings/
    │   ├── __init__.py
    │   └── config.py     # Settings from environment (Ollama, RAG, upload).
    └── services/
        ├── data_loader.py   # Load PDF (and optionally CSV, etc.) into LangChain Documents.
        ├── embedding.py     # Chunk documents and embed via Ollama.
        ├── vector_store.py  # FAISS index + metadata; build, load, query.
        ├── search.py        # RAGSearch: retrieve + generate with ChatOllama.
        ├── rag_pipeline.py  # RagPipeline: retrieve + generate with ollama.chat().
        └── greetings.py     # Detect greetings/meta questions; return canned response.
```

---

## Prerequisites

- **Python** 3.13+ (per `pyproject.toml`).
- **Ollama** running locally (default `http://localhost:11434`):
  - An **embedding model** (e.g. `nomic-embed-text`) for indexing and query embedding.
  - A **chat model** (e.g. `gemma3:1b`, `llama3.2`) for generating answers.
- **Documents** in the `data` directory (e.g. `data/pdf/*.pdf`) for ingestion.

---

## Setup steps

1. **Install Python 3.13+** and ensure Ollama is installed and running (`ollama serve`).
2. **Pull Ollama models** (from project root or backend):
  ```bash
   ollama pull nomic-embed-text
   ollama pull gemma3:1b   # or llama3.2 / your preferred chat model
  ```
3. **Install backend dependencies** (from `backend/`):
  ```bash
   uv sync
   # or: pip install -r requirements.txt
  ```
4. **Configure environment** (optional): Create a `.env` in the project root with `OLLAMA_CHAT_MODEL`, `OLLAMA_EMBEDDING_MODEL`, and any overrides (see [Configuration](#configuration)).
5. **Add documents**: Place PDFs (or other supported files) in `backend/data/` (e.g. `backend/data/pdf/`).
6. **Run the API** (from `backend/`):
  ```bash
   uv run uvicorn app:app --reload
  ```
7. **Ingest (if needed)**: If the vector store is empty or you added new files, call `POST /ingest` to build/rebuild the index. The app can also auto-build on first request if no index exists.

---

## Installation

From the `backend` directory:

```bash
# Using uv (recommended)
uv sync

# Or with pip
pip install -r requirements.txt
```

Create a `.env` in the project root (or `backend/`) to override defaults (see [Configuration](#configuration)).

---

## Configuration

Settings are read from the environment; a `.env` file is loaded from the repo root (see `config.py`).


| Variable                 | Description                                | Default                  |
| ------------------------ | ------------------------------------------ | ------------------------ |
| `OLLAMA_HOST`            | Ollama API base URL                        | `http://localhost:11434` |
| `OLLAMA_API_KEY`         | Optional API key for Ollama                | —                        |
| `OLLAMA_CHAT_MODEL`      | Chat model name (e.g. for `/chat` and RAG) | (required in practice)   |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model name                       | `nomic-embed-text`       |
| `CHUNK_SIZE`             | Text chunk size (chars) for splitting      | `512`                    |
| `CHUNK_OVERLAP`          | Overlap between chunks                     | `64`                     |
| `TOP_K`                  | Default number of chunks to retrieve       | `10`                     |
| `MAX_UPLOAD_SIZE_MB`     | Max upload size (for future upload API)    | `20`                     |
| `HF_TOKEN`               | Hugging Face token (if needed)             | —                        |


- Allowed file extensions for upload (config) are `.pdf`, `.txt`, `.csv`.

## Data Ingestion:

- Place your documents in `backend/data` and run ****`/ingest` 

---

## Architecture and data flow

1. **Ingest (one-off or on demand)**
  - `data_loader` loads documents from `data/` (e.g. PDFs) into LangChain `Document` objects.  
  - `EmbeddingPipeline` chunks them (RecursiveCharacterTextSplitter) and embeds chunks with Ollama.  
  - `FaissVectorStore` stores embeddings in FAISS and chunk text (and optional metadata) in `metadata.pkl`.
2. **Chat request**
  - **Greeting/meta:** If `greetings.get_greeting_response(query)` returns a string, the API responds with that and no RAG/LLM.  
  - **RAG path:**  
    - Query is embedded with the same Ollama embedding model.  
    - FAISS returns top‑k nearest chunks (by L2 distance).  
    - Chunk texts are concatenated into a single context string.  
    - Context + query are sent to the LLM with a “answer only from context” prompt.  
    - Response (answer + sources/metadata) is returned.
3. **Two pipelines**
  - **RAGSearch** (`/chat`): Uses LangChain `ChatOllama` and the shared vector store; prompt is in `search.py`.  
  - **RagPipeline** (`/chatv2`): Uses `ollama.chat()` with a fixed model name (e.g. `llama3.2`) and the same store; prompt is in `rag_pipeline.py`.

---

## Design decisions


| Decision                                | Rationale                                                                                                                                                                                                                         |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FAISS for vector search**             | Simple, file-based persistence (`faiss.index` + `metadata.pkl`), no separate database. Good for single-node and moderate scale; L2 distance is sufficient for semantic similarity with normalized embeddings.                     |
| **Ollama for embeddings and chat**      | Keeps the stack local and model-agnostic; same interface for different models. Embeddings (e.g. `nomic-embed-text`) and chat (e.g. `gemma3:1b`, `llama3.2`) are configured via env.                                               |
| **Greeting and meta-question handling** | Avoids unnecessary retrieval and LLM calls for “Hi”, “Who are you?”, etc. Reduces latency and cost and gives a consistent, on-brand reply. Implemented via a simple phrase/prefix check in `greetings.py`.                        |
| **Context-only answers**                | Prompts explicitly instruct the LLM to answer only from the provided context and to say “I don’t know” (or similar) when the answer isn’t in context. Reduces hallucination and keeps answers grounded in the ingested documents. |
| **RecursiveCharacterTextSplitter**      | LangChain’s default splitter; respects paragraph and line boundaries. Chunk size and overlap are configurable via env for different document types and embedding model limits.                                                    |
| **Persistent vector store on disk**     | Index is built once (or via `/ingest`) and loaded on startup. No need to re-embed on every restart; rebuild only when documents change.                                                                                           |


---

## API reference

Base URL: `http://localhost:8000` (when run with uvicorn on port 8000).


| Method | Path      | Description                                  |
| ------ | --------- | -------------------------------------------- |
| GET    | `/health` | Health check; returns `{"status": "ok"}`.    |
| POST   | `/chat`   | RAG chat (RAGSearch + LangChain ChatOllama). |
| POST   | `/chatv2` | RAG chat (RagPipeline + ollama.chat).        |
| POST   | `/ingest` | Rebuild vector store from `data/` documents. |


### POST `/chat`

**Request body (JSON):**

```json
{
  "query": "Your question here",
  "top_k": 5
}
```

`top_k` is optional; default is 5 (number of chunks to retrieve).

**Response (JSON):**

```json
{
  "answer": "Generated answer based on retrieved context.",
  "sources": ["chunk text 1", "chunk text 2", ...],
  "metadata": [{ "text": "..." }, ...]
}
```

For greeting/meta queries, `sources` and `metadata` are empty arrays.

### POST `/ingest`

No request body. Loads documents from the configured `data` directory (e.g. `backend/data`), chunks and embeds them, and writes `faiss_store/faiss.index` and `faiss_store/metadata.pkl`.  
**Response (JSON):**

```json
{
  "status": "success",
  "documents_loaded": 42
}
```

---

## Running the application

From the `backend` directory (with Ollama running and models pulled):

```bash
# Default: app on 0.0.0.0:8000
uv run uvicorn app:app --reload

# Or with Python
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

- **Docs:** `http://localhost:8000/docs` (Swagger UI).  
- **Health:** `curl http://localhost:8000/health`.  
- **Chat:** `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"query":"What is X?"}'`.

`main.py` is a standalone script (load docs, build/load store, run `RAGSearch.search_and_summarize`) and is not required to run the API.

## Ingest and vector store

- **First run:** If `faiss_store/faiss.index` and `faiss_store/metadata.pkl` do not exist, `RAGSearch` and `RagPipeline` will load documents from `"data"` and build the store on startup.  
- **Rebuild:** Call **POST /ingest** to rebuild from current `data/` contents; this overwrites the existing FAISS index and metadata.  
- **Persistence:** The store is on disk; restarting the app loads it from `faiss_store/` and does not re-ingest unless you delete those files or run ingest again.

## Potential improvements with additional time

- **Unified chat pipeline**
  - Support switching between different LLMs to compare responses and customize output.
- **Token usage and latency in API** 
  - Return `input_tokens`, `output_tokens`, and `response_time_seconds` in the chat response so clients can show usage and speed; requires reading LLM response metadata (e.g. Ollama’s `prompt_eval_count` / `eval_count`) and timing the call.
- **Richer source metadata in responses**
  - Persist and return per-chunk metadata (source file path, page number, document title) so the UI can show “Source: doc.pdf, p. 3” and support citation or deep links.
- **Document upload API**
  - Allow uploading PDFs via the API (within `MAX_UPLOAD_SIZE_MB` and allowed extensions), write to `data/`, then trigger ingest or incremental index update.
- **Conversation history**
  - Keep a short conversation window (e.g. last N turns) and pass it to the LLM for follow-up questions; optional chat/session ID for multi-user.
- **Evaluation and monitoring**
  - Add a small set of example queries and expected behavior (or manual labels) to track retrieval quality and answer relevance over time; optional logging to LangSmith or similar.

