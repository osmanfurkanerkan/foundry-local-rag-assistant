from rag_engine.interfaces.models import Chunk
from rag_engine.retrieval.base import RetrievalStrategy
from rag_engine.retrieval.reranker_base import Reranker


class RerankingRetriever(RetrievalStrategy):
    """Genis bir ilk arama yapip sonucu bir Reranker ile dar top-k'ya indirir.

    "Genis ara + dar suz" deseni: sarmalanan strateji (embedding/hybrid) hizli
    ama kaba bir aday listesi (fetch_k) cikarir; Reranker daha yavas ama cok
    daha isabetli bir modelle bu adaylari yeniden siralar. Decorator deseni --
    herhangi bir RetrievalStrategy, herhangi bir Reranker ile sarmalanabilir.
    """

    def __init__(self, base_strategy: RetrievalStrategy, reranker: Reranker, fetch_k: int = 10):
        self._base_strategy = base_strategy
        self._reranker = reranker
        self._fetch_k = fetch_k

    def get_top_chunks(self, query: str, k: int) -> list[Chunk]:
        candidates = self._base_strategy.get_top_chunks(query, self._fetch_k)
        return self._reranker.rerank(query, candidates, k)
