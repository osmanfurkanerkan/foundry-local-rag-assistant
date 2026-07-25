"""Faz 1.2: data/raw/ dokumanlarini temizleyip chunk'lara bolme dogrulamasi.

Kullanim: .venv/Scripts/python.exe scripts/build_chunks.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.ingestion.cleaner import clean_text
from rag_engine.ingestion.fixed_size_chunker import FixedSizeChunker
from rag_engine.ingestion.loader import load_raw_documents

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

if __name__ == "__main__":
    documents = load_raw_documents(RAW_DIR)
    chunker = FixedSizeChunker(chunk_size=300, overlap=50)

    all_chunks = []
    for source, raw_text in documents:
        cleaned = clean_text(raw_text)
        chunks = chunker.chunk(source, cleaned)
        all_chunks.extend(chunks)
        print(f"  {source}: {len(chunks)} chunk")

    print(f"\nToplam: {len(documents)} dokuman -> {len(all_chunks)} chunk")

    sample = all_chunks[0]
    print("\nOrnek chunk:")
    print(f"  id: {sample.id}")
    print(f"  source: {sample.source}")
    print(f"  text (ilk 200 karakter): {sample.text[:200]}...")
