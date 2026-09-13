"""API FastAPI — débat Grok (pour) vs GPT (contre)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .debate import keys_missing_message, run_remaining
from .models import (
    Debate,
    DebateCreate,
    DebateCreateResponse,
    DebateResponse,
    DebateStatus,
)

# Charge .env depuis bot-debate/ si présent (ne jamais committer de secrets)
_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV)

app = FastAPI(
    title="Bot Debate API",
    description="Débat Grok (pour) vs GPT (contre) avec résumé neutre.",
    version="1.0.0",
)

# CORS ouvert pour Expo local (web / emulator / device sur LAN)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store en mémoire (OK pour le scaffold)
_STORE: Dict[str, Debate] = {}


def _to_response(d: Debate) -> DebateResponse:
    return DebateResponse(
        id=d.id,
        topic=d.topic,
        total_messages=d.total_messages,
        complexity=d.complexity,
        status=d.status,
        messages=d.messages,
        summary=d.summary,
        remaining_turns=d.remaining_turns,
        error=d.error,
    )


@app.get("/health")
def health():
    missing = keys_missing_message()
    return {
        "ok": missing is None,
        "keys_ready": missing is None,
        "detail": missing,
    }


@app.post("/debates", response_model=DebateCreateResponse, status_code=201)
def create_debate(body: DebateCreate):
    debate = Debate(
        topic=body.topic.strip(),
        total_messages=body.total_messages,
        complexity=body.complexity,
    )
    _STORE[debate.id] = debate
    return DebateCreateResponse(
        id=debate.id,
        topic=debate.topic,
        total_messages=debate.total_messages,
        complexity=debate.complexity,
        status=debate.status,
    )


@app.get("/debates/{debate_id}", response_model=DebateResponse)
def get_debate(debate_id: str):
    debate = _STORE.get(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail="Débat introuvable.")
    return _to_response(debate)


@app.post("/debates/{debate_id}/run", response_model=DebateResponse)
def run_debate(debate_id: str):
    debate = _STORE.get(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail="Débat introuvable.")

    missing = keys_missing_message()
    if missing:
        raise HTTPException(status_code=503, detail=missing)

    if debate.status == DebateStatus.COMPLETED:
        return _to_response(debate)

    if debate.status == DebateStatus.RUNNING:
        raise HTTPException(
            status_code=409, detail="Ce débat est déjà en cours d'exécution."
        )

    updated = run_remaining(debate)
    _STORE[debate_id] = updated

    if updated.status == DebateStatus.FAILED and updated.error:
        # Si c'est encore un problème de clés, 503 ; sinon renvoyer l'état failed
        if "API_KEY" in (updated.error or ""):
            raise HTTPException(status_code=503, detail=updated.error)
        return _to_response(updated)

    return _to_response(updated)


def main():
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api.app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
