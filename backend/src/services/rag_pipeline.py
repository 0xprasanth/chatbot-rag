from langchain_ollama import ChatOllama
import ollama
from src.services.vector_store import FaissVectorStore
from src.settings.config import get_settings
import os

settings = get_settings()


class RagPipeline:

    def __init__(
        self,
        persist_dir: str = "faiss_store",
        embedding_model: str = settings.ollama_embedding_model,
        llm_model: str = settings.ollama_chat_model,
    ):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from data_loader import load_all_documents

            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
        self.llm = ChatOllama(
            ollama_api_key=settings.ollama_api_key,
            model=settings.ollama_chat_model,
            temperature=0.1,
            max_tokens=1024,
        )

        print(f"[INFO] Ollama LLM initialized: {llm_model}")

    def retrieve(self, query: str, top_k: int = 5):

        results = self.vectorstore.query(query, top_k=top_k)

        texts = []
        metadatas = []

        for r in results:
            if r["metadata"]:
                texts.append(r["metadata"]["text"])
                metadatas.append(r["metadata"])

        return texts, metadatas

    def generate_answer(self, query: str, contexts: list[str]):

        context_text = "\n\n".join(contexts)

        prompt = f"""
Answer ONLY from the provided context.

Context:
{context_text}

Question:
{query}

If answer not in context, say "I don't know".
"""

        response = ollama.chat(
            model="llama3.2", messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]

    def chat(self, query: str, top_k: int = 5):

        contexts, metadata = self.retrieve(query, top_k)

        answer = self.generate_answer(query, contexts)

        return answer, contexts, metadata
