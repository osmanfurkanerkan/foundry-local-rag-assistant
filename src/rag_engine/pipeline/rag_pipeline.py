from rag_engine.interfaces.models import ConversationTurn, RagAnswer
from rag_engine.llm.base import LLMProvider
from rag_engine.pipeline.prompt_builder import NOT_FOUND_MESSAGE, build_prompt
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

    def answer_query(self, question: str, history: list[ConversationTurn] | None = None, k: int = 3) -> RagAnswer:
        history = history or []
        # Faz 3.1: takip sorusunu ("peki ya bu?" gibi) gecmise bakarak once
        # bagimsiz bir arama sorgusuna cevir, retrieval'i bununla yap; ama
        # modele gosterilen QUESTION hala kullanicinin orijinal ifadesi kalsin.
        search_query = rewrite_query(question, history, self._llm)
        chunks = self._retriever.get_top_chunks(search_query, k)
        prompt = build_prompt(question, chunks, history)
        answer_text = self._llm.generate(prompt)

        # Faz 3.2: model "bulamadim" derse chunk'lar alakasiz demektir --
        # o durumda sahte/yaniltici bir kaynak listesi gostermiyoruz.
        if NOT_FOUND_MESSAGE in answer_text:
            sources: list[str] = []
        else:
            sources = sorted({chunk.source for chunk in chunks})

        return RagAnswer(text=answer_text, sources=sources)
