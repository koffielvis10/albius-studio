---
title: Albius Backend
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Albius

> L'en-tête YAML ci-dessus sert uniquement au déploiement du backend sur Hugging Face Spaces (SDK Docker). Il est sans effet sur GitHub.

Albius transforme un enregistrement audio de cours (par ex. un cours de maths) en une vidéo pédagogique animée. L'audio est transcrit, un agent IA génère des composants vidéo (Remotion) et des animations mathématiques (Manim), puis la vidéo finale est rendue.

## Architecture

Le projet est un monorepo composé de trois parties :

| Dossier          | Rôle                                                                 | Stack                          |
| ---------------- | -------------------------------------------------------------------- | ------------------------------ |
| `backend/`       | API, transcription audio, agent IA, orchestration du rendu           | Python, FastAPI, Manim         |
| `render-server/` | Composition et rendu des vidéos                                      | Remotion (TypeScript/React)    |
| `frontend/`      | Interface utilisateur (upload audio, suivi, prévisualisation)        | React, Vite                    |

## Prérequis

- Python 3.10+
- Node.js 18+
- Clés API : Anthropic et OpenAI

## Installation

### Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
pip install -r requirements.txt   # ou installer les dépendances utilisées
cp .env.example .env              # puis renseigner vos clés API
```

Lancer l'API :

```bash
uvicorn main:app --reload
```

### Render-server

```bash
cd render-server
npm install
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Créez un fichier `backend/.env` à partir de `backend/.env.example` :

```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
FRONTEND_URL=http://localhost:5173
```

> ⚠️ Ne committez jamais le fichier `.env` : il contient vos clés API et est ignoré par Git.

## Déploiement

| Partie | Hébergeur | Notes |
| ------ | --------- | ----- |
| `frontend/` | **Vercel** | Root Directory = `frontend`, framework Vite. Variable `VITE_API_URL` = URL du backend. |
| `backend/` + `render-server/` | **Hugging Face Space** (SDK Docker) | Build via le `Dockerfile` à la racine (port 7860). Secrets à définir : `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `FRONTEND_URL`, `PUBLIC_URL`. |

Le backend fait du rendu vidéo lourd (Manim + Remotion + ffmpeg, jobs longs) : il ne peut pas tourner en serverless (Vercel), d'où un Space Docker avec beaucoup de RAM.

