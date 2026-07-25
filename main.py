"""Faz 1.6: Terminalden soru-cevap dongusu -- projenin MVP giris noktasi.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/python.exe main.py
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from rag_engine.embeddings.foundry_local_embedder import FoundryLocalEmbedder
from rag_engine.llm.foundry_local_provider import FoundryLocalProvider
from rag_engine.pipeline.rag_pipeline import RagPipeline
from rag_engine.retrieval.retriever import Retriever
from rag_engine.vectorstore.chroma_vectorstore import ChromaVectorStore

EXIT_COMMANDS = {"exit", "quit", "q"}


def build_pipeline() -> RagPipeline:
    retriever = Retriever(embedder=FoundryLocalEmbedder(), vectorstore=ChromaVectorStore())
    return RagPipeline(retriever=retriever, llm=FoundryLocalProvider())


if __name__ == "__main__":
    pipeline = build_pipeline()

    print("Local RAG Assistant (Foundry Local + Foundry Local docs)")
    print("Cikmak icin 'exit' yaz.\n")

    while True:
        question = input("Soru: ").strip()
        if not question:
            continue
        if question.lower() in EXIT_COMMANDS:
            print("Gorusuruz.")
            break

        answer = pipeline.answer_query(question)
        print(f"\nCevap: {answer}\n")
