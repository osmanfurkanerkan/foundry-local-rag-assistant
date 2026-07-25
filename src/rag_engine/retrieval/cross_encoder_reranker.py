from sentence_transformers import CrossEncoder

from rag_engine.interfaces.models import Chunk
from rag_engine.retrieval.reranker_base import Reranker

DEFAULT_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker(Reranker):
    """Soru ve chunk'i birlikte modele vererek alakalilik skoru ureten cross-encoder reranker.

    Bi-encoder'lardan (embedding) farkli olarak soru ve chunk ayri ayri
    vektore cevrilmez; ikisi birlikte tek bir model cagrisina girer. Bu daha
    isabetlidir ama her chunk icin ayri bir model calistirmayi gerektirdiginden
    tum koleksiyonda degil, sadece kucuk bir aday listesinde kullanilir.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self._model = CrossEncoder(model_name)

    def rerank(self, query: str, chunks: list[Chunk], k: int) -> list[Chunk]:
        if not chunks:
            return []

        pairs = [(query, chunk.text) for chunk in chunks]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
        return [chunk for chunk, _score in ranked[:k]]
