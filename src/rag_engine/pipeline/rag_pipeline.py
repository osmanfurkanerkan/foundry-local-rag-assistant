from collections.abc import Callable, Iterator

from rag_engine.interfaces.models import Chunk, ConversationTurn, RagAnswer
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

    def _prepare(self, question: str, history: list[ConversationTurn], k: int) -> tuple[str, list[Chunk]]:
        # Faz 3.1: takip sorusunu ("peki ya bu?" gibi) gecmise bakarak once
        # bagimsiz bir arama sorgusuna cevir, retrieval'i bununla yap; ama
        # modele gosterilen QUESTION hala kullanicinin orijinal ifadesi kalsin.
        search_query = rewrite_query(question, history, self._llm)
        chunks = self._retriever.get_top_chunks(search_query, k)
        prompt = build_prompt(question, chunks, history)
        return prompt, chunks

    @staticmethod
    def _sources_for(answer_text: str, chunks: list[Chunk]) -> list[str]:
        # Faz 3.2: model "bulamadim" derse chunk'lar alakasiz demektir --
        # o durumda sahte/yaniltici bir kaynak listesi gostermiyoruz.
        if NOT_FOUND_MESSAGE in answer_text:
            return []
        return sorted({chunk.source for chunk in chunks})

    def answer_query(self, question: str, history: list[ConversationTurn] | None = None, k: int = 3) -> RagAnswer:
        history = history or []
        prompt, chunks = self._prepare(question, history, k)
        answer_text = self._llm.generate(prompt)
        return RagAnswer(text=answer_text, sources=self._sources_for(answer_text, chunks))

    def answer_query_stream(
        self, question: str, history: list[ConversationTurn] | None = None, k: int = 3
    ) -> tuple[Iterator[str], Callable[[], list[str]]]:
        """Faz 3.3: cevabi tek seferde degil, parca parca (streaming) uretir.

        Bir (iterator, get_sources) cifti dondurur: iterator tuketildikce
        cevap metnini parca parca verir; get_sources ise iterator TAMAMEN
        tuketildikten sonra cagirilmali -- kaynak listesi (NOT_FOUND_MESSAGE
        kontrolu) ancak tam metin toplandiktan sonra belli olur.
        """
        history = history or []
        prompt, chunks = self._prepare(question, history, k)
        collected: list[str] = []

        def iterator() -> Iterator[str]:
            for piece in self._llm.generate_stream(prompt):
                collected.append(piece)
                yield piece

        def get_sources() -> list[str]:
            return self._sources_for("".join(collected), chunks)

        return iterator(), get_sources
