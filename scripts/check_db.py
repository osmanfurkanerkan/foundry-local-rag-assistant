"""Faz 1.3 dogrulama: Chroma koleksiyonunda kac chunk kayitli, kontrol eder.

Kullanim: .venv/Scripts/python.exe scripts/check_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

if __name__ == "__main__":
    store = ChromaVectorStore()
    print(f"Koleksiyondaki toplam chunk sayisi: {store.count()}")
