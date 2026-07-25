from abc import ABC, abstractmethod

from rag_engine.interfaces.models import Chunk


class Reranker(ABC):
    """Bir aday chunk listesini, soruyla olan gercek alakaliligina gore yeniden siralayan soyut arayuz.

    Dependency Inversion: RerankingRetriever bu arayuze bagli olur, hangi
    reranking modelinin (cross-encoder, baska bir model) kullanildigini bilmez.
    """

    @abstractmethod
    def rerank(self, query: str, chunks: list[Chunk], k: int) -> list[Chunk]:
        """Verilen chunk'lari soruya gore yeniden siralayip en alakali k tanesini dondurur."""
        raise NotImplementedError
