from abc import ABC, abstractmethod

from rag_engine.interfaces.models import Chunk


class RetrievalStrategy(ABC):
    """Bir soru icin en alakali chunk'lari getiren stratejilerin soyut arayuzu.

    Dependency Inversion: RagPipeline bu arayuze bagli olur, hangi retrieval
    yonteminin (saf embedding, BM25, hybrid) kullanildigini bilmez.
    """

    @abstractmethod
    def get_top_chunks(self, query: str, k: int) -> list[Chunk]:
        """Verilen soru icin en alakali k chunk'i, alakaliliga gore siralanmis dondurur."""
        raise NotImplementedError
