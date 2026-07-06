import subprocess
import json
import os
import shutil
from pathlib import Path

RENDER_SERVER_DIR = Path("../render-server")
OUTPUT_DIR = Path("outputs/final")
FFMPEG_EXE = "ffmpeg"

# Nombre de CPU disponibles pour la concurrence Remotion
CPU_COUNT = os.cpu_count() or 4


def valider_et_nettoyer_tsx(code: str) -> str:
    """Nettoie le code TSX généré par Claude"""

    # Supprimer les backticks
    if "```" in code:
        parties = code.split("```")
        for partie in parties:
            if "import" in partie and "remotion" in partie:
                code = partie
                if code.startswith(("tsx", "jsx", "javascript")):
                    code = code[code.index("\n")+1:]
                break

    code = code.strip()

    # Convertir les caractères Unicode en entités JSX
    # Les emojis et symboles mathématiques deviennent des
    # entités HTML numériques que React gère parfaitement
    import re

    def to_jsx_entity(match):
        char = match.group(0)
        codepoint = ord(char)
        return f"{{{codepoint}}}"  # JSX unicode escape

    # Convertir uniquement les caractères > ASCII (> 127)
    # qui sont hors du range Basic Multilingual Plane
    code = re.sub(
        r'[\U00010000-\U0010ffff]',  # emojis 4 octets
        lambda m: f"{{String.fromCodePoint({ord(m.group(0))})}}", 
        code
    )

    # Vérifications basiques
    if "export const LessonVideo" not in code:
        raise Exception("export const LessonVideo manquant")

    # Sauvegarder pour inspection
    debug_path = Path("debug_composant.tsx")
    debug_path.write_text(code, encoding="utf-8")
    print(f"Composant sauvegardé dans {debug_path}")

    return code

def render_video_local(
    composant_tsx: str,
    audio_path: str,
    output_filename: str,
    duree_secondes: float,
    props: dict,
    fps: int = 30,
    preview: bool = True  # True = 720p/24fps, False = 1080p/30fps
) -> str:
    """
    1. Écrit le composant TSX généré par Claude
    2. Lance Remotion CLI → vidéo muette
    3. FFmpeg mixe l'audio du prof avec la vidéo muette
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Résolution et FPS selon mode preview
    if preview:
        width, height, render_fps = 1280, 720, 24
        print("Mode preview : 1280x720 @ 24fps")
    else:
        width, height, render_fps = 1920, 1080, 30
        print("Mode export : 1920x1080 @ 30fps")

    # ── 1. Écrire le composant ──
    composant_tsx = valider_et_nettoyer_tsx(composant_tsx)
    lesson_path = RENDER_SERVER_DIR / "src" / "LessonVideo.tsx"
    lesson_path.write_text(composant_tsx, encoding="utf-8")

    # Props sans audio (mixé par FFmpeg après)
    props_sans_audio = {k: v for k, v in props.items() if k != "audioUrl"}
    props_sans_audio["audioUrl"] = ""
    props_path = RENDER_SERVER_DIR / "props.json"
    props_path.write_text(json.dumps(props_sans_audio), encoding="utf-8")

    output_path = OUTPUT_DIR / output_filename
    video_muette = OUTPUT_DIR / f"_silent_{output_filename}"
    duree_frames = int(duree_secondes * render_fps)

    print(f"Lancement Remotion render — {duree_frames} frames (vidéo muette)...")
    print(f"Concurrence : {CPU_COUNT} CPU")

    # ── 2. Rendu Remotion ──
    result = subprocess.run(
    f'npx remotion render src/index.ts LessonVideo'
    f' --output "{video_muette.resolve()}"'
    f' --props props.json'
    f' --frames 0-{duree_frames - 1}'
    f' --concurrency {CPU_COUNT}',
    cwd=str(RENDER_SERVER_DIR.resolve()),
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=1800,
    shell=True
    )

    if props_path.exists():
        props_path.unlink()

    print("=== Remotion stdout ===")
    print(result.stdout[-1000:] if result.stdout else "vide")
    print("=== Remotion stderr ===")
    print(result.stderr[-3000:] if result.stderr else "vide")

    if result.returncode != 0:
        raise Exception(f"Remotion render échoué (code {result.returncode})")

    print("Vidéo muette rendue :", video_muette)

    # ── 3. FFmpeg : mixer audio du prof + vidéo muette ──
    if audio_path and os.path.exists(audio_path):
        print("Mixage FFmpeg audio + vidéo...")
        mix = subprocess.run([
            FFMPEG_EXE,
            "-i", str(video_muette),
            "-i", audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            str(output_path)
        ], capture_output=True, text=True)

        if mix.returncode != 0:
            print("Erreur FFmpeg :", mix.stderr[-500:])
            shutil.move(str(video_muette), str(output_path))
        else:
            video_muette.unlink(missing_ok=True)
    else:
        shutil.move(str(video_muette), str(output_path))

    print(f"Vidéo finale : {output_path}")
    return str(output_path)