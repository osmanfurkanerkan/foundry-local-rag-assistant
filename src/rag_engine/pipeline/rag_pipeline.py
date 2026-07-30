from rag_engine.interfaces.models import ConversationTurn
from rag_engine.llm.base import LLMProvider
from rag_engine.pipeline.prompt_builder import build_prompt
from rag_engine.pipeline.query_rewriter import rewrite_query
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

    def answer_query(self, question: str, history: list[ConversationTurn] | None = None, k: int = 3) -> str:
        history = history or []
        # Faz 3.1: takip sorusunu ("peki ya bu?" gibi) gecmise bakarak once
        # bagimsiz bir arama sorgusuna cevir, retrieval'i bununla yap; ama
        # modele gosterilen QUESTION hala kullanicinin orijinal ifadesi kalsin.
        search_query = rewrite_query(question, history, self._llm)
        chunks = self._retriever.get_top_chunks(search_query, k)
        prompt = build_prompt(question, chunks, history)
        return self._llm.generate(prompt)
