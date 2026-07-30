"""Faz 5.2: Test soru setini (data/eval/test_questions.json) calistirip basit
"LLM-judge" metrikleri hesaplar ve data/eval/eval_report.md'ye yazar.

RAGAS yerine neden custom bir judge: ragas==0.4.3, langchain-community'nin
artik kaldirilmis bir alt modulune (chat_models.vertexai) sabit bir import
yapiyor; kurulumu, projenin kullandigi modern LangChain 1.x yiginini (Faz
4.1/4.3'un uzerine kuruldugu langchain-core/langgraph/langchain-openai 1.x)
0.3.x'e geriletmeyi gerektirdi -- bu, calisan agentic RAG ozelliklerini
bozacagi icin kabul edilebilir bir cozum degildi. Bunun yerine RAGAS'in
olcmeye calistigi ayni kavramlari (faithfulness, answer relevancy, retrieval
dogrulugu) kendi basit YES/NO "LLM-judge" promptlarimizla olcuyoruz. Ayrica
kucuk yerel modelin (phi-3.5-mini) yapisal/JSON ciktida daha once (Faz 1.5,
4.2) tutarsiz oldugunu gordugumuz icin, RAGAS'in bekledigi karmasik yapili
ciktilar yerine tek kelimelik YES/NO promptlari zaten daha guvenilir bir secim.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe scripts/run_evaluation.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.langchain_foundry_provider import LangchainFoundryProvider
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.bm25_retriever import BM25Retriever
from rag_engine.retrieval.cross_encoder_reranker import CrossEncoderReranker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.retrieval.hybrid_retriever import HybridRetriever
from rag_engine.retrieval.langchain_retriever_adapter import LangchainRetrieverAdapter
from rag_engine.retrieval.reranking_retriever import RerankingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

EVAL_SET_PATH = Path(__file__).resolve().parent.parent / "data" / "eval" / "test_questions.json"
REPORT_PATH = Path(__file__).resolve().parent.parent / "data" / "eval" / "eval_report.md"
K = 3

FAITHFULNESS_INSTRUCTION = (
    "You are checking if an answer is faithful to the given context -- i.e. every "
    "claim in the answer is supported by the context, with no invented information. "
    "Reply with ONLY the single word YES or NO."
)
RELEVANCY_INSTRUCTION = (
    "You are checking if an answer actually addresses the question asked (regardless "
    "of whether the answer is factually correct). Reply with ONLY the single word YES or NO."
)


def judge_yes_no(instruction: str, body: str, llm) -> bool:
    verdict = llm.generate(f"{instruction}\n\n{body}\n\nVERDICT (YES/NO):").strip().upper()
    return verdict.startswith("Y")


def evaluate_answerable(item: dict, answer, chunks, llm) -> dict:
    context = "\n\n".join(chunk.text for chunk in chunks)
    return {
        "id": item["id"],
        "question": item["question"],
        "expected_behavior": "answerable",
        "expected_source": item["expected_source"],
        "got_sources": answer.sources,
        "retrieval_hit": item["expected_source"] in answer.sources,
        "faithful": judge_yes_no(FAITHFULNESS_INSTRUCTION, f"CONTEXT:\n{context}\n\nANSWER:\n{answer.text}", llm),
        "relevant": judge_yes_no(RELEVANCY_INSTRUCTION, f"QUESTION: {item['question']}\n\nANSWER:\n{answer.text}", llm),
        "correct_refusal": None,
    }


def evaluate_unanswerable(item: dict, answer) -> dict:
    correct_refusal = not answer.sources and "could not find" in answer.text.lower()
    return {
        "id": item["id"],
        "question": item["question"],
        "expected_behavior": "unanswerable",
        "expected_source": None,
        "got_sources": answer.sources,
        "retrieval_hit": None,
        "faithful": None,
        "relevant": None,
        "correct_refusal": correct_refusal,
    }


def write_report(rows: list[dict]) -> None:
    answerable = [r for r in rows if r["expected_behavior"] == "answerable"]
    unanswerable = [r for r in rows if r["expected_behavior"] == "unanswerable"]

    retrieval_hit_rate = sum(r["retrieval_hit"] for r in answerable) / len(answerable)
    faithfulness_rate = sum(r["faithful"] for r in answerable) / len(answerable)
    relevancy_rate = sum(r["relevant"] for r in answerable) / len(answerable)
    refusal_rate = sum(r["correct_refusal"] for r in unanswerable) / len(unanswerable)

    lines = [
        "# Faz 5.2 -- Degerlendirme Raporu",
        "",
        f"Toplam soru: {len(rows)} ({len(answerable)} cevaplanabilir, {len(unanswerable)} cevaplanamaz)",
        "",
        "## Ozet Metrikler",
        "",
        f"- **Retrieval hit rate** (dogru kaynak top-{K}'ta bulundu mu): {retrieval_hit_rate:.0%}",
        f"- **Faithfulness** (cevap sadece context'e mi dayaniyor): {faithfulness_rate:.0%}",
        f"- **Answer relevancy** (cevap soruyu cevapliyor mu): {relevancy_rate:.0%}",
        f"- **Correct refusal rate** (cevaplanamaz sorularda dogru 'bulamadim' oranı): {refusal_rate:.0%}",
        "",
        "## Cevaplanabilir Sorular",
        "",
        "| id | soru | beklenen kaynak | bulunan kaynaklar | hit | faithful | relevant |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in answerable:
        lines.append(
            f"| {r['id']} | {r['question']} | {r['expected_source']} | {', '.join(r['got_sources']) or '(yok)'} "
            f"| {'OK' if r['retrieval_hit'] else 'MISS'} | {'YES' if r['faithful'] else 'NO'} "
            f"| {'YES' if r['relevant'] else 'NO'} |"
        )

    lines += [
        "",
        "## Cevaplanamaz Sorular",
        "",
        "| id | soru | bulunan kaynaklar | dogru 'bulamadim' mi |",
        "|---|---|---|---|",
    ]
    for r in unanswerable:
        lines.append(
            f"| {r['id']} | {r['question']} | {', '.join(r['got_sources']) or '(yok)'} "
            f"| {'OK' if r['correct_refusal'] else 'HATA'} |"
        )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nRapor yazildi: {REPORT_PATH}")


if __name__ == "__main__":
    with open(EVAL_SET_PATH, encoding="utf-8") as f:
        eval_set = json.load(f)

    vectorstore = ChromaVectorStore()
    embedding_retriever = EmbeddingRetriever(embedder=FoundryLocalEmbedder(), vectorstore=vectorstore)
    bm25_retriever = BM25Retriever(chunks=vectorstore.get_all_chunks())
    hybrid_retriever = HybridRetriever(strategies=[embedding_retriever, bm25_retriever])
    reranking_retriever = RerankingRetriever(base_strategy=hybrid_retriever, reranker=CrossEncoderReranker())
    langchain_retriever = LangchainRetrieverAdapter(strategy=reranking_retriever, k=K)
    llm = LangchainFoundryProvider()
    pipeline = RagPipeline(retriever=langchain_retriever, llm=llm)

    rows = []
    for item in eval_set:
        answer = pipeline.answer_query(item["question"], k=K)
        if item["expected_behavior"] == "answerable":
            chunks = langchain_retriever.get_top_chunks(item["question"], K)
            row = evaluate_answerable(item, answer, chunks, llm)
        else:
            row = evaluate_unanswerable(item, answer)
        rows.append(row)
        print(f"[{item['id']:>2}] {item['question'][:65]:<65} {row}")

    write_report(rows)
