from transcriber import transcribe_audio
from agent import generer_composant_remotion
from renderer import render_video_local

AUDIO_PATH = r"C:\Users\kouak\Downloads\Explication Ddf.ogg"

# Étape 1 — Transcription
print("Transcription en cours...")
transcription = transcribe_audio(AUDIO_PATH)
print(f"Transcription OK — {len(transcription['segments'])} segments")

# Étape 2 — Génération du composant par Claude
print("Génération du composant Remotion par Claude...")
composant_tsx = generer_composant_remotion(
    transcription=transcription,
    annotations=[],
    niveau="Seconde",
    matiere="Mathématiques",
    audio_filename="Explication Ddf.ogg"
)
print("Composant généré — aperçu :")
print(composant_tsx[:300])

# Sauvegarder le composant pour inspection
with open("composant_genere.tsx", "w", encoding="utf-8") as f:
    f.write(composant_tsx)
print("Composant sauvegardé dans composant_genere.tsx")

# Étape 3 — Rendu Remotion
print("Rendu vidéo...")
props = {
    "audioUrl": "",
    "segments": transcription["segments"],
    "titre": "Ensemble de définition",
    "matiere": "Mathématiques",
    "niveau": "Seconde"
}

resultat = render_video_local(
    composant_tsx=composant_tsx,
    audio_path=AUDIO_PATH,
    output_filename="cours_complet.mp4",
    duree_secondes=transcription["duree_totale"],
    props=props
)

print(f"\nVidéo finale : {resultat}")