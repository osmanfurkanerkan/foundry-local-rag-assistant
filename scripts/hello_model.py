"""Faz 0.3: FoundryLocalProvider uzerinden ilk 'hello model' testi.

Onkosul: `foundry server start` ile daemon calisiyor ve
`foundry model download phi-3.5-mini` ile model inmis olmali.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_engine.llm.foundry_local_provider import FoundryLocalProvider

if __name__ == "__main__":
    provider = FoundryLocalProvider()
    answer = provider.generate("Say hello in one short sentence.")
    print(answer)
