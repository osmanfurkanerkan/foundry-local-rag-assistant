"""Faz 6.1: RAG pipeline'ini bir HTTP API'sine donusturur.

Onkosul: `foundry server start` calisiyor, hem chat hem embedding modeli yuklu olmali.
Kullanim: .venv/Scripts/uvicorn.exe api:app --reload
Test: curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"What is Foundry Local?\"}"
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import build_pipeline
from rag_engine.interfaces.models import ConversationTurn
from rag_engine.pipeline.rag_pipeline import RagPipeline

_pipeline: RagPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pipeline (embedding modeli, vektor DB, LLM baglantisi) sadece bir kere,
    # sunucu ayaga kalkarken kuruluyor -- her istekte yeniden kurmak pahali olurdu.
    global _pipeline
    _pipeline = build_pipeline()
    yield


app = FastAPI(title="Local RAG Assistant API", lifespan=lifespan)


class HistoryTurnDto(BaseModel):
    question: str
    answer: str


class AskRequest(BaseModel):
    question: str
    history: list[HistoryTurnDto] = []


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question bos olamaz")

    history = [ConversationTurn(question=turn.question, answer=turn.answer) for turn in request.history]

    try:
        result = _pipeline.answer_query(question, history=history)
    except Exception as exc:
        # Foundry Local sunucusu kapaliysa vb. -- musteriye 500 yerine
        # "servis su an kullanilamiyor" anlamina gelen 503 donduruyoruz.
        raise HTTPException(status_code=503, detail=f"RAG pipeline hatasi: {exc}") from exc

    return AskResponse(answer=result.text, sources=result.sources)


# Faz 6.2: basit HTML/JS sohbet arayuzu -- /ask'tan SONRA mount edildigi icin
# API rotalari once eslesir, geri kalan her yol (orn. "/") static/index.html'e gider.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
