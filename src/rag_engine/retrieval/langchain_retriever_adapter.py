from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from rag_engine.retrieval.base import RetrievalStrategy


class LangchainRetrieverAdapter(BaseRetriever):
    """Kendi RetrievalStrategy'mizi LangChain'in BaseRetriever arayuzune sarar (Faz 4.1).

    Faz 2'de kurulan hybrid+rerank retrieval mantigi (`strategy`) hic
    degismeden, boylece hem RagPipeline (get_top_chunks ile, duck typing --
    RetrievalStrategy'den miras almasa da ayni imzayi tasiyor) hem de
    LangChain'in bekledigi her yerde (invoke/BaseRetriever ile) kullanilabilir.
    """

    strategy: RetrievalStrategy
    k: int = 3

    model_config = {"arbitrary_types_allowed": True}

    def _get_relevant_documents(self, query: str) -> list[Document]:
        chunks = self.strategy.get_top_chunks(query, self.k)
        return [
            Document(page_content=chunk.text, metadata={"source": chunk.source, "chunk_id": chunk.id})
            for chunk in chunks
        ]

    def get_top_chunks(self, query: str, k: int):
        # BaseRetriever.invoke() cagri basina k parametresi almadigi icin,
        # RagPipeline'in her cagirdiginda farkli k istemesi durumunda
        # sarilan strategy'ye dogrudan gidiyoruz (LangChain'in kendi
        # akisini bypass ediyor, ama kendi RetrievalStrategy sozlesmemizi
        # tam olarak koruyor).
        return self.strategy.get_top_chunks(query, k)
