import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api.routes import ingest, router

DATA_DIR = "data"
FAISS_STORE = "faiss_store"


def _has_pdf_data() -> bool:
    data_path = Path(DATA_DIR).resolve()
    if not data_path.is_dir():
        return False
    return bool(list(data_path.glob("**/*.pdf")))


def _faiss_store_ready() -> bool:
    faiss_path = os.path.join(FAISS_STORE, "faiss.index")
    meta_path = os.path.join(FAISS_STORE, "metadata.pkl")
    return os.path.exists(faiss_path) and os.path.exists(meta_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not _has_pdf_data():
        raise RuntimeError(
            "Cannot start: data directory is empty or contains no PDFs. For now only PDF is supported."
        )
    if not _faiss_store_ready():
        await asyncio.to_thread(ingest)
    yield


app = FastAPI(title="RAG Chatbot API", version="1.0.0", lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
