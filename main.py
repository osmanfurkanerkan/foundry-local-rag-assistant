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
from rag_engine.llm.langchain_foundry_provider import LangchainFoundryProvider
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.langchain_retriever_adapter import LangchainRetrieverAdapter
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

EXIT_COMMANDS = {"exit", "quit", "q"}


def build_pipeline() -> RagPipeline:
    # Faz 4.1: retrieval (Faz 2'nin hybrid+rerank yigini) ve LLM (Foundry
    # Local) artik LangChain'in standart arayuzleri (BaseRetriever, LCEL
    # chain) uzerinden calisiyor -- ama RagPipeline hicbir sey bilmiyor,
    # cunku ikisi de ayni RetrievalStrategy/LLMProvider sozlesmesini tasiyor.
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())
    langchain_retriever = LangchainRetrieverAdapter(strategy=reranking_retriever, k=3)
    return RagPipeline(retriever=langchain_retriever, llm=LangchainFoundryProvider())


# Faz 3.1: kac onceki turun modele gosterilecegi -- sinirsiz buyursen prompt
# gereksiz sisirilir, gecmis konuyla alakasi azalan eski turlar de gurultu katar.
# Faz sonrasi (demo hazirligi): kucuk/sinirli VRAM'li GPU'larda buyuyen
# gecmisin CUDA out-of-memory'ye yol actigi gozlemlendi (bkz. PROJECT_PLAN.md)
# -- deger 5'ten 3'e dusuruldu, ama bu tam bir cozum degil, sadece riski azaltir.
HISTORY_LIMIT = 3

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

        # Faz 3.3: cevabi tek seferde degil, kelime kelime canli yazdir.
        stream, get_sources = pipeline.answer_query_stream(question, history=history[-HISTORY_LIMIT:])
        print("\nCevap: ", end="", flush=True)
        answer_parts: list[str] = []
        for piece in stream:
            print(piece, end="", flush=True)
            answer_parts.append(piece)
        print()

        sources = get_sources()
        if sources:
            print(f"Kaynak: {', '.join(sources)}")
        print()

        history.append(ConversationTurn(question=question, answer="".join(answer_parts)))
