"""Detect greeting and meta questions and return a friendly response without calling RAG."""

import re
import random
from typing import Optional

# Exact phrases (after normalizing: strip, lower, collapse spaces)
GREETING_PHRASES = frozenset(
    {
        "hi",
        "hello",
        "hey",
        "hola",
        "hi there",
        "hello there",
        "hey there",
        "good morning",
        "good afternoon",
        "good evening",
        "good day",
        "howdy",
        "greetings",
        "how are you",
        "what's up",
        "whats up",
        "sup",
    }
)

# Prefixes for meta / identity questions (query starts with one of these)
META_PREFIXES = (
    "who are you",
    "what are you",
    "who created you",
    "who made you",
    "who built you",
    "what can you do",
    "what are you capable of",
    "what do you do",
    "what is your purpose",
    "tell me about yourself",
    "introduce yourself",
)

# List of possible greeting responses for greetings and meta questions
GREETING_RESPONSES = [
    """Hello! I'm a document Q&A assistant. I answer questions using the content from the documents that have been loaded into my knowledge base.

You can ask me things like:
• Explain ASCII
• What does dynamic routing mean?
• Summarize the document

If you'd like to know more about what I can do, just ask a question about the documents.""",
    """Hey there! I’m your helpful document assistant. I use the documents you've uploaded to provide accurate answers to your questions.

You might ask things like:
• What is the main idea of the document?
• Define a technical term from your docs
• Summarize this chapter

If you need anything, just ask me about your uploaded materials!""",
    """Greetings! I assist in answering questions using information from your loaded documents.

Need ideas? Try:
• What does this document cover?
• Give me a summary of section 2
• Explain [some concept] based on the docs

Whenever you’re ready, just ask me something about your documents!""",
]


def _normalize(query: str) -> str:
    """Strip and collapse whitespace, lower case."""
    return " ".join(query.strip().lower().split())


def get_greeting_response(query: str) -> Optional[str]:
    """
    If the query is a greeting or meta question (who are you, what can you do, etc.),
    return a friendly response string randomly selected from a set.
    Otherwise return None.
    """
    if not query or not query.strip():
        return None
    normalized = _normalize(query)
    if normalized in GREETING_PHRASES:
        return random.choice(GREETING_RESPONSES)
    for prefix in META_PREFIXES:
        if normalized.startswith(prefix) or normalized == prefix.rstrip("s"):
            return random.choice(GREETING_RESPONSES)
    return None
