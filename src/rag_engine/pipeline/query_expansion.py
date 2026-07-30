from rag_engine.llm.base import LLMProvider

EXPANSION_INSTRUCTION = (
    "Rewrite the following search query to make it more effective for document "
    "retrieval. Expand vague references and abbreviations, spell out what the user "
    "likely means, and add relevant technical terms implied by the question -- but "
    "do not change its meaning or invent information not implied by the query. "
    "Reply with ONLY the rewritten query -- no explanation, no quotes."
)


def expand_query(query: str, llm: LLMProvider) -> str:
    """Kullanicinin (muhtemelen belirsiz/kotu ifade edilmis) sorgusunu, retrieval'dan
    once LLM ile daha aramaya elverisli bir sorguya cevirir (Faz 4.2).

    `query_rewriter.rewrite_query`'den farki: bu, konusma gecmisinden bagimsiz
    calisir -- ilk soru dahil her sorguya uygulanabilir, cunku amac takip
    sorusunu cozmek degil, herhangi bir sorgunun kendisini iyilestirmek.
    """
    prompt = f"{EXPANSION_INSTRUCTION}\n\nQUERY: {query}\nREWRITTEN QUERY:"
    return llm.generate(prompt).strip()
