# Backend Albius : FastAPI + Manim (LaTeX) + Remotion (Chrome headless)
# Cible : Hugging Face Space (SDK docker, port 7860)
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# ── Dépendances système ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg \
    build-essential pkg-config \
    ffmpeg \
    # Manim : Cairo / Pango + LaTeX
    libcairo2-dev libpango1.0-dev \
    texlive texlive-latex-extra texlive-fonts-extra texlive-science dvisvgm \
    # Chrome headless (Remotion) : librairies système
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    libpango-1.0-0 libcairo2 libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Node.js 20 (Remotion) ──
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Utilisateur non-root (recommandé par HF Spaces) ──
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

# ── Dépendances Python (couche cache séparée) ──
COPY --chown=user backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt

# ── Dépendances Node du render-server (couche cache séparée) ──
COPY --chown=user render-server/package.json render-server/package-lock.json ./render-server/
RUN cd render-server && npm ci

# ── Code source ──
COPY --chown=user backend ./backend
COPY --chown=user render-server ./render-server

# Pré-télécharge le Chrome Headless Shell utilisé par Remotion
RUN cd render-server && npx remotion browser ensure || true

EXPOSE 7860
WORKDIR /home/user/app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
