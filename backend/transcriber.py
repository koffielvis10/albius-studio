import json
import os
from openai import OpenAI

# Utilise l'API OpenAI Whisper (pas de modèle local -> hébergement léger).
# La clé est lue depuis la variable d'env OPENAI_API_KEY.
client = OpenAI()

# Limite de taille de l'API Whisper (25 Mo).
MAX_BYTES = 25 * 1024 * 1024


def transcribe_audio(audio_path: str) -> dict:
    taille = os.path.getsize(audio_path)
    if taille > MAX_BYTES:
        raise ValueError(
            f"Fichier audio trop volumineux ({taille // (1024*1024)} Mo). "
            f"Maximum {MAX_BYTES // (1024*1024)} Mo pour l'API Whisper."
        )

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="fr",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    segments = []
    for segment in (result.segments or []):
        segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
        })

    if segments:
        duree_totale = round(segments[-1]["end"], 2)
    else:
        duree_totale = round(getattr(result, "duration", 0.0), 2)

    return {
        "texte_complet": result.text,
        "segments": segments,
        "duree_totale": duree_totale,
    }


if __name__ == "__main__":
    resultat = transcribe_audio("test.mp3")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
