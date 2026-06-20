import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import database
from .config import INDEX_PATH, TOP_K
from .retrieval import Retriever, build_index


class SearchRequest(BaseModel):
    query: str
    top_k: int = TOP_K


class ChatRequest(BaseModel):
    message: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not INDEX_PATH.exists():
        build_index()
    database.ensure_database()
    yield


app = FastAPI(title="AI Insight Assistant", version="1.0.0", lifespan=lifespan)

_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def search(request: SearchRequest):
    return {"results": _get_retriever().search(request.query, request.top_k)}


@app.post("/chat")
def chat(request: ChatRequest):
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not configured")
    from .agent import Assistant

    return {"answer": Assistant().run(request.message)}
