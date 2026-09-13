# Bot Debate — Grok vs GPT

Application mobile (Expo) + API FastAPI pour un débat structuré entre **Grok (xAI)** et **GPT (OpenAI gpt-4o-mini)**.

| Rôle | Modèle | Camp |
|------|--------|------|
| Grok | xAI (API chat completions) | **POUR** |
| GPT | OpenAI `gpt-4o-mini` | **CONTRE** |
| Résumé | OpenAI `gpt-4o-mini` | **Neutre** |

Protocole de bonne foi : pas de strawman, argumentation logique / scientifique / philosophique, concessions lorsque c’est justifié. UI en français.

## Structure

```
bot-debate/
  README.md
  .env.example
  requirements.txt
  grok.py              # helper xAI
  api/
    app.py             # FastAPI : CORS, POST/GET /debates, POST /debates/{id}/run
    debate.py          # orchestration des tours + résumé
    prompts.py
    models.py
  mobile/              # Expo SDK 52 (TypeScript)
  contexts/            # contextes texte (conservés)
  tools/               # outils agent (conservés)
```

## Prérequis

- Python 3.10+
- Node.js 18+ (pour Expo)
- Clés : `XAI_API_KEY`, `OPENAI_API_KEY` (**uniquement** côté backend)

## Backend

```bash
cd bot-debate
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# éditer .env avec vos vraies clés — ne jamais committer .env

# depuis bot-debate/
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints :

- `GET /health` — état des clés
- `POST /debates` — body `{ "topic", "total_messages" (pair 2–20), "complexity": "tout_public"|"intermediaire"|"expert" }`
- `GET /debates/{id}`
- `POST /debates/{id}/run` — exécute tous les tours restants + résumé  
  → **503** avec message clair si une clé API manque

CORS ouvert pour Expo local. Store en mémoire (suffisant pour le scaffold).

## Mobile (Expo)

```bash
cd bot-debate/mobile
npm install
npx expo start
```

Variable d’environnement :

| Environnement | `EXPO_PUBLIC_API_URL` |
|---------------|------------------------|
| iOS Simulator / web | `http://localhost:8000` (défaut) |
| **Android emulator** | `http://10.0.2.2:8000` |
| Device physique | `http://<IP-LAN-du-PC>:8000` |

Exemple Android :

```bash
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000 npx expo start --android
```

Parcours : **Setup** → **Transcript** (bulles distinctes Grok / GPT) → **Résumé** neutre.

## Sécurité

- Jamais de clés dans le client mobile ni dans git.
- Utiliser `.env` local (gitignoré) ; `.env.example` documente les variables.
- L’ancien fichier `env` du dépôt n’est qu’un exemple vide — préférer `.env` + `.env.example`.

## Test rapide API

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/debates \
  -H 'Content-Type: application/json' \
  -d '{"topic":"Le télétravail devrait être la norme","total_messages":4,"complexity":"tout_public"}'
# puis POST /debates/{id}/run
```
