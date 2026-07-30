"""Faz 5.3: Regresyon testleri icin ortak fixture'lar.

Testlerin buyuk cogunlugu gercek Foundry Local sunucusuna ihtiyac duymaz --
FakeLLM/FakeRetriever ile RagPipeline'in kendi mantigini (kaynak gosterme,
"bilmiyorum" davranisi, rewrite/expansion cagri sirasi vb.) izole test eder.
Bu, testlerin CI'da (Faz 6.4) sunucu olmadan da hizli calismasini saglar.
`integration` isaretli testler ise gercek sunucuya ihtiyac duyar; sunucu
calismiyorsa otomatik atlanir (bkz. `require_live_server`).
"""
import socket
from urllib.parse import urlparse

import pytest

from rag_engine.config import FOUNDRY_BASE_URL
from rag_engine.interfaces.models import Chunk
from rag_engine.llm.base import LLMProvider
from rag_engine.retrieval.base import RetrievalStrategy


class FakeLLM(LLMProvider):
    """Gercek Foundry Local'a gitmeden, onceden belirlenmis cevaplari sirayla dondurur."""

    def __init__(self, responses: list[str] | None = None, default: str = "fake answer"):
        self._responses = list(responses or [])
        self._default = default
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self._responses:
            return self._responses.pop(0)
        return self._default

    def generate_stream(self, prompt: str):
        for word in self.generate(prompt).split(" "):
            yield word + " "


class FakeRetriever(RetrievalStrategy):
    """Sabit bir chunk listesini, hangi query/k ile cagrildigini kaydederek dondurur."""

    def __init__(self, chunks: list[Chunk]):
        self._chunks = chunks
        self.calls: list[tuple[str, int]] = []

    def get_top_chunks(self, query: str, k: int) -> list[Chunk]:
        self.calls.append((query, k))
        return self._chunks[:k]


def make_chunk(source: str, text: str = "sample text", chunk_index: int = 0) -> Chunk:
    return Chunk(id=f"{source}::{chunk_index}", source=source, chunk_index=chunk_index, text=text)


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    return [make_chunk("doc-a", "Doc A hakkinda bilgi."), make_chunk("doc-b", "Doc B hakkinda bilgi.")]


def _server_is_reachable() -> bool:
    parsed = urlparse(FOUNDRY_BASE_URL)
    try:
        with socket.create_connection((parsed.hostname, parsed.port), timeout=1.0):
            return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def require_live_server():
    """`integration` testlerinin onkosulu -- Foundry Local calismiyorsa testi atlar."""
    if not _server_is_reachable():
        pytest.skip(f"Foundry Local sunucusuna ulasilamiyor ({FOUNDRY_BASE_URL}) -- integration testi atlandi.")
