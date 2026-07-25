from rag_engine.embeddings.base import EmbeddingProvider
from rag_engine.interfaces.models import Chunk
from rag_engine.retrieval.base import RetrievalStrategy
from rag_engine.vectorstore.base import VectorStore


class EmbeddingRetriever(RetrievalStrategy):
    """Sorguyu embedding'e cevirip vektor benzerligine gore en alakali chunk'lari getirir.

    Dependency Inversion: somut FoundryLocalEmbedder / ChromaVectorStore'a
    degil, EmbeddingProvider / VectorStore soyut arayuzlerine bagli.
    """

    def __init__(self, embedder: EmbeddingProvider, vectorstore: VectorStore):
        self._embedder = embedder
        self._vectorstore = vectorstore

    def get_top_chunks(self, query: str, k: int = 3) -> list[Chunk]:
        query_embedding = self._embedder.embed([query])[0]
        return self._vectorstore.query(query_embedding, k)
