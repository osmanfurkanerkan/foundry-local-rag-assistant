from abc import ABC, abstractmethod

from rag_engine.interfaces.models import Chunk


class VectorStore(ABC):
    """Chunk'lari embedding'leriyle birlikte kalici olarak saklayan soyut arayuz.

    Dependency Inversion: pipeline bu arayuze bagli olur, somut vektor
    veritabanina (Chroma, baska bir DB) degil.
    """

    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Chunk'lari ve karsilik gelen embedding'lerini veritabanina yazar."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Veritabaninda kayitli toplam chunk sayisini dondurur."""
        raise NotImplementedError

    @abstractmethod
    def query(self, query_embedding: list[float], k: int) -> list[Chunk]:
        """Verilen embedding'e en yakin k chunk'i, benzerlige gore siralanmis dondurur."""
        raise NotImplementedError
