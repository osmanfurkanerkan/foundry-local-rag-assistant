"""Faz 2.1/2.2: Saf embedding, hybrid (BM25 + embedding) ve hybrid+rerank
(cross-encoder) retrieval sonuclarini yan yana karsilastirir.

Kullanim: .venv/Scripts/python.exe scripts/test_retrieval.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

TEST_QUERIES = [
    "Foundry Local'i bilgisayarima nasil kurarim?",
    "RAG nedir ve nasil calisir?",
    "Embedding ve cosine similarity arasindaki iliski nedir?",
    "Foundry Local CLI ile bir modeli nasil yuklerim?",
]


def print_results(label: str, chunks) -> None:
    print(f"\n  -- {label} --")
    for rank, chunk in enumerate(chunks, start=1):
        print(f"  [{rank}] source={chunk.source} (chunk #{chunk.chunk_index})")
        print(f"      {chunk.text[:150]}...")


if __name__ == "__main__":
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())

    for query in TEST_QUERIES:
        print(f"\n{'=' * 70}")
        print(f"SORU: {query}")
        print("=" * 70)

        print_results("Sadece Embedding", embedding_retriever.get_top_chunks(query, k=3))
        print_results("Hybrid (BM25 + Embedding, RRF)", hybrid_retriever.get_top_chunks(query, k=3))
        print_results("Hybrid + Rerank (Cross-Encoder)", reranking_retriever.get_top_chunks(query, k=3))
