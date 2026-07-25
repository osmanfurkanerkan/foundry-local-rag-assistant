import os

# Foundry Local, her baslatildiginda farkli bir port secebilir.
# `foundry server status` ile ogrenilip burada override edilebilir.
FOUNDRY_BASE_URL = os.environ.get("FOUNDRY_BASE_URL", "http://127.0.0.1:58546/v1")
FOUNDRY_MODEL_ALIAS = os.environ.get("FOUNDRY_MODEL_ALIAS", "phi-3.5-mini")
