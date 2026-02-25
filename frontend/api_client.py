"""Client for the FastAPI backend: upload and chat."""

import os
from typing import List, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def _error_detail(response: httpx.Response) -> str:
    """Extract backend error detail from response body for clearer user feedback."""
    try:
        body = response.json()
        if isinstance(body, dict) and "detail" in body:
            return str(body["detail"])
    except Exception:
        pass
    return f"{response.status_code} {response.reason_phrase}"


def send_chat_message(message: str) -> dict[str, Any]:
    """Send a chat message to POST /chat."""
    with httpx.Client(timeout=120.0) as client:
        r = client.post(
            f"{BACKEND_URL}/chat",
            json={"query": message},
            headers={"Content-Type": "application/json"},
        )
    r.raise_for_status()
    return r.json()
