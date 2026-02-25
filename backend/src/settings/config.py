"""Application config: env only for Ollama URL (and optional API key from existing Ollama setup)."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from backend/ so env vars are available to os.getenv (e.g. when run from project root)
# _env_path = Path(__file__).resolve().parent.parent / ".env"
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


@lru_cache
def get_settings():
    return Settings()


class Settings:
    """Settings loaded from environment."""
    hf_token: str = os.getenv("HF_TOKEN")

    # Ollama (existing setup - URL and optional API key from your env)
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_api_key: Optional[str] = os.getenv("OLLAMA_API_KEY")
    ollama_chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


    # RAG
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "512"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "64"))
    top_k: int = int(os.getenv("TOP_K", "10"))

    # Upload
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
    allowed_extensions: set = frozenset({".pdf", ".txt", ".md"})
