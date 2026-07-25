from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """Bir kaynak dokumandan cikarilmis, aramaya uygun kucuk bir metin parcasi.

    Ingestion, embeddings, vectorstore ve retrieval paketleri arasinda
    paylasilan ortak veri tipi -- bu paketlerin birbirini dogrudan import
    etmesini onlemek icin burada, ayri bir yerde tutuluyor.
    """

    id: str
    source: str
    chunk_index: int
    text: str
