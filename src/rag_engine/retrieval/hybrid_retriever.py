from rag_engine.interfaces.models import Chunk
from rag_engine.retrieval.base import RetrievalStrategy

RRF_K = 60  # standart RRF sabiti; ust siralardaki farklarin agirligini dengeler


class HybridRetriever(RetrievalStrategy):
    """Birden fazla retrieval stratejisinin sonuclarini Reciprocal Rank Fusion (RRF) ile birlestirir.

    Her stratejiden ayri bir siralama alinir. Ham skorlar (BM25 vs cosine
    similarity) farkli olceklerde oldugu icin dogrudan toplanamaz; bunun
    yerine her sonucun sirasi (rank) kullanilir: score = 1 / (RRF_K + rank).
    Bir chunk birden fazla stratejide ust siralarda ciktiysa toplam skoru
    yukselir ve fused siralamada one gecer.
    """

    def __init__(self, strategies: list[RetrievalStrategy], fetch_k: int = 10):
        if not strategies:
            raise ValueError("en az bir retrieval stratejisi gerekli")
        self._strategies = strategies
        self._fetch_k = fetch_k

    def get_top_chunks(self, query: str, k: int) -> list[Chunk]:
        fused_scores: dict[str, float] = {}
        chunks_by_id: dict[str, Chunk] = {}

        for strategy in self._strategies:
            ranked_chunks = strategy.get_top_chunks(query, self._fetch_k)
            for rank, chunk in enumerate(ranked_chunks, start=1):
                fused_scores[chunk.id] = fused_scores.get(chunk.id, 0.0) + 1.0 / (RRF_K + rank)
                chunks_by_id[chunk.id] = chunk

        ranked_ids = sorted(fused_scores, key=lambda cid: fused_scores[cid], reverse=True)
        return [chunks_by_id[cid] for cid in ranked_ids[:k]]
