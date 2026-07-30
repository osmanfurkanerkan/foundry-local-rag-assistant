from rag_engine.interfaces.models import ConversationTurn
from rag_engine.llm.base import LLMProvider

REWRITE_INSTRUCTION = (
    "Given the conversation history and a follow-up question, rewrite the follow-up "
    "question into a standalone question that includes all context needed to search "
    "for it on its own (resolve pronouns like 'it'/'that' using the history). If the "
    "follow-up question is already standalone, return it unchanged. Reply with ONLY "
    "the rewritten question -- no explanation, no quotes."
)


def rewrite_query(question: str, history: list[ConversationTurn], llm: LLMProvider) -> str:
    """Takip sorusunu, konusma gecmisine bakarak bagimsiz bir arama sorgusuna cevirir.

    Faz 3.1'in basit query rewriting adimi. Gecmis bossa (ilk soru) rewriting
    atlanir -- gereksiz bir LLM cagrisi olurdu ve ilk soru zaten bagimsizdir.
    """
    if not history:
        return question

    history_text = "\n".join(f"Q: {turn.question}\nA: {turn.answer}" for turn in history)
    prompt = (
        f"{REWRITE_INSTRUCTION}\n\nHISTORY:\n{history_text}\n\n"
        f"FOLLOW-UP QUESTION: {question}\nSTANDALONE QUESTION:"
    )
    return llm.generate(prompt).strip()
