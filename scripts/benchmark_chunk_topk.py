"""Faz 2.4: Farkli chunk_size / top-k kombinasyonlarinin retrieval kalitesine
etkisini, elle etiketlenmis kucuk bir soru setiyle (hit rate) olcer.

Her soru icin "cevap hangi kaynak dokumanda olmali" onceden biliniyor; top-k
sonuclar arasinda o kaynak varsa "isabet" sayilir. Degiskenleri (chunk_size,
top-k) izole etmek icin hybrid/rerank karistirilmadan sadece saf embedding
retrieval kullanilir.

Kullanim: .venv/Scripts/python.exe scripts/benchmark_chunk_topk.py
"""
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.ingestion.cleaner import clean_text
from rag_engine.ingestion.loader import load_raw_documents
from rag_engine.ingestion.markdown_chunker import MarkdownChunker
from rag_engine.retrieval.embedding_retriever import EmbeddingRetriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
BENCH_DIR = Path(__file__).resolve().parent.parent / "chroma_db_bench"

# (soru, beklenen kaynak dokuman -- data/raw/<bu>.md)
EVAL_SET = [
    ("Foundry Local nedir?", "what-is-foundry-local"),
    ("Foundry Local'i nasil kurar ve calistiririm?", "get-started"),
    ("Foundry Local'in mimarisi nasil isliyor?", "foundry-local-architecture"),
    ("Foundry Local CLI komutlari nelerdir?", "reference-cli"),
    ("RAG nedir ve nasil calisir?", "retrieval-augmented-generation"),
    ("RAG cozumu tasarlarken nelere dikkat edilmeli?", "rag-solution-design-and-evaluation-guide"),
    ("Embedding kavrami nedir?", "understand-embeddings"),
    ("Azure OpenAI ile embedding nasil uretilir?", "embeddings"),
    ("Vektor arama icin embedding nasil olusturulur?", "vector-search-how-to-generate-embeddings"),
]

CONFIGS = [
    {"name": "kucuk chunk (800/100), k=3", "chunk_size": 800, "overlap": 100, "k": 3},
    {"name": "varsayilan (1500/200), k=3", "chunk_size": 1500, "overlap": 200, "k": 3},
    {"name": "varsayilan (1500/200), k=5", "chunk_size": 1500, "overlap": 200, "k": 5},
    {"name": "buyuk chunk (2500/300), k=3", "chunk_size": 2500, "overlap": 300, "k": 3},
]


def build_chunks(chunk_size: int, overlap: int):
    documents = load_raw_documents(RAW_DIR)
    chunker = MarkdownChunker(chunk_size=chunk_size, overlap=overlap)
    chunks = []
    for source, raw_text in documents:
        chunks.extend(chunker.chunk(source, clean_text(raw_text)))
    return chunks


def hit_rate(retriever: EmbeddingRetriever, k: int) -> float:
    hits = 0
    for question, expected_source in EVAL_SET:
        results = retriever.get_top_chunks(question, k)
        if any(chunk.source == expected_source for chunk in results):
            hits += 1
    return hits / len(EVAL_SET)


if __name__ == "__main__":
    embedder = FoundryLocalEmbedder()
    summary = []

    for i, config in enumerate(CONFIGS):
        # Windows'ta Chroma'nin dosya handle'i acikken silmek kilit hatasi
        # verdigi icin her config kendi alt-klasorunu kullanir; temizlik sonda.
        config_dir = BENCH_DIR / f"cfg_{i}"

        chunks = build_chunks(config["chunk_size"], config["overlap"])
        embeddings = embedder.embed([chunk.text for chunk in chunks])

        vectorstore = ChromaVectorStore(persist_dir=str(config_dir), collection_name="bench")
        vectorstore.add(chunks, embeddings)

        retriever = EmbeddingRetriever(embedder=embedder, vectorstore=vectorstore)
        rate = hit_rate(retriever, config["k"])
        summary.append((config["name"], len(chunks), rate))
        print(f"{config['name']}: {len(chunks)} chunk, hit rate = {rate:.0%}")

    try:
        shutil.rmtree(BENCH_DIR)
    except OSError:
        print(f"\n(Not: {BENCH_DIR} otomatik silinemedi, elle silebilirsin -- gitignore'da, zararsiz.)")

    print("\n--- Ozet ---")
    for name, chunk_count, rate in summary:
        print(f"{name}: {chunk_count} chunk, hit rate={rate:.0%}")
