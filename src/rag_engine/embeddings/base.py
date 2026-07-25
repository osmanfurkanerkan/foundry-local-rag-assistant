from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Metinleri sayi vektorlerine (embedding) ceviren soyut arayuz.

    Dependency Inversion: vectorstore ve pipeline bu arayuze bagli olur,
    somut modele (Foundry Local, baska bir servis) degil.
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Her metin icin bir embedding vektoru dondurur (ayni sirada)."""
        raise NotImplementedError
