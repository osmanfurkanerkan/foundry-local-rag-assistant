"""Faz 1.6: Terminalden soru-cevap dongusu -- projenin MVP giris noktasi.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe main.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.interfaces.models import ConversationTurn
from rag_engine.llm.foundry_local_provider import FoundryLocalProvider
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

EXIT_COMMANDS = {"exit", "quit", "q"}


def build_pipeline() -> RagPipeline:
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())
    return RagPipeline(retriever=reranking_retriever, llm=FoundryLocalProvider())


# Faz 3.1: kac onceki turun modele gosterilecegi -- sinirsiz buyursen prompt
# gereksiz sisirilir, gecmis konuyla alakasi azalan eski turlar de gurultu katar.
HISTORY_LIMIT = 5

if __name__ == "__main__":
    pipeline = build_pipeline()
    history: list[ConversationTurn] = []

    print("Local RAG Assistant (Foundry Local + Foundry Local docs)")
    print("Cikmak icin 'exit' yaz.\n")

    while True:
        question = input("Soru: ").strip()
        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("Gorusuruz.")
            break

        answer = pipeline.answer_query(question, history=history[-HISTORY_LIMIT:])
        print(f"\nCevap: {answer}\n")
        history.append(ConversationTurn(question=question, answer=answer))
