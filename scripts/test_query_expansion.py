"""Faz 4.2: Belirsiz/kotu ifade edilmis sorgularda, query expansion acik/kapali
retrieval sonuclarini karsilastirir.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe scripts/test_query_expansion.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.langchain_foundry_provider import LangchainFoundryProvider
from rag_engine.pipeline.query_expansion import expand_query
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

# Kasitli olarak belirsiz/kisa/gundelik ifade edilmis sorgular -- "mukemmel
# arama sorgusu" degil, gercek bir kullanicinin yazabilecegi turden.
VAGUE_QUERIES = [
    "how do i get this thing running on my machine?",
    "cli commands",
    "embeddings azure",
    "whats RAG",
]


def print_results(label: str, chunks) -> None:
    print(f"  -- {label} --")
    for rank, chunk in enumerate(chunks, start=1):
        print(f"  [{rank}] source={chunk.source} (chunk #{chunk.chunk_index})")
    print()


if __name__ == "__main__":
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())
    llm = LangchainFoundryProvider()

    for query in VAGUE_QUERIES:
        print(f"\n{'=' * 70}")
        print(f"HAM SORGU: {query}")
        expanded = expand_query(query, llm)
        print(f"GENISLETILMIS SORGU: {expanded}")
        print("=" * 70)

        print_results("Expansion KAPALI (ham sorguyla retrieval)", reranking_retriever.get_top_chunks(query, k=3))
        print_results("Expansion ACIK (genisletilmis sorguyla retrieval)", reranking_retriever.get_top_chunks(expanded, k=3))
