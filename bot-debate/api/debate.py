"""Orchestration du débat Grok (pour) vs GPT (contre) + résumé neutre."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from openai import OpenAI

# Permet d'importer grok.py depuis bot-debate/
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import grok as grok_client  # noqa: E402

from .models import Debate, DebateStatus, Message, Speaker
from . import prompts


OPENAI_MODEL = "gpt-4o-mini"


def openai_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def keys_missing_message() -> Optional[str]:
    missing = []
    if not grok_client.is_configured():
        missing.append("XAI_API_KEY")
    if not openai_configured():
        missing.append("OPENAI_API_KEY")
    if not missing:
        return None
    return (
        "Clés API manquantes côté serveur : "
        + ", ".join(missing)
        + ". Configurez-les dans l'environnement (voir .env.example) puis relancez l'API."
    )


def _openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY manquante.")
    return OpenAI(api_key=key)


def _gpt_chat(system: str, user: str) -> str:
    client = _openai_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def _history_tuples(debate: Debate) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    for m in debate.messages:
        if m.speaker == Speaker.SUMMARY:
            continue
        label = "Grok" if m.speaker == Speaker.GROK else "GPT"
        side = m.side or ("pour" if m.speaker == Speaker.GROK else "contre")
        out.append((label, side, m.content))
    return out


def run_remaining(debate: Debate) -> Debate:
    """Exécute tous les tours restants puis le résumé neutre."""
    missing = keys_missing_message()
    if missing:
        debate.status = DebateStatus.FAILED
        debate.error = missing
        return debate

    debate.status = DebateStatus.RUNNING
    debate.error = None

    try:
        spoken = sum(
            1 for m in debate.messages if m.speaker in (Speaker.GROK, Speaker.GPT)
        )

        while spoken < debate.total_messages:
            turn_index = spoken + 1  # 1-based
            # Odd turns = Grok (pour), even = GPT (contre)
            if turn_index % 2 == 1:
                speaker = Speaker.GROK
                side = "pour"
                system = prompts.system_prompt_pour(debate.topic, debate.complexity)
                user = prompts.user_turn_prompt(
                    debate.topic,
                    turn_index,
                    debate.total_messages,
                    side,
                    _history_tuples(debate),
                )
                content = grok_client.grok(user, system=system)
            else:
                speaker = Speaker.GPT
                side = "contre"
                system = prompts.system_prompt_contre(debate.topic, debate.complexity)
                user = prompts.user_turn_prompt(
                    debate.topic,
                    turn_index,
                    debate.total_messages,
                    side,
                    _history_tuples(debate),
                )
                content = _gpt_chat(system, user)

            debate.messages.append(
                Message(
                    index=turn_index,
                    speaker=speaker,
                    content=content,
                    side=side,  # type: ignore[arg-type]
                )
            )
            spoken += 1

        # Résumé neutre (OpenAI)
        transcript = "\n\n".join(
            f"[{m.speaker.value} — {m.side}] {m.content}"
            for m in debate.messages
            if m.speaker in (Speaker.GROK, Speaker.GPT)
        )
        summary = _gpt_chat(
            prompts.summary_system_prompt(),
            prompts.summary_user_prompt(debate.topic, transcript),
        )
        debate.summary = summary
        debate.messages.append(
            Message(
                index=len(debate.messages) + 1,
                speaker=Speaker.SUMMARY,
                content=summary,
                side="neutre",
            )
        )
        debate.status = DebateStatus.COMPLETED
    except Exception as exc:  # noqa: BLE001 — surface clear API error
        debate.status = DebateStatus.FAILED
        debate.error = f"Échec du débat : {exc}"

    return debate
