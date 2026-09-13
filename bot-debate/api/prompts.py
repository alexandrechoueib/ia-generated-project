"""Prompts de débat — protocole de bonne foi, rôles Grok (pour) / GPT (contre)."""

from __future__ import annotations

from .models import Complexity

COMPLEXITY_GUIDANCE = {
    Complexity.TOUT_PUBLIC: (
        "Adapte le niveau à un public général : vocabulaire accessible, "
        "exemples concrets, pas de jargon inutile."
    ),
    Complexity.INTERMEDIAIRE: (
        "Niveau intermédiaire : raisonnements structurés, notions techniques "
        "explicitées, références générales autorisées."
    ),
    Complexity.EXPERT: (
        "Niveau expert : argumentation dense, nuances, références "
        "scientifiques / philosophiques précises, vocabulaire spécialisé acceptable."
    ),
}

GOOD_FAITH_PROTOCOL = """
PROTOCOLE DE BONNE FOI (obligatoire) :
- Pas de strawman : représente fidèlement la position adverse avant de la critiquer.
- Argumentation logique, scientifique ou philosophique selon le sujet.
- Concède clairement lorsqu'un point adverse est solide.
- Pas d'attaques personnelles, pas de rhétorique purement émotionnelle.
- Reste sur le sujet ; une idée principale claire par message.
- Réponds en français.
""".strip()


def system_prompt_pour(topic: str, complexity: Complexity) -> str:
    return f"""Tu es Grok (xAI). Tu défends la position POUR sur le sujet suivant :
« {topic} »

{GOOD_FAITH_PROTOCOL}

Niveau : {complexity.value}
{COMPLEXITY_GUIDANCE[complexity]}

Tu es le premier à parler, puis tu alternes avec l'adversaire (GPT / contre).
Sois persuasif mais honnête. Si l'adversaire a raison sur un point, concède-le
avant de rebondir.
""".strip()


def system_prompt_contre(topic: str, complexity: Complexity) -> str:
    return f"""Tu es GPT (OpenAI). Tu défends la position CONTRE sur le sujet suivant :
« {topic} »

{GOOD_FAITH_PROTOCOL}

Niveau : {complexity.value}
{COMPLEXITY_GUIDANCE[complexity]}

Tu réponds après Grok (pour). Réfute ou nuance ses arguments sans les déformer.
Concède lorsque c'est justifié, puis avance tes meilleurs contre-arguments.
""".strip()


def user_turn_prompt(
    topic: str,
    turn_index: int,
    total: int,
    side: str,
    previous: list[tuple[str, str, str]],
) -> str:
    """previous: list of (speaker_label, side, content)."""
    if previous:
        history_block = "\n\n".join(
            f"[{speaker} — {s}] {text}" for speaker, s, text in previous
        )
    else:
        history_block = "(début du débat)"

    return f"""Sujet : {topic}
Tour {turn_index}/{total} — tu parles pour le camp « {side} ».

Historique du débat :
{history_block}

Produis UNIQUEMENT ton prochain message de débat (pas de méta-commentaire).
""".strip()


def summary_system_prompt() -> str:
    return """Tu es un modérateur neutre. Tu produis un résumé équilibré d'un débat
entre Grok (POUR) et GPT (CONTRE). Pas de parti pris. Réponds en français.
Structure :
1. Contexte / sujet
2. Arguments principaux POUR
3. Arguments principaux CONTRE
4. Points de convergence / concessions
5. Synthèse ouverte (sans départager de façon partisane)
""".strip()


def summary_user_prompt(topic: str, transcript: str) -> str:
    return f"""Sujet du débat : {topic}

Transcript :
{transcript}

Rédige le résumé neutre final.
""".strip()
