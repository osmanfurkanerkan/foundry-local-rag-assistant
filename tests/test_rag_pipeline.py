from rag_engine.pipeline.prompt_builder import NOT_FOUND_MESSAGE
from rag_engine.pipeline.rag_pipeline import RagPipeline
from tests.conftest import FakeLLM, FakeRetriever
from tests.conftest import make_chunk as chunk


def test_answer_query_returns_sorted_unique_sources():
    retriever = FakeRetriever([chunk("doc-b"), chunk("doc-a"), chunk("doc-a", chunk_index=1)])
    llm = FakeLLM(responses=["Cevap metni."])

    answer = RagPipeline(retriever=retriever, llm=llm).answer_query("soru?")

    assert answer.text == "Cevap metni."
    assert answer.sources == ["doc-a", "doc-b"]


def test_answer_query_hides_sources_when_not_found():
    retriever = FakeRetriever([chunk("doc-a")])
    llm = FakeLLM(responses=[NOT_FOUND_MESSAGE])

    answer = RagPipeline(retriever=retriever, llm=llm).answer_query("alakasiz soru?")

    assert answer.sources == []


def test_answer_query_passes_k_through_to_retriever():
    retriever = FakeRetriever([chunk("doc-a")])
    llm = FakeLLM()

    RagPipeline(retriever=retriever, llm=llm).answer_query("soru?", k=7)

    assert retriever.calls[-1][1] == 7


def test_answer_query_stream_concatenates_pieces_and_reports_sources():
    retriever = FakeRetriever([chunk("doc-a")])
    llm = FakeLLM(responses=["merhaba dunya"])

    stream, get_sources = RagPipeline(retriever=retriever, llm=llm).answer_query_stream("soru?")
    collected = "".join(stream)

    assert collected.strip() == "merhaba dunya"
    assert get_sources() == ["doc-a"]


def test_query_expansion_only_runs_when_enabled():
    retriever = FakeRetriever([chunk("doc-a")])
    llm = FakeLLM()

    RagPipeline(retriever=retriever, llm=llm, use_query_expansion=False).answer_query("soru?")
    calls_without_expansion = len(llm.prompts)

    llm_with_expansion = FakeLLM()
    RagPipeline(retriever=retriever, llm=llm_with_expansion, use_query_expansion=True).answer_query("soru?")
    calls_with_expansion = len(llm_with_expansion.prompts)

    # Expansion acikken bir ekstra LLM cagrisi (expand_query) yapilmali.
    assert calls_with_expansion == calls_without_expansion + 1
