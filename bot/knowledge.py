"""
Knowledge base loader and vector search via ChromaDB.
Supports TXT, PDF, DOCX files.
"""
import logging
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from bot.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "knowledge"
CHUNK_SIZE = 500        # chars per chunk
CHUNK_OVERLAP = 50      # overlap between chunks

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def _get_collection() -> chromadb.Collection:
    global _client, _collection
    if _collection is not None:
        return _collection

    Path(settings.CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    _client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    _collection = _client.get_or_create_collection(COLLECTION_NAME, embedding_function=ef)
    return _collection


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if len(c) > 30]


def _read_txt(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    return ""


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        logger.warning("pypdf not installed, skipping PDF: %s", path)
        return ""
    except Exception as e:
        logger.error("Failed to read PDF %s: %s", path, e)
        return ""


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        logger.warning("python-docx not installed, skipping DOCX: %s", path)
        return ""
    except Exception as e:
        logger.error("Failed to read DOCX %s: %s", path, e)
        return ""


def _read_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".txt":
        return _read_txt(path)
    elif ext == ".pdf":
        return _read_pdf(path)
    elif ext == ".docx":
        return _read_docx(path)
    return ""


def load_knowledge_base() -> int:
    """Load all documents from KNOWLEDGE_DIR into ChromaDB. Returns chunk count."""
    global _collection
    _collection = None  # reset to force reload

    kb_dir = Path(settings.KNOWLEDGE_DIR)
    if not kb_dir.exists():
        logger.warning("Knowledge base directory not found: %s", kb_dir)
        return 0

    col = _get_collection()

    # Clear existing data
    try:
        existing = col.get()
        if existing["ids"]:
            col.delete(ids=existing["ids"])
    except Exception:
        pass

    docs, ids, metas = [], [], []
    chunk_idx = 0

    for path in sorted(kb_dir.rglob("*")):
        if path.suffix.lower() not in (".txt", ".pdf", ".docx"):
            continue
        text = _read_file(path)
        if not text.strip():
            continue

        chunks = _chunk_text(text)
        for chunk in chunks:
            docs.append(chunk)
            ids.append(f"chunk_{chunk_idx}")
            metas.append({"source": path.name})
            chunk_idx += 1

        logger.info("Loaded %s: %d chunks", path.name, len(chunks))

    if docs:
        # Add in batches to avoid memory issues
        batch = 100
        for i in range(0, len(docs), batch):
            col.add(documents=docs[i:i+batch], ids=ids[i:i+batch], metadatas=metas[i:i+batch])

    logger.info("Knowledge base loaded: %d chunks total", chunk_idx)
    return chunk_idx


def search(query: str, n_results: int = 3) -> list[dict]:
    """Return relevant chunks for a query."""
    col = _get_collection()
    if col.count() == 0:
        return []

    results = col.query(
        query_texts=[query],
        n_results=min(n_results, col.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB returns L2 distance — convert to similarity score
        similarity = 1 / (1 + dist)
        if similarity >= settings.MIN_RELEVANCE:
            chunks.append({"text": doc, "source": meta.get("source", ""), "score": similarity})

    return chunks
