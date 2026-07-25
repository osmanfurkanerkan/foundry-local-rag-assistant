"""Faz 1.4: get_top_chunks() sonuclarinin gercekten alakali olup olmadigini
elle kontrol etmek icin birkac ornek soru calistirir.

Kullanim: .venv/Scripts/python.exe scripts/test_retrieval.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.retrieval.retriever import Retriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

TEST_QUERIES = [
    "Foundry Local'i bilgisayarima nasil kurarim?",
    "RAG nedir ve nasil calisir?",
    "Embedding ve cosine similarity arasindaki iliski nedir?",
    "Foundry Local CLI ile bir modeli nasil yuklerim?",
]

if __name__ == "__main__":
    retriever = Retriever(embedder=FoundryLocalEmbedder(), vectorstore=ChromaVectorStore())

    for query in TEST_QUERIES:
        print(f"\n{'=' * 70}")
        print(f"SORU: {query}")
        print("=" * 70)

        for rank, chunk in enumerate(retriever.get_top_chunks(query, k=3), start=1):
            print(f"\n  [{rank}] source={chunk.source} (chunk #{chunk.chunk_index})")
            print(f"      {chunk.text[:200]}...")
