"""Faz 1.6: Terminalden soru-cevap dongusu -- projenin MVP giris noktasi.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe main.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.foundry_local_provider import FoundryLocalProvider
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

EXIT_COMMANDS = {"exit", "quit", "q"}


def build_pipeline() -> RagPipeline:
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    return RagPipeline(retriever=hybrid_retriever, llm=FoundryLocalProvider())


if __name__ == "__main__":
    pipeline = build_pipeline()

    print("Local RAG Assistant (Foundry Local + Foundry Local docs)")
    print("Cikmak icin 'exit' yaz.\n")

    while True:
        question = input("Soru: ").strip()
        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("Gorusuruz.")
            break

        answer = pipeline.answer_query(question)
        print(f"\nCevap: {answer}\n")
