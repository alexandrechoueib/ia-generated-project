"""Client utilitaire xAI (Grok) pour le débat.

Utilisé par l'API FastAPI. Les clés restent dans l'environnement backend.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx

XAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_GROK_MODEL = "grok-2-latest"


def _api_key() -> Optional[str]:
    return os.getenv("XAI_API_KEY") or None


def is_configured() -> bool:
    return bool(_api_key())


def grok(
    content: str,
    *,
    system: Optional[str] = None,
    model: str = DEFAULT_GROK_MODEL,
    history: Optional[list[dict]] = None,
) -> str:
    """Envoie un message (et un historique optionnel) à Grok via l'API OpenAI-compatible xAI."""
    key = _api_key()
    if not key:
        raise RuntimeError(
            "XAI_API_KEY manquante. Configurez-la dans l'environnement backend."
        )

    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": content})

    with httpx.Client(timeout=120.0) as client:
        response = client.post(
            f"{XAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    import sys

    prompt = " ".join(sys.argv[1:]) or "Bonjour"
    print(grok(prompt))
