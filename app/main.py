"""API local. Não disponibilizar sem autenticação/limites de acesso em ambiente público."""
from typing import Literal
from fastapi import FastAPI, HTTPException, Query as QueryParam
from pydantic import BaseModel, Field
from .core import OllamaError, load_chunks, response, retrieve

app = FastAPI(title="PassoLivre AI — Demo acadêmica local", version="0.2.0")


class Question(BaseModel):
    pergunta: str = Field(min_length=3, max_length=1000)
    modo: Literal["puro", "rag", "agente"] = "agente"


@app.get("/health")
def health():
    return {"status": "ok", "observacao": "Não testa a conectividade com Ollama"}


@app.get("/fontes")
def fontes():
    return [{k: c[k] for k in ("id", "titulo", "tipo", "url", "licenca", "referencia")}
            for c in load_chunks()]


@app.get("/buscar")
def buscar(q: str = QueryParam(min_length=3, max_length=1000), k: int = QueryParam(default=3, ge=1, le=10)):
    return retrieve(q, k=k)


@app.post("/perguntar")
def perguntar(payload: Question):
    try:
        return response(payload.pergunta, payload.modo)
    except OllamaError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
