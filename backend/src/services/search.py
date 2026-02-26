import os
from dotenv import load_dotenv
from ollama import ChatResponse
from src.services.vector_store import FaissVectorStore
from langchain_ollama import ChatOllama
from src.settings.config import get_settings
from typing import List

settings = get_settings()


class RAGSearch:
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

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        # prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""

        prompt = f"""
                Answer ONLY from the provided context.

                Context:
                {context}

                Question:
                {query}

                If answer not in context, say  "I don't have information about that".
                """
        response = self.llm.invoke([prompt])
        return response.content

    def retrieve_context(
        self, query: str, top_k: int = 5
    ) -> tuple[str, List[str], List[dict]]:
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        metadatas = [r.get("metadata", {}) for r in results]
        context = "\n\n".join(texts) if texts else ""
        if not context:
            return "No relevant documents found.", [], metadatas
        return context, texts, metadatas

    def generate_response(self, query: str, context: str) -> str:
        # Use a single user message so the model (especially small ones like gemma3:1b)
        # sees context and question together and is less likely to default to "I don't know"
        user_prompt = f"""Use the following context to answer the question. Base your answer only on this context.

                Context:
                {context}

                Question: {query}

                Answer the question using the context above. If the context does not contain enough information to answer, then say "I don't have information about that"."""
        response = self.llm.invoke([("user", user_prompt)])
        print("[DEBUG] Response:", response.to_json())
        return response.content

    def chat(self, query: str, top_k: int = 5) -> tuple[str, List[str], List[dict]]:
        context, source_chunks, metadatas = self.retrieve_context(query, top_k)
        print("[DEBUG] Context:", context[:50])
        answer = self.generate_response(query, context)
        return answer, source_chunks, metadatas


# Example usage
if __name__ == "__main__":
    rag_search = RAGSearch()
    query = "Explain ASCII"
    answer, context, metadatas = rag_search.chat(query, top_k=3)
    print("Answer:", answer)
    print("Context:", context[:50])
    print("Metadatas:", metadatas)
    # summary = rag_search.search_and_summarize(query, top_k=3)
    # print("Summary:", summary)
