from src.services.data_loader import load_all_documents
from src.services.vector_store import FaissVectorStore
from src.services.search import RAGSearch
from src.settings.config import get_settings

settings = get_settings()

# Example usage
if __name__ == "__main__":
    
    docs = load_all_documents("data")
    store = FaissVectorStore("faiss_store", chunk_overlap=settings.chunk_overlap, chunk_size=settings.chunk_size, embedding_model=settings.ollama_embedding_model)
    #store.build_from_documents(docs)
    store.load()
    #print(store.query("What is attention mechanism?", top_k=3))
    rag_search = RAGSearch()
    query = "Explain Dynamic Routing"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)