from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import subprocess
import sys
import os
import tempfile

MANIM_EXE = Path(sys.executable).parent / "manim.exe"
FFMPEG_EXE = "ffmpeg"
OUTPUT_DIR = Path("outputs/final")


def mixer_audio_video(audio_path: str, video_path: str, output_path: str) -> str:
    """
    Mixe la vidéo Manim avec l'audio du prof via FFmpeg.
    S'arrête sur la piste la plus courte (-shortest).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = subprocess.run([
        FFMPEG_EXE,
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-y",
        output_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("Erreur FFmpeg :", result.stderr[-500:])
        raise RuntimeError(f"FFmpeg a échoué (code {result.returncode})")

    print(f"Vidéo finale : {output_path}")
    return output_path


def creer_image_slide(slide_data: dict, width: int = 1920, height: int = 1080) -> np.ndarray:
    """Génère une image numpy pour une slide"""

    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)

    # Essayer de charger une police, sinon utiliser la police par défaut
    try:
        font_titre = ImageFont.truetype("arial.ttf", 72)
        font_point = ImageFont.truetype("arial.ttf", 48)
        font_exemple = ImageFont.truetype("arial.ttf", 38)
    except:
        font_titre = ImageFont.load_default()
        font_point = ImageFont.load_default()
        font_exemple = ImageFont.load_default()

    # Ligne décorative en haut
    draw.rectangle([80, 60, 400, 68], fill='#4fc3f7')

    # Titre
    titre = slide_data.get("titre", "")
    draw.text((80, 100), titre, fill='#ffffff', font=font_titre)

    # Ligne séparatrice
    draw.rectangle([80, 210, width - 80, 214], fill='#2a2a4e')

    # Points clés
    points = slide_data.get("points", [])
    y_pos = 260
    for point in points:
        # Puce colorée
        draw.ellipse([80, y_pos + 18, 104, y_pos + 42], fill='#4fc3f7')
        draw.text((130, y_pos), point, fill='#e0e0e0', font=font_point)
        y_pos += 90

    # Exemple ivoirien si présent
    exemple = slide_data.get("exemple_ivoirien", "")
    if exemple:
        draw.rectangle([80, height - 180, width - 80, height - 176], fill='#4fc3f7')
        draw.text((80, height - 160), f"💡 {exemple}", fill='#81c784', font=font_exemple)

    return np.array(img)


def image_to_video(img_array: np.ndarray, duration: float, output_path: str):
    """Convertit une image en clip vidéo de durée fixe via FFmpeg"""

    # Sauvegarder l'image temporairement
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        tmp_img = f.name

    Image.fromarray(img_array).save(tmp_img)

    subprocess.run([
        FFMPEG_EXE,
        '-loop', '1',
        '-i', tmp_img,
        '-c:v', 'libx264',
        '-t', str(duration),
        '-pix_fmt', 'yuv420p',
        '-vf', 'scale=1920:1080',
        '-y',
        output_path
    ], capture_output=True)

    os.unlink(tmp_img)


def composer_video_finale(
    audio_path: str,
    timeline: list,
    output_path: str = "outputs/final/cours_final.mp4"
) -> str:
    """
    Assemble la vidéo finale :
    - Audio du prof en continu
    - Slides et animations Manim synchronisées selon la timeline
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clips_paths = []

    print("Génération des clips visuels...")

    for i, segment in enumerate(timeline):
        duree = segment["timestamp_fin"] - segment["timestamp_debut"]
        clip_path = str(OUTPUT_DIR / f"clip_{i}.mp4")

        if segment["type"] == "slide":
            print(f"  Slide {i} ({duree:.1f}s)...")
            img = creer_image_slide(segment["contenu"])
            image_to_video(img, duree, clip_path)
            clips_paths.append(clip_path)

        elif segment["type"] == "manim":
            video_path = segment.get("video_path")
            if video_path and os.path.exists(video_path):
                print(f"  Animation Manim {i} ({duree:.1f}s)...")
                # Ajuster la durée de l'animation à celle du segment
                clip_ajuste = str(OUTPUT_DIR / f"clip_{i}_ajuste.mp4")
                subprocess.run([
                    FFMPEG_EXE,
                    '-i', video_path,
                    '-t', str(duree),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    clip_ajuste
                ], capture_output=True)
                clips_paths.append(clip_ajuste)
            else:
                # Fallback : slide si Manim a échoué
                print(f"  Fallback slide pour segment {i}...")
                img = creer_image_slide({
                    "titre": "Animation",
                    "points": ["Visualisation en cours..."]
                })
                image_to_video(img, duree, clip_path)
                clips_paths.append(clip_path)

    # Créer le fichier de liste pour FFmpeg
    print("Assemblage des clips...")
    liste_path = str(OUTPUT_DIR / "liste_clips.txt")
    with open(liste_path, 'w') as f:
        for clip in clips_paths:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    # Concaténer tous les clips en une vidéo muette
    video_muette = str(OUTPUT_DIR / "video_muette.mp4")
    subprocess.run([
        FFMPEG_EXE,
        '-f', 'concat',
        '-safe', '0',
        '-i', liste_path,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-y',
        video_muette
    ], capture_output=True)

    # Mixer la voix du prof avec la vidéo
    print("Mixage audio...")
    subprocess.run([
        FFMPEG_EXE,
        '-i', video_muette,
        '-i', audio_path,
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-y',
        output_path
    ], capture_output=True)
    # Nettoyage des fichiers temporaires
    for clip in clips_paths:
        if os.path.exists(clip):
            os.remove(clip)
    if os.path.exists(video_muette):
        os.remove(video_muette)
    if os.path.exists(liste_path):
        os.remove(liste_path)

    print(f"Vidéo finale : {output_path}")
    return output_path


if __name__ == "__main__":

    timeline_test = [
        {
            "timestamp_debut": 0.0,
            "timestamp_fin": 8.0,
            "type": "slide",
            "contenu": {
                "titre": "Le théorème de Pythagore",
                "points": [
                    "S'applique aux triangles rectangles",
                    "Relation entre les côtés",
                    "Formule : a² + b² = c²"
                ],
                "exemple_ivoirien": "Utilisé par les maçons à Abidjan"
            }
        },
        {
            "timestamp_debut": 8.0,
            "timestamp_fin": 20.0,
            "type": "slide",
            "contenu": {
                "titre": "Triangle rectangle",
                "points": [
                    "Angle de 90° présent",
                    "Hypoténuse = côté le plus long"
                ]
            }
        }
    ]

    resultat = composer_video_finale(
        audio_path=r"C:\Users\kouak\Downloads\Explication Ddf.ogg",
        timeline=timeline_test,
        output_path="outputs/final/test_composer.mp4"
    )

    print(f"\nRésultat : {resultat}")