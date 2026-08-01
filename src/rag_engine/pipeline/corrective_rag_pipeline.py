"""Faz 4.3: Corrective RAG -- retrieval sonuclarini kendi kendine degerlendirip
yetersizse farkli bir stratejiyle (query expansion + daha buyuk k) tekrar deneyen,
LangGraph ile kurulmus dongusel/kosullu bir akis.

Sabit borulama (RagPipeline: retrieve -> prompt -> generate, hep tek seferde)
ile arasindaki fark: burada bir "grade" dugumu, bulunan chunk'larin soruyu
cevaplamaya yeterli olup olmadigina LLM ile karar veriyor; yetersizse bir onceki
Faz 4.2'de yazdigimiz query expansion'i "farkli strateji" olarak kullanip,
top-k'yi da buyuterek yeniden retrieval yapiyor.
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from rag_engine.interfaces.models import Chunk, ConversationTurn, RagAnswer
from rag_engine.llm.base import LLMProvider
from rag_engine.pipeline.prompt_builder import build_prompt, is_refusal
from rag_engine.pipeline.query_expansion import expand_query
from rag_engine.pipeline.query_rewriter import rewrite_query
from rag_engine.retrieval.base import RetrievalStrategy

# En fazla kac deneme yapilacagi (ilk deneme dahil) -- sinirsiz denemek hem
# gecikmeyi hem maliyeti katlar, bir noktada durup "bulamadim" demek gerekir.
MAX_ATTEMPTS = 2
K_INCREMENT = 2

GRADE_INSTRUCTION = (
    "You are grading whether the passages below contain enough information to "
    "answer the question. Reply with ONLY the single word YES or NO -- nothing else."
)


class CorrectiveRagState(TypedDict):
    question: str
    history: list[ConversationTurn]
    search_query: str
    k: int
    chunks: list[Chunk]
    attempts: int
    is_sufficient: bool
    answer_text: str
    sources: list[str]


def _grade_chunks(question: str, chunks: list[Chunk], llm: LLMProvider) -> bool:
    """Chunk'larin soruyu cevaplamaya yeterli olup olmadigina LLM ile karar verir."""
    if not chunks:
        return False
    context = "\n\n".join(f"[{chunk.source}]\n{chunk.text}" for chunk in chunks)
    prompt = f"{GRADE_INSTRUCTION}\n\nQUESTION: {question}\n\nPASSAGES:\n{context}\n\nRELEVANT (YES/NO):"
    verdict = llm.generate(prompt).strip().upper()
    return verdict.startswith("Y")


def build_corrective_rag_graph(retriever: RetrievalStrategy, llm: LLMProvider):
    """Rewrite -> retrieve -> grade -> (yeterli: generate) | (yetersiz: tekrar dene) akisini kurar."""

    def rewrite_node(state: CorrectiveRagState) -> dict:
        if state["attempts"] == 0:
            # Faz 3.1: ilk denemede takip sorusunu gecmise bakarak coz.
            search_query = rewrite_query(state["question"], state["history"], llm)
        else:
            # Faz 4.2: yetersiz kaldiginda "farkli bir strateji" olarak
            # sorguyu genislet.
            search_query = expand_query(state["search_query"], llm)
        return {"search_query": search_query}

    def retrieve_node(state: CorrectiveRagState) -> dict:
        chunks = retriever.get_top_chunks(state["search_query"], state["k"])
        return {"chunks": chunks}

    def grade_node(state: CorrectiveRagState) -> dict:
        return {"is_sufficient": _grade_chunks(state["question"], state["chunks"], llm)}

    def retry_or_generate(state: CorrectiveRagState) -> str:
        if state["is_sufficient"] or state["attempts"] + 1 >= MAX_ATTEMPTS:
            return "generate"
        return "retry"

    def bump_attempt_node(state: CorrectiveRagState) -> dict:
        return {"attempts": state["attempts"] + 1, "k": state["k"] + K_INCREMENT}

    def generate_node(state: CorrectiveRagState) -> dict:
        prompt = build_prompt(state["question"], state["chunks"], state["history"])
        answer_text = llm.generate(prompt)
        if is_refusal(answer_text):
            sources: list[str] = []
        else:
            sources = sorted({chunk.source for chunk in state["chunks"]})
        return {"answer_text": answer_text, "sources": sources}

    graph = StateGraph(CorrectiveRagState)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("bump_attempt", bump_attempt_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("rewrite")
    graph.add_edge("rewrite", "retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_conditional_edges("grade", retry_or_generate, {"generate": "generate", "retry": "bump_attempt"})
    graph.add_edge("bump_attempt", "rewrite")
    graph.add_edge("generate", END)

    return graph.compile()


class CorrectiveRagPipeline:
    """RagPipeline ile ayni RagAnswer sozlesmesini tasiyan, corrective (self-grading) versiyon."""

    def __init__(self, retriever: RetrievalStrategy, llm: LLMProvider):
        self._graph = build_corrective_rag_graph(retriever, llm)

    def answer_query(self, question: str, history: list[ConversationTurn] | None = None, k: int = 3) -> RagAnswer:
        initial_state: CorrectiveRagState = {
            "question": question,
            "history": history or [],
            "search_query": question,
            "k": k,
            "chunks": [],
            "attempts": 0,
            "is_sufficient": False,
            "answer_text": "",
            "sources": [],
        }
        final_state = self._graph.invoke(initial_state)
        return RagAnswer(text=final_state["answer_text"], sources=final_state["sources"])
