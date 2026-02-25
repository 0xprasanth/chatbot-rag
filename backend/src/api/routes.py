from fastapi import APIRouter, HTTPException
from src.api.schemas import ChatRequest, ChatResponse, HealthResponse, IngestResponse
from src.services.data_loader import load_all_documents
from src.services.vector_store import FaissVectorStore
from src.services.search import RAGSearch
from src.services.greetings import get_greeting_response
from src.settings.config import get_settings

router = APIRouter()
settings = get_settings()
rag_search = RAGSearch()


def _chat_response(answer: str, sources: list, metadata: list):
    return {"answer": answer, "sources": sources, "metadata": metadata}


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    greeting = get_greeting_response(req.query)
    if greeting is not None:
        return _chat_response(greeting, [], [])
    try:
        answer, source_chunks, metadata = rag_search.chat(req.query, req.top_k or 5)
        return _chat_response(answer, source_chunks, metadata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/ingest", response_model=IngestResponse)
def ingest():

    docs = load_all_documents("data")

    store = FaissVectorStore(
        "faiss_store",
        chunk_overlap=settings.chunk_overlap,
        chunk_size=settings.chunk_size,
        embedding_model=settings.ollama_embedding_model,
    )

    store.build_from_documents(docs)

    return {"status": "success", "documents_loaded": len(docs)}
