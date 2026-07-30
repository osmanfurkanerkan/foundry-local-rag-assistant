from collections.abc import Iterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from rag_engine.config import FOUNDRY_BASE_URL, FOUNDRY_MODEL_ALIAS
from rag_engine.llm.base import LLMProvider


class LangchainFoundryProvider(LLMProvider):
    """LLMProvider'in LangChain uzerinden calisan implementasyonu (Faz 4.1).

    Foundry Local zaten OpenAI-uyumlu bir REST servisi calistirdigi icin
    custom bir LangChain LLM sinifi yazmaya gerek yok -- standart
    `ChatOpenAI`, `base_url` override edilerek dogrudan kullanilabiliyor.
    Generate/prompt adimi bir LCEL zinciri (prompt | llm | output_parser)
    olarak kuruluyor; RagPipeline zaten hazir prompt metnini verdigi icin
    burada tek degiskenli, gecirmeli (pass-through) bir prompt template
    yeterli.
    """

    def __init__(self, base_url: str = FOUNDRY_BASE_URL, model_alias: str = FOUNDRY_MODEL_ALIAS):
        llm = ChatOpenAI(base_url=base_url, api_key="not-needed", model=model_alias)
        prompt = ChatPromptTemplate.from_template("{prompt}")
        self._chain = prompt | llm | StrOutputParser()

    def generate(self, prompt: str) -> str:
        return self._chain.invoke({"prompt": prompt})

    def generate_stream(self, prompt: str) -> Iterator[str]:
        yield from self._chain.stream({"prompt": prompt})
