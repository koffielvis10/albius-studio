import whisper
import json

print("Chargement du modèle Whisper...")
model = whisper.load_model("base")
print("Modèle Whisper prêt.")

def transcribe_audio(audio_path: str) -> dict:
    
    result = model.transcribe(
        audio_path,
        language="fr",
        word_timestamps=True
    )
    
    segments = []
    for segment in result["segments"]:
        segments.append({
            "start": round(segment["start"], 2),
            "end": round(segment["end"], 2),
            "text": segment["text"].strip()
        })
    
    return {
        "texte_complet": result["text"],
        "segments": segments,
        "duree_totale": round(result["segments"][-1]["end"], 2)
    }


if __name__ == "__main__":
    resultat = transcribe_audio("test.mp3")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))