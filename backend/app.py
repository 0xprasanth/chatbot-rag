import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api.routes import ingest, router

FAISS_STORE = "faiss_store"


def _faiss_store_ready() -> bool:
    faiss_path = os.path.join(FAISS_STORE, "faiss.index")
    meta_path = os.path.join(FAISS_STORE, "metadata.pkl")
    return os.path.exists(faiss_path) and os.path.exists(meta_path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not _faiss_store_ready():
        await asyncio.to_thread(ingest)
    yield


app = FastAPI(title="RAG Chatbot API", version="1.0.0", lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
