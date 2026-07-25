from openai import OpenAI

from rag_engine.config import FOUNDRY_BASE_URL, FOUNDRY_EMBEDDING_MODEL_ALIAS
from rag_engine.embeddings.base import EmbeddingProvider


class FoundryLocalEmbedder(EmbeddingProvider):
    def __init__(self, base_url: str = FOUNDRY_BASE_URL, model_alias: str = FOUNDRY_EMBEDDING_MODEL_ALIAS):
        self._model_alias = model_alias
        self._client = OpenAI(base_url=base_url, api_key="not-needed")

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            response = self._client.embeddings.create(model=self._model_alias, input=text)
            vectors.append(response.data[0].embedding)
        return vectors
