from rag_engine.ingestion.base import TextChunker
from rag_engine.interfaces.models import Chunk


class FixedSizeChunker(TextChunker):
    """Metni sabit kelime sayisinda, ust uste binen (overlap) parcalara boler."""

    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        if overlap >= chunk_size:
            raise ValueError("overlap, chunk_size'dan kucuk olmali")
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, source: str, text: str) -> list[Chunk]:
        words = text.split()
        if not words:
            return []

        step = self._chunk_size - self._overlap
        chunks: list[Chunk] = []
        chunk_index = 0
        start = 0
        while start < len(words):
            end = start + self._chunk_size
            chunk_text = " ".join(words[start:end])
            chunks.append(
                Chunk(
                    id=f"{source}::{chunk_index}",
                    source=source,
                    chunk_index=chunk_index,
                    text=chunk_text,
                )
            )
            chunk_index += 1
            start += step

        return chunks
