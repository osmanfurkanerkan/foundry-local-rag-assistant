from abc import ABC, abstractmethod


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
