from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import OllamaEmbeddings
import numpy as np
from src.services.data_loader import load_all_documents

from src.settings.config import get_settings

settings = get_settings()


# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
class EmbeddingPipeline:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200, base_url:str ="http://localhost:11434"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # self.model = SentenceTransformer(model_name)
        self.model =  OllamaEmbeddings(model=model_name,base_url="http://localhost:11434")
        print(f"[INFO] Loaded embedding model: {model_name}")

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def embed_chunks(self, chunks: List[Any]) -> np.ndarray:
        if not chunks:
            return np.array([], dtype=np.float32)
        
        texts = [chunk.page_content for chunk in chunks]

        print(f"[INFO] Generating embeddings for {len(texts)} chunks...")
        # embeddings = self.model.embed_documents(texts,show_progress_bar=True )
        
        embeddings = np.array(
            self.model.embed_documents(texts),
            dtype=np.float32
        )
        
        print(f"[INFO] Embeddings shape: {embeddings.shape}")
        return embeddings

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    emb_pipe = EmbeddingPipeline(model_name=settings.ollama_embedding_model)
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print("[INFO] Example embedding:", embeddings[0][:20] if len(embeddings) > 0 else None)