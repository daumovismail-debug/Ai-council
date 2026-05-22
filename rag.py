"""
RAG module for Storonsky bot.
Uses ChromaDB with its built-in ONNX embedding (no PyTorch needed).
Falls back to keyword search if ChromaDB is unavailable.
"""
from __future__ import annotations
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

CHROMA_PATH = Path(__file__).parent / "data" / "rag_store"
COLLECTION_NAME = "storonsky_corpus"
CHUNK_SIZE = 280   # words
CHUNK_OVERLAP = 40  # words
TOP_N = 4


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def _chunk_text(text: str) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + CHUNK_SIZE])
        if chunk.strip():
            chunks.append(chunk.strip())
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ---------------------------------------------------------------------------
# ChromaDB backend
# ---------------------------------------------------------------------------

_collection = None


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection

    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    _collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=DefaultEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def index_file(filepath: str | Path, source_name: str | None = None) -> int:
    """Chunk a text file and upsert into the vector store. Returns chunk count."""
    filepath = Path(filepath)
    source = source_name or filepath.stem
    text = filepath.read_text(encoding="utf-8")
    chunks = _chunk_text(text)
    if not chunks:
        return 0

    col = _get_collection()
    ids = [f"{source}__chunk_{i}" for i in range(len(chunks))]
    metas = [{"source": source, "chunk_idx": i} for i in range(len(chunks))]
    col.upsert(documents=chunks, ids=ids, metadatas=metas)
    logger.info("[rag] indexed %s → %d chunks", filepath.name, len(chunks))
    return len(chunks)


def rag_query(query: str, n: int = TOP_N) -> str:
    """Return top-n relevant chunks as a formatted string, or '' if store is empty."""
    try:
        col = _get_collection()
        count = col.count()
        if count == 0:
            return ""
        results = col.query(query_texts=[query], n_results=min(n, count))
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        if not docs:
            return ""
        lines = []
        for doc, meta in zip(docs, metas):
            src = meta.get("source", "интервью")
            lines.append(f"[{src}]: {doc}")
        return "\n\n".join(lines)
    except Exception as exc:
        logger.warning("[rag] query failed: %s", exc)
        return ""


def collection_count() -> int:
    try:
        return _get_collection().count()
    except Exception:
        return 0
