from rag_engine.interfaces.models import ConversationTurn
from rag_engine.pipeline.query_expansion import expand_query
from rag_engine.pipeline.query_rewriter import rewrite_query
from tests.conftest import FakeLLM


def test_rewrite_query_skips_llm_call_when_history_is_empty():
    llm = FakeLLM()

    result = rewrite_query("soru?", [], llm)

    assert result == "soru?"
    assert llm.prompts == []  # gereksiz LLM cagrisi yapilmamali


def test_rewrite_query_calls_llm_when_history_present():
    llm = FakeLLM(responses=["standalone soru"])
    history = [ConversationTurn(question="onceki soru", answer="onceki cevap")]

    result = rewrite_query("peki ya bu?", history, llm)

    assert result == "standalone soru"
    assert len(llm.prompts) == 1
    assert "onceki soru" in llm.prompts[0]


def test_expand_query_always_calls_llm():
    llm = FakeLLM(responses=["genisletilmis soru"])

    result = expand_query("kisa soru", llm)

    assert result == "genisletilmis soru"
    assert len(llm.prompts) == 1
    assert "kisa soru" in llm.prompts[0]
