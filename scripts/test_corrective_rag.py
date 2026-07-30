"""Faz 4.3: Corrective RAG (self-grading retrieval) dongusunu, LangGraph'in
.stream() ile adim adim gozlemleyerek test eder -- her dugumden sonra state'in
nasil degistigini yazdirir, boylece "yetersiz bulundu -> tekrar denendi" akisi
gozle gorulebilir.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe scripts/test_corrective_rag.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.langchain_foundry_provider import LangchainFoundryProvider
from rag_engine.pipeline.corrective_rag_pipeline import build_corrective_rag_graph
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

# Faz 2.4 benchmarkinda bulunan zayif noktayi kullaniyoruz: bu soru konu
# olarak birbirine yakin dokumanlar (get-started / what-is-foundry-local /
# foundry-local-architecture) arasinda kaliyor. Bilincli olarak k=1 ile
# baslatiyoruz ki ilk deneme dar kalsin ve corrective dongu bir isi olsun.
QUESTION = "Foundry Local'i nasil kurar ve calistiririm?"
STARTING_K = 1

if __name__ == "__main__":
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())
    llm = LangchainFoundryProvider()

    graph = build_corrective_rag_graph(retriever=reranking_retriever, llm=llm)

    initial_state = {
        "question": QUESTION,
        "history": [],
        "search_query": QUESTION,
        "k": STARTING_K,
        "chunks": [],
        "attempts": 0,
        "is_sufficient": False,
        "answer_text": "",
        "sources": [],
    }

    print(f"SORU: {QUESTION}  (baslangic k={STARTING_K})\n")
    state = dict(initial_state)
    for step in graph.stream(initial_state):
        node_name, update = next(iter(step.items()))
        print(f"[{node_name}] {update}")
        state.update(update)

    print(f"\nDeneme sayisi: {state['attempts'] + 1}")
    print(f"CEVAP: {state['answer_text']}")
    print(f"Kaynak: {', '.join(state['sources']) if state['sources'] else '(yok)'}")
