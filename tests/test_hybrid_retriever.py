import pytest

from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from tests.conftest import FakeRetriever
from tests.conftest import make_chunk as chunk


def test_hybrid_retriever_requires_at_least_one_strategy():
    with pytest.raises(ValueError):
        HybridRetriever(strategies=[])


def test_hybrid_retriever_boosts_chunk_found_by_both_strategies():
    # doc-a: sadece strateji 1'de 1. sirada. doc-b: her iki stratejide de var,
    # ikisinde de daha dusuk sirada -- RRF birlesince doc-b one gecmeli.
    strategy_1 = FakeRetriever([chunk("doc-a"), chunk("doc-b")])
    strategy_2 = FakeRetriever([chunk("doc-c"), chunk("doc-b")])

    results = HybridRetriever(strategies=[strategy_1, strategy_2]).get_top_chunks("soru?", k=1)

    assert results[0].source == "doc-b"


def test_hybrid_retriever_respects_k():
    strategy = FakeRetriever([chunk("doc-a"), chunk("doc-b"), chunk("doc-c")])

    results = HybridRetriever(strategies=[strategy]).get_top_chunks("soru?", k=2)

    assert len(results) == 2
