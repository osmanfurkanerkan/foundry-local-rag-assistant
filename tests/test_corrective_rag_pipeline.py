from rag_engine.pipeline.corrective_rag_pipeline import MAX_ATTEMPTS, CorrectiveRagPipeline
from tests.conftest import FakeLLM, FakeRetriever
from tests.conftest import make_chunk as chunk


def test_corrective_pipeline_generates_immediately_when_grade_is_sufficient():
    retriever = FakeRetriever([chunk("doc-a")])
    llm = FakeLLM(responses=["YES", "Final answer"])

    answer = CorrectiveRagPipeline(retriever=retriever, llm=llm).answer_query("soru?")

    assert answer.text == "Final answer"
    assert answer.sources == ["doc-a"]
    # Sadece 1 retrieval yapilmis olmali (retry tetiklenmemeli).
    assert len(retriever.calls) == 1


def test_corrective_pipeline_retries_then_falls_back_after_max_attempts():
    retriever = FakeRetriever([chunk("doc-a")])
    # grade -> NO, expand_query -> "genisletilmis soru", grade -> NO, generate -> cevap
    llm = FakeLLM(responses=["NO", "genisletilmis soru", "NO", "Nihai cevap"])

    answer = CorrectiveRagPipeline(retriever=retriever, llm=llm).answer_query("soru?", k=1)

    assert answer.text == "Nihai cevap"
    # MAX_ATTEMPTS kadar retrieval denemesi yapilmis olmali.
    assert len(retriever.calls) == MAX_ATTEMPTS
    # Ikinci denemede sorgu genisletilmis olmali.
    assert retriever.calls[1][0] == "genisletilmis soru"
