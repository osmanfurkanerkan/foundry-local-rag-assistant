"""Faz 1.3: chunk'lari embed edip ChromaDB'ye kalici olarak yazma.

Onkosul: `foundry server start` calisiyor ve embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe scripts/build_vector_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.ingestion.cleaner import clean_text
from rag_engine.ingestion.loader import load_raw_documents
from rag_engine.ingestion.markdown_chunker import MarkdownChunker
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

if __name__ == "__main__":
    documents = load_raw_documents(RAW_DIR)
    chunker = MarkdownChunker(chunk_size=1500, overlap=200)

    all_chunks = []
    for source, raw_text in documents:
        cleaned = clean_text(raw_text)
        all_chunks.extend(chunker.chunk(source, cleaned))

    print(f"{len(all_chunks)} chunk embed edilecek...")

    embedder = FoundryLocalEmbedder()
    embeddings = embedder.embed([chunk.text for chunk in all_chunks])

    store = ChromaVectorStore()
    store.add(all_chunks, embeddings)

    print(f"Chroma'ya yazildi. Koleksiyondaki toplam chunk sayisi: {store.count()}")
