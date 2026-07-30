"""Faz 5.3: Gercek Foundry Local sunucusuna ihtiyac duyan uctan uca testler.

Sunucu calismiyorsa (`require_live_server`) otomatik atlanir -- boylece bu
dosya CI'da (Faz 6.4, sunucusuz bir runner'da) hata vermez, sadece skip olur.
"""
import pytest

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.langchain_foundry_provider import LangchainFoundryProvider
from rag_engine.pipeline.prompt_builder import NOT_FOUND_MESSAGE
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.langchain_retriever_adapter import LangchainRetrieverAdapter
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def live_pipeline(require_live_server):
    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())
    langchain_retriever = LangchainRetrieverAdapter(strategy=reranking_retriever, k=3)
    return RagPipeline(retriever=langchain_retriever, llm=LangchainFoundryProvider())


def test_retrieval_is_not_empty_for_a_covered_topic(live_pipeline):
    chunks = live_pipeline._retriever.get_top_chunks("What is Foundry Local?", k=3)

    assert len(chunks) > 0


def test_answer_contains_expected_keyword_for_known_topic(live_pipeline):
    answer = live_pipeline.answer_query("What is Foundry Local?")

    assert "foundry local" in answer.text.lower()
    assert answer.sources


def test_answer_refuses_gracefully_for_unrelated_question(live_pipeline):
    answer = live_pipeline.answer_query("What is the capital of France?")

    assert NOT_FOUND_MESSAGE in answer.text
    assert answer.sources == []
