# Faz 6.3: RAG uygulamasini (FastAPI + web arayuzu) tek komutla ayaga
# kaldirilabilir bir container'a paketler.
#
# ONEMLI: Foundry Local (LLM + embedding runtime), Windows/Mac'e ozgu yerel bir
# servis oldugu icin bu container'in ICINE paketlenmiyor -- host makinede
# `foundry server start` calisiyor olmali. Container, FOUNDRY_BASE_URL ile
# host'un Foundry Local'ina ag uzerinden (host.docker.internal) baglanir.
FROM python:3.12-slim

WORKDIR /app

# Once sadece requirements.txt kopyalanip kurulur ki kod degisince
# Docker layer cache'i bozulmasin (pip install her seferinde tekrar calismaz).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py main.py ./
COPY src/ ./src/
COPY static/ ./static/

EXPOSE 8000

# Container icinde 127.0.0.1 yerine 0.0.0.0 dinlenmeli -- aksi halde
# container disindan gelen istekler ulasamaz.
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
