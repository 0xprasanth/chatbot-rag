from pydantic import BaseModel
from typing import List, Optional, Any


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    metadata: Optional[List[Any]] = None


class IngestResponse(BaseModel):
    status: str
    documents_loaded: int