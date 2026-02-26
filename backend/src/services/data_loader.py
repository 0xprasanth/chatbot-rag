from pathlib import Path
from typing import List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_csv_documents(data_path: Path) -> List[Any]:
    """
    Load CSV files from the data directory and convert to LangChain document structure.
    """
    csv_files = list(data_path.glob("**/*.csv"))

    for csv_file in csv_files:
        print(f"[DEBUG] Loading PDF: {csv_file}")
        try:
            loader = CSVLoader(str(csv_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} CSV docs from {csv_file}")
            return loaded if loaded else []
        except Exception as e:
            print(f"[ERROR] Failed to load CSV {csv_file}: {e}")


def load_pdf_documents(data_path: Path) -> List[Any]:
    pdf_files = list(data_path.glob("**/*.pdf"))
    for pdf_file in pdf_files:
        print(f"[DEBUG] Loading PDF: {pdf_file}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded PDF: {len(loaded)} pdf's from {pdf_file}")
            return loaded if loaded else []
        except Exception as e:
            print(f"[ERROR] Failed to load PDF {pdf_file}: {e}")


def load_markdown_documents(data_path: Path) -> List[Any]:
    markdown_files = list(data_path.glob("**/*.md"))
    for markdown_file in markdown_files:
        print(f"[DEBUG] Loading Markdown: {markdown_file}")
        try:
            loader = UnstructuredMarkdownLoader(str(markdown_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} Markdown docs from {markdown_file}")
            return loaded if loaded else []
        except Exception as e:
            print(f"[ERROR] Failed to load Markdown {markdown_file}: {e}")


def load_txt_documents(data_path: Path) -> List[Any]:
    txt_files = list(data_path.glob("**/*.txt"))
    for txt_file in txt_files:
        print(f"[DEBUG] Loading TXT: {txt_file}")
        try:
            loader = TextLoader(str(txt_file))
            loaded = loader.load()
            print(f"[DEBUG] Loaded {len(loaded)} TXT docs from {txt_file}")
            return loaded if loaded else []
        except Exception as e:
            print(f"[ERROR] Failed to load TXT {txt_file}: {e}")


def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from the data directory and convert to LangChain document structure.
    Supported: PDF, TXT, CSV, Markdown
    """
    data_path = Path(data_dir).resolve()
    print(f"[debug] data path: {data_path}")

    documents = []
    documents.extend(load_pdf_documents(data_path))
    # documents.extend(load_csv_documents(data_path))
    # documents.extend(load_markdown_documents(data_path) or [])
    # documents.extend(load_txt_documents(data_path) or [])
    print(f"[INFO] Total documents loaded: {len(documents)}")

    return documents


# Example usage
if __name__ == "__main__":
    docs = load_all_documents("data")
    print(f"Loaded {len(docs)} documents.")
    # print("Example document:", docs[0] if docs else None)
