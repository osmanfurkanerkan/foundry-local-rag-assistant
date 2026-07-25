import chromadb

from rag_engine.config import CHROMA_COLLECTION_NAME, CHROMA_DB_DIR
from rag_engine.interfaces.models import Chunk
from rag_engine.vectorstore.base import VectorStore


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_dir: str = CHROMA_DB_DIR, collection_name: str = CHROMA_COLLECTION_NAME):
        client = chromadb.PersistentClient(path=persist_dir)
        self._collection = client.get_or_create_collection(name=collection_name)

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        self._collection.add(
            ids=[chunk.id for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk.text for chunk in chunks],
            metadatas=[{"source": chunk.source, "chunk_index": chunk.chunk_index} for chunk in chunks],
        )

    def count(self) -> int:
        return self._collection.count()
