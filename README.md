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

> Turn a recorded spoken lesson into an animated educational video, helping teachers create online learning content.
>
> **Status: Project discontinued.** Functional prototype, never integrated into the Albius platform. The reasons why are explained below, and they are the most valuable part of this project.

< Video Demo: https://github.com/koffielvis10/albius-studio/issues/2 >

## Context

**Albius** was an online learning platform for middle and high school students in Côte d'Ivoire, launched with a friend. It was built around one observation: there is a shortage of teachers.

For an online learning platform to exist, it needs lessons. Our hypothesis was that **the main barrier for teachers was the time and expertise required to produce high-quality videos.** Albius Studio was designed to remove that barrier. Teachers could record their lessons orally and/or provide their written lesson notes, and the tool would generate an animated video.

## What the prototype does

1. The teacher uploads an audio recording of a lesson (e.g., a math lesson).
2. The audio is transcribed.
3. An AI agent generates video scenes using Remotion and mathematical animations using Manim.
4. The final video is rendered and displayed for preview in the interface.

## Why the project was discontinued

- **Teachers weren't enthusiastic.** When we presented the project to them, we didn't get the level of interest we had expected. Video production wasn't actually their main problem.
- **Students showed us we were solving the wrong problem.** Through conversations with them, we realized that making more accessible content available wasn't the solution to their actual needs. What they really needed was an available, patient teacher who encouraged them and used a teaching approach they could relate to.
- **We therefore stopped Studio before integrating it**, rather than investing further in a solution for which we hadn't validated demand.

## What I learned

- **I built before validating the problem.** This technically ambitious prototype—featuring an audio-to-video pipeline, an AI agent, and two rendering engines—was developed before any structured conversations with users. A few interviews with teachers and students could have helped us change direction much earlier.
- **On a two-sided platform, both sides need to be validated.** We focused on the supply side (teachers) without verifying what the demand side (students) actually needed.
- **These lessons led to [Philomath](#)**, the next iteration: an AI-powered Socratic tutor for independent math learning. This time, I started by interviewing five high school students, then wrote an Opportunity Brief and a PRD, and only then started coding.

---

## Technical Details

### Architecture

A monorepo organized into three components:

| Directory | Purpose | Tech Stack |
| --- | --- | --- |
| `backend/` | API, audio transcription, AI agent, rendering orchestration | Python, FastAPI, Manim |
| `render-server/` | Video composition and rendering | Remotion (TypeScript/React) |
| `frontend/` | User interface (audio upload, progress tracking, preview) | React, Vite |

**Hosting decisions:** Video rendering is resource-intensive (Manim, Remotion, and FFmpeg, with long-running jobs) and cannot run in a serverless environment. The frontend is therefore hosted on Vercel, while the backend and render server run in a Hugging Face Docker Space with ample RAM.

### Running the project locally

Requirements: Python 3.10+, Node.js 18+, Anthropic and OpenAI API keys.

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # Set ANTHROPIC_API_KEY, OPENAI_API_KEY, FRONTEND_URL
uvicorn main:app --reload

# Render server
cd render-server && npm install

# Frontend
cd frontend && npm install && npm run dev
```

### Deployment

| Component | Hosting Provider | Notes |
| --- | --- | --- |
| `frontend/` | Vercel | Root Directory = `frontend`, Vite framework. Set `VITE_API_URL` to the backend URL. |
| `backend/` + `render-server/` | Hugging Face Space (Docker SDK) | `Dockerfile` at the root (port 7860). Secrets: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `FRONTEND_URL`, `PUBLIC_URL`. |

