import subprocess
import tempfile
import os
from pathlib import Path
import sys

OUTPUT_DIR = Path("outputs/manim")
MANIM_EXE = Path(sys.executable).parent / "manim.exe"


def render_manim(code: str, segment_id: str) -> str | None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        suffix='.py',
        mode='w',
        encoding='utf-8',
        delete=False
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        print(f"    Rendu Manim segment {segment_id}...")

        result = subprocess.run([
            str(MANIM_EXE),
            tmp_path,
            'LessonAnimation',
            '--format', 'mp4',
            '--media_dir', str(OUTPUT_DIR),
            '-q', 'm',
            '--disable_caching'
        ],
        capture_output=True,
        text=True,
        timeout=180
        )

        if result.returncode == 0:
            mp4_files = list(OUTPUT_DIR.rglob("*.mp4"))
            if mp4_files:
                output_path = OUTPUT_DIR / f"segment_{segment_id}.mp4"
                mp4_files[-1].rename(output_path)
                print(f"    Succès : {output_path}")
                return str(output_path)
            else:
                print("    Erreur : aucun mp4 trouvé")
                return None
        else:
            print("    Erreur Manim :")
            print(result.stderr[-500:])
            return None

    except subprocess.TimeoutExpired:
        print(f"    Timeout : segment {segment_id}")
        return None

    except Exception as e:
        print(f"    Exception : {e}")
        return None

    finally:
        os.unlink(tmp_path)


def render_all(timeline: list) -> list:
    timeline_enrichie = []

    for i, segment in enumerate(timeline):
        if segment["type"] == "manim":
            chemin = render_manim(
                segment["code_manim"],
                str(i)
            )
            segment["video_path"] = chemin
            segment["render_ok"] = chemin is not None

        timeline_enrichie.append(segment)

    return timeline_enrichie