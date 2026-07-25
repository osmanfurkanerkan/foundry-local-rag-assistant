from rag_engine.llm.base import LLMProvider
from rag_engine.pipeline.prompt_builder import build_prompt
from rag_engine.retrieval.base import RetrievalStrategy


class RagPipeline:
    """Retrieval + prompt olusturma + generate adimlarini birlestiren uctan uca RAG akisi.

    Dependency Inversion: RetrievalStrategy ve LLMProvider soyut arayuzlerine
    bagli, hangi retrieval yontemi / embedding modeli / vektor DB / LLM
    kullanildigini bilmez.
    """

    def __init__(self, retriever: RetrievalStrategy, llm: LLMProvider):
        self._retriever = retriever
        self._llm = llm

    def answer_query(self, question: str, k: int = 3) -> str:
        chunks = self._retriever.get_top_chunks(question, k)
        prompt = build_prompt(question, chunks)
        return self._llm.generate(prompt)
