---
title: Albius Backend
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Albius Studio

> Transformer un cours enregistré à l'oral en vidéo pédagogique animée, pour aider les profs à produire du contenu en ligne.
>
> **Statut : projet arrêté.** Prototype fonctionnel, jamais intégré à la plateforme Albius. Le « pourquoi » est expliqué plus bas, et c'est la partie la plus intéressante du projet.

< Vidéo Demo : https://github.com/koffielvis10/albius-studio/issues/2 >

## Le contexte

**Albius** était une plateforme de cours en ligne pour les collégiens et lycéens de Côte d'Ivoire, lancée avec un ami. Elle partait d'un constat : il manque de professeurs.

Pour qu'une plateforme de cours existe, il faut des cours. Notre hypothèse : **le frein principal pour les profs est le temps et la compétence nécessaires pour produire des vidéos de qualité.** Albius Studio devait lever ce frein. Le prof enregistre son cours à l'oral (et/ou fournit sa fiche de cours), et l'outil génère une vidéo animée.

## Ce que fait le prototype

1. Le prof dépose l'enregistrement audio de son cours (par exemple un cours de maths).
2. L'audio est transcrit.
3. Un agent IA génère les scènes vidéo (Remotion) et les animations mathématiques (Manim).
4. La vidéo finale est rendue puis prévisualisée dans l'interface.

## Pourquoi le projet s'est arrêté

- **Les profs n'étaient pas enthousiastes.** En leur présentant le projet, nous n'avons pas obtenu l'adhésion attendue : la production de vidéos n'était pas leur vrai problème.
- **Les élèves nous ont montré que nous visions à côté.** En discutant avec eux, nous avons compris que le manque de profs n'était pas le problème à résoudre en premier. <!-- Préciser ici en une phrase ce que les élèves ont révélé -->
- **Nous avons donc arrêté Studio avant de l'intégrer**, plutôt que d'investir davantage dans une solution sans demande.

## Ce que j'en ai retenu

- **J'ai construit avant d'avoir validé le problème.** Ce prototype techniquement ambitieux (pipeline audio → vidéo, agent IA, double moteur de rendu) a été développé avant toute discussion structurée avec les utilisateurs. Quelques entretiens avec des profs et des élèves auraient suffi à changer de direction plus tôt.
- **Sur une plateforme à deux faces, il faut valider les deux faces.** Nous avons misé sur l'offre (les profs) sans avoir vérifié ce dont la demande (les élèves) avait réellement besoin.
- **Ces leçons ont donné [Philomath](#)**, le pivot qui a suivi : un tuteur IA socratique pour apprendre les maths en autonomie. Cette fois, j'ai commencé par interviewer 5 lycéens, puis rédigé un Opportunity Brief et un PRD, et seulement ensuite le code.

---

## Détails techniques

### Architecture

Monorepo en trois parties :

| Dossier          | Rôle                                                          | Stack                       |
| ---------------- | ------------------------------------------------------------- | --------------------------- |
| `backend/`       | API, transcription audio, agent IA, orchestration du rendu    | Python, FastAPI, Manim      |
| `render-server/` | Composition et rendu des vidéos                               | Remotion (TypeScript/React) |
| `frontend/`      | Interface utilisateur (upload audio, suivi, prévisualisation) | React, Vite                 |

**Choix d'hébergement :** le rendu vidéo est lourd (Manim, Remotion et ffmpeg, avec des jobs longs) et ne peut pas tourner en serverless. Le frontend est donc hébergé sur Vercel, et le backend ainsi que le render-server dans un Space Docker Hugging Face avec beaucoup de RAM.

### Lancer le projet en local

Prérequis : Python 3.10+, Node.js 18+, clés API Anthropic et OpenAI.

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # renseigner ANTHROPIC_API_KEY, OPENAI_API_KEY, FRONTEND_URL
uvicorn main:app --reload

# Render-server
cd render-server && npm install

# Frontend
cd frontend && npm install && npm run dev
```

### Déploiement

| Partie                        | Hébergeur                       | Notes                                                                                        |
| ----------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------- |
| `frontend/`                   | Vercel                          | Root Directory = `frontend`, framework Vite. Variable `VITE_API_URL` = URL du backend.        |
| `backend/` + `render-server/` | Hugging Face Space (SDK Docker) | `Dockerfile` à la racine (port 7860). Secrets : `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `FRONTEND_URL`, `PUBLIC_URL`. |

> L'en-tête YAML en haut de ce fichier sert uniquement au déploiement sur Hugging Face Spaces.
