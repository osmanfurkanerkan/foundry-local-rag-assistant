from abc import ABC, abstractmethod
from collections.abc import Iterator


class LLMProvider(ABC):
    """Bir dil modelinden metin uretimi icin soyut arayuz.

    Pipeline katmani (src/rag_engine/pipeline) bu arayuze bagimlidir,
    somut bir saglayiciya (ornegin FoundryLocalProvider) degil. Boylece
    ileride farkli bir LLM saglayicisi eklemek, mevcut kodu degistirmeden
    yeni bir sinif yazmak anlamina gelir (Dependency Inversion, Open/Closed).
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Verilen prompt icin modelden tek seferlik bir cevap uretir."""
        raise NotImplementedError

    @abstractmethod
    def generate_stream(self, prompt: str) -> Iterator[str]:
        """Verilen prompt icin modelden metni parca parca (streaming) uretir.

        Faz 3.3: CLI'nin cevabi kelime kelime canli yazdirabilmesi icin.
        """
        raise NotImplementedError
