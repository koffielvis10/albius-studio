from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import shutil
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from uuid import uuid4

from transcriber import transcribe_audio
from agent import orchestrer_remotion, chat_remotion, analyser_pour_plan, modifier_composant_existant
from renderer import render_video_local

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app):
    print("Pre-building Remotion bundle...")
    try:
        result = subprocess.run(
            "npx remotion bundle src/index.ts --bundle-cache",
            cwd=str(Path("../render-server").resolve()),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            timeout=120
        )
        if result.returncode == 0:
            print("Bundle Remotion prêt.")
        else:
            print(f"Warning bundle : {result.stderr[-300:]}")
    except Exception as e:
        print(f"Warning pre-build : {e}")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs/final")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/")
def root():
    return {"message": "Albius API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transcrire")
async def transcrire_cours(
    audio: UploadFile = File(...),
    niveau: str = Form(...),
    matiere: str = Form(...)
):
    try:
        audio_path = UPLOAD_DIR / f"{uuid4().hex[:8]}_{audio.filename}"
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        print(f"Audio sauvegardé : {audio_path}")

        print("Transcription Whisper en cours...")
        transcription = transcribe_audio(str(audio_path))
        print(f"Transcription : {len(transcription['segments'])} segments, {transcription['duree_totale']}s")

        return JSONResponse(content={
            "status": "success",
            "audio_filename": audio_path.name,
            "transcription": transcription,
            "niveau": niveau,
            "matiere": matiere,
            "duree_totale": transcription["duree_totale"]
        })

    except Exception as e:
        print(f"Erreur /transcrire : {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/analyser")
async def analyser_cours(payload: dict):
    try:
        transcription = payload.get("transcription")
        niveau        = payload.get("niveau")
        matiere       = payload.get("matiere")

        if not transcription:
            raise ValueError("transcription est requise")

        print("Analyse du plan pédagogique...")
        plan = analyser_pour_plan(transcription, niveau, matiere)

        return JSONResponse(content={"status": "success", "plan": plan})

    except Exception as e:
        print(f"Erreur /analyser : {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/generer")
async def generer_cours(payload: dict):
    try:
        transcription            = payload.get("transcription")
        annotations              = payload.get("annotations", [])
        niveau                   = payload.get("niveau")
        matiere                  = payload.get("matiere")
        historique_chat          = payload.get("historique_chat", [])
        audio_filename           = payload.get("audio_filename")
        plan_enrichi             = payload.get("plan_enrichi")
        composant_existant       = payload.get("composant_existant", "")
        instruction_modification = payload.get("instruction_modification", "")

        if not transcription or not audio_filename:
            raise ValueError("transcription et audio_filename sont requis")

        audio_path = UPLOAD_DIR / audio_filename
        if not audio_path.exists():
            raise FileNotFoundError(f"Fichier audio introuvable : {audio_filename}")

        if composant_existant and instruction_modification:
            print("Modification du composant existant...")
            composant_jsx = modifier_composant_existant(
                composant_jsx=composant_existant,
                instruction=instruction_modification,
                transcription=transcription,
                niveau=niveau,
                matiere=matiere
            )
            plan = {
                "composant_jsx": composant_jsx,
                "duree_totale": transcription["duree_totale"],
                "titre_cours": payload.get("titre_cours", ""),
            }
        else:
            print("Orchestration Remotion complète...")
            plan = orchestrer_remotion(
                transcription=transcription,
                annotations=annotations,
                historique_chat=historique_chat,
                niveau=niveau,
                matiere=matiere,
                plan_enrichi=plan_enrichi
            )

        print("Rendu Remotion CLI...")
        output_filename = f"{audio_path.stem}_final.mp4"
        video_path = render_video_local(
            composant_tsx=plan["composant_jsx"],
            audio_path=str(audio_path),
            output_filename=output_filename,
            duree_secondes=plan["duree_totale"],
            props={
                "audioUrl": "",
                "segments": transcription.get("segments", []),
                "titre": plan.get("titre_cours", ""),
                "matiere": matiere,
                "niveau": niveau
            }
        )

        nom_fichier = Path(video_path).name

        return JSONResponse(content={
            "status": "success",
            "plan": {k: v for k, v in plan.items() if k != "composant_jsx"},
            "composant_jsx": plan["composant_jsx"],
            "video_url": f"http://127.0.0.1:8000/outputs/final/{nom_fichier}"
        })

    except Exception as e:
        print(f"Erreur /generer : {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/chat")
async def chat_cours(payload: dict):
    try:
        message       = payload.get("message", "")
        transcription = payload.get("transcription")
        annotations   = payload.get("annotations", [])
        composant_jsx = payload.get("composant_jsx", "")
        historique    = payload.get("historique", [])
        niveau        = payload.get("niveau")
        matiere       = payload.get("matiere")

        if not transcription or not message:
            raise ValueError("transcription et message sont requis")

        result = chat_remotion(
            message, transcription, annotations,
            composant_jsx, historique, niveau, matiere
        )

        if result.get("regenerer"):
            result["instruction_modification"] = message

        return JSONResponse(content=result)

    except Exception as e:
        print(f"Erreur /chat : {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )