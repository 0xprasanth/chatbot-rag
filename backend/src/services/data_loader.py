from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders import JSONLoader

def load_csv_documents(data_path: Path) -> List[Any]:
    """
    Load CSV files from the data directory and convert to LangChain document structure.
    """
    csv_files = list(data_path.glob('**/*.csv'))
    
    for csv_file in csv_files:
        print(f"[DEBUG] Loading PDF: {csv_file}")
        try:
            loader = CSVLoader(str(csv_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} CSV docs from {csv_file}")
            return loaded
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")

def load_pdf_documents(data_path: Path) -> List[Any]:
    pdf_files = list(data_path.glob('**/*.pdf'))
    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded PDF: {len(loaded)} pdf's from {pdf_file}")
            return loaded
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")


def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory and convert to LangChain document structure.
    Supported: PDF, TXT, CSV, Excel, Word, JSON
    """
    data_path = Path(data_dir).resolve()
    print(f"[debug] data path: {data_path}")

    documents = []
    documents.extend(load_pdf_documents(data_path))
    # documents.extend(load_csv_documents(data_path))

    print(f"[INFO] Total documents loaded: {len(documents)}")

    return documents

# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    print(f"Loaded {len(docs)} documents.")
    # print("Example document:", docs[0] if docs else None)