from abc import ABC, abstractmethod

from rag_engine.interfaces.models import Chunk


class TextChunker(ABC):
    """Bir metni aramaya uygun kucuk parcalara (chunk) bolen soyut arayuz.

    Dependency Inversion / Open-Closed: pipeline bu arayuze bagli olur,
    somut stratejiye (sabit boyut, semantic, vb.) degil. Yeni bir chunking
    stratejisi eklemek icin bu arayuzu implemente eden yeni bir sinif
    yazmak yeterli, var olan kod degismez.
    """

    @abstractmethod
    def chunk(self, source: str, text: str) -> list[Chunk]:
        """Verilen metni, kaynagi belirtilmis Chunk nesnelerine boler."""
        raise NotImplementedError
