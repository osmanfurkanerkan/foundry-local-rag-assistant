from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from rag_engine.ingestion.base import TextChunker
from rag_engine.interfaces.models import Chunk

HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]


class MarkdownChunker(TextChunker):
    """Once markdown basliklarina, sonra (gerekirse) paragraf sinirlarina gore boler.

    FixedSizeChunker'in aksine kelime sayisina degil, dokumanin dogal yapisina
    (baslik -> paragraf) bakar; bu sayede bir chunk nadiren bir cumleyi veya
    fikri ortadan keser. Her chunk'a, hangi baslik altinda oldugunu belirten
    kisa bir "baslik yolu" (orn. "Overview > Architecture") ekleniyor --
    boylece chunk baglamindan koparilsa bile hangi konuya ait oldugu belli olur.
    """

    def __init__(self, chunk_size: int = 1500, overlap: int = 200):
        self._header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)
        self._sub_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def chunk(self, source: str, text: str) -> list[Chunk]:
        sections = self._header_splitter.split_text(text)

        chunks: list[Chunk] = []
        chunk_index = 0
        for section in sections:
            heading_path = " > ".join(section.metadata.values())
            section_text = f"{heading_path}\n{section.page_content}" if heading_path else section.page_content

            for piece in self._sub_splitter.split_text(section_text):
                if not piece.strip():
                    continue
                chunks.append(
                    Chunk(
                        id=f"{source}::{chunk_index}",
                        source=source,
                        chunk_index=chunk_index,
                        text=piece,
                    )
                )
                chunk_index += 1

        return chunks
