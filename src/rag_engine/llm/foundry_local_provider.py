from openai import OpenAI

from rag_engine.config import FOUNDRY_BASE_URL, FOUNDRY_MODEL_ALIAS
from rag_engine.llm.base import LLMProvider


class FoundryLocalProvider(LLMProvider):
    """LLMProvider'in Foundry Local implementasyonu.

    Foundry Local, yerelde OpenAI-uyumlu bir REST servisi calistirir
    (`foundry server start`). Bu sinif, standart `openai` client'ini
    o yerel endpoint'e yonlendirerek kullanir.
    """

    def __init__(self, base_url: str = FOUNDRY_BASE_URL, model_alias: str = FOUNDRY_MODEL_ALIAS):
        self._model_alias = model_alias
        self._client = OpenAI(base_url=base_url, api_key="not-needed")

    def generate(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model_alias,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
