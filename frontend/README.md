# RAG Chatbot — Frontend

Streamlit UI for the RAG (Retrieval-Augmented Generation) chatbot. 

## Single-page interface
- Chat with the assistant
- Answers are powered by the FastAPI backend and your pre-ingested documents.

## Prerequisites

- **Python 3.13+**
- Backend running and reachable (see [backend README](../backend/README.md))

## Project structure

```
frontend/
├── main.py          # Streamlit app: chat UI and session state
├── api_client.py    # HTTP client for backend (POST /chat)
├── pyproject.toml   # Project and dependencies (uv/pip)
├── requirements.txt
└── README.md
```

## Setup

**With uv:**

```bash
cd frontend
uv sync
```

**With pip:**

```bash
cd frontend
pip install -r requirements.txt
```

## Environment

| Variable      | Default              | Description                    |
|---------------|----------------------|--------------------------------|
| `BACKEND_URL` | `http://localhost:8000` | Base URL of the FastAPI backend |

Create a `.env` in the frontend directory or set the variable in the shell. Trailing slashes are stripped.

## Run

```bash
streamlit run main.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

## Backend contract

The app talks to the backend **POST `/chat`** endpoint:

- **Request:** `{"query": "<user message>", "top_k": 5}` (optional)
- **Response:** `{"answer": "<text>", "sources": [...], "metadata": [...]}`

The UI currently displays only `answer`; 
- the client uses a 120s timeout and surfaces backend `detail` on errors.

## Dependencies

- **streamlit** — Web UI
- **httpx** — HTTP client for the backend
- **python-dotenv** — Load `BACKEND_URL` from `.env`

See `pyproject.toml` for versions and optional tooling (e.g. uv).
