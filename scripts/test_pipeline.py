"""Faz 1.5: answer_query() ile uctan uca RAG akisini test eder.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe scripts/test_pipeline.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.foundry_local_provider import FoundryLocalProvider
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

TEST_QUESTIONS = [
    "What is Foundry Local and why does it run locally?",
    "How does RAG work? Explain the steps.",
]

if __name__ == "__main__":
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    pipeline = RagPipeline(retriever=hybrid_retriever, llm=FoundryLocalProvider())

    for question in TEST_QUESTIONS:
        print(f"\n{'=' * 70}")
        print(f"SORU: {question}")
        print("=" * 70)
        print(pipeline.answer_query(question))
