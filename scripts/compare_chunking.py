"""Faz 2.3: FixedSizeChunker (kelime bazli) ile MarkdownChunker (baslik/paragraf
bazli) sonuclarini karsilastirir.

Kullanim: .venv/Scripts/python.exe scripts/compare_chunking.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.ingestion.cleaner import clean_text
from rag_engine.ingestion.fixed_size_chunker import FixedSizeChunker
from rag_engine.ingestion.loader import load_raw_documents
from rag_engine.ingestion.markdown_chunker import MarkdownChunker

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

if __name__ == "__main__":
    documents = load_raw_documents(RAW_DIR)
    fixed_chunker = FixedSizeChunker(chunk_size=300, overlap=50)
    markdown_chunker = MarkdownChunker(chunk_size=1500, overlap=200)

    total_fixed = 0
    total_markdown = 0

    for source, raw_text in documents:
        cleaned = clean_text(raw_text)
        fixed_chunks = fixed_chunker.chunk(source, cleaned)
        markdown_chunks = markdown_chunker.chunk(source, cleaned)

        total_fixed += len(fixed_chunks)
        total_markdown += len(markdown_chunks)

        print(f"{source}: fixed={len(fixed_chunks)} chunk, markdown={len(markdown_chunks)} chunk")

    print(f"\nTOPLAM: fixed={total_fixed} chunk, markdown={total_markdown} chunk")

    print("\n--- Ornek: ilk dokumanin ilk markdown chunk'i ---")
    example_source, example_text = documents[0]
    example_chunks = markdown_chunker.chunk(example_source, clean_text(example_text))
    print(example_chunks[0].text[:400])
