from rank_bm25 import BM25Okapi

from rag_engine.interfaces.models import Chunk
from rag_engine.retrieval.base import RetrievalStrategy


class BM25Retriever(RetrievalStrategy):
    """Anahtar kelime (BM25) tabanli arama -- tum chunk'lari bellekte indexler.

    Embedding'in anlam bazli aramasinin aksine, BM25 sorgudaki kelimelerin
    chunk'ta tam olarak gecip gecmedigine bakar; ozel isim, kisaltma, kod gibi
    tam terim eslesmelerinde embedding'den daha guvenilir olabilir.
    """

    def __init__(self, chunks: list[Chunk]):
        self._chunks = chunks
        tokenized_corpus = [self._tokenize(chunk.text) for chunk in chunks]
        self._bm25 = BM25Okapi(tokenized_corpus)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return text.lower().split()

    def get_top_chunks(self, query: str, k: int) -> list[Chunk]:
        scores = self._bm25.get_scores(self._tokenize(query))
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self._chunks[i] for i in ranked_indices[:k]]
