"""Faz 0.4: Embedding ve cosine similarity kavramini elle kesfetme.

Amac: Chroma gibi kutuphaneler bu isi bizim yerimize yapmadan once,
"vektor benzerligi" ne demek, gozle gorelim.

Onkosul: `foundry server start` calisiyor ve `qwen3-embedding-0.6b` inmis olmali.
"""
import sys
from pathlib import Path

import numpy as np
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from rag_engine.config import FOUNDRY_BASE_URL, FOUNDRY_EMBEDDING_MODEL_ALIAS

# 6 ornek cumle -- farkli konularda, boylece benzerlik farkini net gorebiliriz.
SENTENCES = [
    "Foundry Local, modelleri tamamen yerel bilgisayarda calistirir.",
    "RAG, cevap uretmeden once ilgili dokumanlari getirir.",
    "SQLite, tek dosyalik, sunucu gerektirmeyen bir veritabanidir.",
    "Kopekler sadik ve oyuncu hayvanlardir.",
    "Istanbul, Turkiye'nin en kalabalik sehridir.",
    "Embedding, metni anlamini koruyan bir sayi vektorune cevirir.",
]

QUERY = "Yerel bir dil modelini nasil calistiririm?"


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def embed(client: OpenAI, text: str) -> np.ndarray:
    response = client.embeddings.create(model=FOUNDRY_EMBEDDING_MODEL_ALIAS, input=text)
    return np.array(response.data[0].embedding)


if __name__ == "__main__":
    client = OpenAI(base_url=FOUNDRY_BASE_URL, api_key="not-needed")

    sentence_vectors = [embed(client, s) for s in SENTENCES]
    query_vector = embed(client, QUERY)

    scores = [cosine_similarity(query_vector, v) for v in sentence_vectors]
    ranked = sorted(zip(SENTENCES, scores), key=lambda pair: pair[1], reverse=True)

    print(f"Soru: {QUERY}\n")
    print("Benzerlige gore siralanmis cumleler:")
    for sentence, score in ranked:
        print(f"  {score:.4f}  {sentence}")
