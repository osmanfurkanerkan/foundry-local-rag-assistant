import os

# Foundry Local, her baslatildiginda farkli bir port secebilir.
# `foundry server status` ile ogrenilip burada override edilebilir.
FOUNDRY_BASE_URL = os.environ.get("FOUNDRY_BASE_URL", "http://127.0.0.1:52034/v1")
FOUNDRY_MODEL_ALIAS = os.environ.get("FOUNDRY_MODEL_ALIAS", "phi-3.5-mini")
FOUNDRY_EMBEDDING_MODEL_ALIAS = os.environ.get("FOUNDRY_EMBEDDING_MODEL_ALIAS", "qwen3-embedding-0.6b")

# ChromaDB (Faz 1.3): vektorlerin diskte kalici tutuldugu klasor ve koleksiyon adi.
CHROMA_DB_DIR = os.environ.get("CHROMA_DB_DIR", "chroma_db")
CHROMA_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME", "foundry_local_docs")
