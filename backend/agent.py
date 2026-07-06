import anthropic
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

anthropic_client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
ANALYSE_PROMPT = """
Tu es un expert en pédagogie ivoirienne et en production vidéo éducative.
On te donne la transcription d'un cours avec timestamps.

Tu dois analyser le cours et retourner un plan de production en JSON.

RÈGLES CRITIQUES DE DÉCOUPAGE :

1. Durée minimale par segment : 20 secondes
   - Si un segment fait moins de 20 secondes, fusionne-le avec le suivant
   - Ne crée JAMAIS de segment inférieur à 20 secondes

2. Choix du type — sois sélectif :
   - "slide" : introduction, définition, exemples, transitions, listes de propriétés
   - "manim" : UNIQUEMENT si le concept est IMPOSSIBLE à comprendre sans visualisation
     * Formule algébrique avec transformation visuelle
     * Construction géométrique étape par étape
     * Graphe de fonction avec tracé animé
     * NE PAS utiliser manim pour une simple définition ou un exemple textuel
   - En cas de doute → "slide"

3. Regroupement intelligent :
   - Regroupe les segments qui parlent du MÊME concept en un seul segment
   - Un segment = une idée complète
   - Évite de créer un nouveau segment juste parce que le prof fait une pause

4. Nombre de segments :
   - Pour un cours de moins de 5 minutes : maximum 6 segments
   - Pour un cours de 5 à 10 minutes : maximum 10 segments
   - Pour un cours de plus de 10 minutes : maximum 15 segments

Réponds UNIQUEMENT en JSON valide.

Format :
{
  "titre_cours": "...",
  "niveau": "...",
  "matiere": "...",
  "segments": [
    {
      "timestamp_debut": 0.0,
      "timestamp_fin": 45.0,
      "type": "slide",
      "texte_prof": "tout ce que dit le prof dans ce segment regroupé"
    }
  ]
}

EXEMPLES DE BON DÉCOUPAGE :

Transcription :
[0s-5s] "Bonjour"
[5s-12s] "Aujourd'hui nous allons voir les ensembles de définition"
[12s-30s] "Un ensemble de définition c'est l'ensemble des valeurs pour lesquelles une fonction est définie"
[30s-45s] "Autrement dit c'est toutes les valeurs de x que l'on peut mettre dans la fonction sans problème"

❌ MAUVAIS — trop de segments courts :
- Segment 1 : [0s-5s] "Bonjour" → slide
- Segment 2 : [5s-12s] "Aujourd'hui..." → slide
- Segment 3 : [12s-30s] "Un ensemble..." → slide
- Segment 4 : [30s-45s] "Autrement dit..." → slide

✅ BON — segments regroupés et cohérents :
- Segment 1 : [0s-45s] "Bonjour... ensemble de définition... valeurs de x..." → slide

AUTRE EXEMPLE :

Transcription :
[0s-20s] "L'ensemble de définition de f(x) = 1/x"
[20s-40s] "On ne peut pas diviser par zéro donc x ne peut pas valoir zéro"
[40s-65s] "Donc Df = R privé de zéro, c'est à dire tous les réels sauf zéro"
[65s-90s] "Sur la droite des réels, on enlève le point zéro"

✅ BON :
- Segment 1 : [0s-65s] "L'ensemble... diviser par zéro... Df = R privé de zéro" → slide
- Segment 2 : [65s-90s] "Sur la droite des réels..." → manim (visualisation de la droite réelle)
"""

SLIDE_PROMPT = """
Tu es un expert en design pédagogique pour des élèves ivoiriens.
On te donne ce que dit le prof dans un segment de cours.

Tu dois générer le contenu d'une slide claire et engageante.

RÈGLES IMPORTANTES :
- Titre court et percutant (maximum 6 mots)
- 2 à 4 points clés MAXIMUM — pas plus
- Chaque point = une idée simple et complète
- Langage adapté au niveau scolaire — pas de jargon
- Si le prof donne un exemple concret, inclus-le
- Utilise des exemples ivoiriens UNIQUEMENT si c'est naturel
  (ne force pas l'exemple ivoirien si ça ne s'y prête pas)
- Ne répète pas la même idée en plusieurs points
- Préfère 2 points bien formulés à 4 points redondants

Réponds UNIQUEMENT en JSON valide.

Format :
{
  "titre": "...",
  "points": ["...", "..."],
  "exemple_ivoirien": "..." ,
  "score_clarte": 8
}

EXEMPLE :

Texte prof : "L'ensemble de définition c'est l'ensemble des valeurs 
pour lesquelles la fonction est définie. Pour f(x) = 1/x, 
on ne peut pas mettre x=0 car on divise par zéro. 
Donc Df = R privé de zéro."

Résultat attendu :
{
  "titre": "Ensemble de définition",
  "points": [
    "Valeurs de x pour lesquelles f(x) existe",
    "Exclure les valeurs qui posent problème (division par 0, racine négative...)",
    "Pour f(x) = 1/x → Df = ℝ \\ {0}"
  ],
  "exemple_ivoirien": null,
  "score_clarte": 9
}
"""

MANIM_PROMPT = """
Tu es à la fois un expert Manim ET un motion designer pédagogique de haut niveau.
Tu maîtrises l'art de transmettre le savoir par le mouvement, la couleur et le timing.

QUAND UTILISER MANIM :
Manim est justifié UNIQUEMENT pour ces cas précis :
- Tracé de graphe de fonction (courbe qui se dessine progressivement)
- Construction géométrique étape par étape
- Transformation algébrique visuelle (équation qui évolue)
- Visualisation sur la droite des réels (intervalles, points exclus)
- Démonstration de théorème nécessitant un schéma animé

QUAND NE PAS UTILISER MANIM :
- Simple définition textuelle
- Liste de propriétés
- Exemple numérique sans visualisation
- Concept qui s'explique bien avec du texte

PRINCIPES DE MOTION DESIGN PÉDAGOGIQUE :

1. Révélation progressive
   - Ne montre jamais tout d'un coup
   - Fais apparaître les éléments dans l'ordre logique du raisonnement

2. Attention dirigée
   - Utilise Indicate() ou Circumscribe() pour attirer l'attention
   - L'élément important est toujours plus lumineux

3. Transformation plutôt qu'état final
   - Montre les transformations avec Transform() et ReplacementTransform()
   - Un concept qui se transforme visuellement reste gravé en mémoire

4. Rythme naturel
   - Alterne self.play() et self.wait()
   - Les moments importants méritent self.wait(1.5) ou plus

5. Du concret vers l'abstrait
   - Pars toujours d'un exemple concret avant la formule abstraite

PALETTE OBLIGATOIRE :
- Fond : #1a1a2e
- Concept principal : #4fc3f7
- Résultat : #81c784
- Accent/important : #ffb74d
- Formule finale : WHITE
- Secondaire : #b0bec5
- Erreur/exclusion : #ef5350

TECHNIQUES À UTILISER :
- FadeIn/FadeOut avec shift pour entrées dynamiques
- GrowFromCenter pour éléments importants
- DrawBorderThenFill pour formes géométriques
- Write pour textes et formules
- Indicate et Circumscribe pour mettre en valeur
- ReplacementTransform pour les évolutions
- NumberLine pour la droite des réels
- Axes pour les graphes de fonctions

EFFETS VISUELS SPÉCIAUX — à utiliser quand explicitement demandés :

ZOOM : zoomer sur un élément avec la caméra
  self.play(self.camera.animate.scale(0.5).move_to(objet), run_time=2)

ZOOM LENT : zoom progressif avec run_time élevé
  self.play(self.camera.animate.scale(0.4).move_to(objet), run_time=3.5)
  # Utiliser MovingCameraScene au lieu de Scene pour les zooms

3D : scène en trois dimensions
  # Utiliser ThreeDScene au lieu de Scene
  # self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
  # Objets : ThreeDAxes, Surface, ParametricCurve, Sphere, Cylinder
  # self.begin_ambient_camera_rotation(rate=0.1)

ROTATION : rotation animée d'un objet
  self.play(Rotate(objet, angle=PI, axis=OUT), run_time=2)
  self.play(Rotate(objet, angle=TAU, axis=UP, about_point=ORIGIN), run_time=3)

APPARITION PROGRESSIVE : révélation séquentielle avec lag_ratio
  self.play(AnimationGroup(*[FadeIn(el, shift=UP*0.3) for el in elements], lag_ratio=0.2))

FONDU : entrée et sortie en fondu
  self.play(FadeIn(objet, run_time=1.5))
  self.play(FadeOut(objet, run_time=1))

CONTRAINTES TECHNIQUES :
- Manim Community Edition v0.18+
- Classe nommée TOUJOURS "LessonAnimation"
- Pour ZOOM : hériter de MovingCameraScene
- Pour 3D : hériter de ThreeDScene
- Sinon : hériter de Scene
- Textes en français
- Durée totale proche de la durée du segment fourni
- Code Python valide sans erreurs de syntaxe
- Fond sombre obligatoire : self.camera.background_color = "#1a1a2e"

Réponds UNIQUEMENT avec le code Python, rien d'autre, pas d'explication.

EXEMPLE POUR ENSEMBLE DE DÉFINITION — DROITE RÉELLE :

Texte prof : "Df = R privé de zéro, on enlève le point zéro sur la droite réelle"
Durée : 20 secondes

```python
from manim import *

class LessonAnimation(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        COL_MAIN = "#4fc3f7"
        COL_RESULT = "#81c784"
        COL_ACCENT = "#ffb74d"
        COL_EXCLU = "#ef5350"

        # Titre
        titre = Text(
            "Df = ℝ \\ {0}",
            font_size=42,
            color=WHITE
        ).to_edge(UP, buff=0.8)
        self.play(Write(titre), run_time=1.5)
        self.wait(0.5)

        # Droite des réels
        droite = NumberLine(
            x_range=[-4, 4, 1],
            length=10,
            color=COL_MAIN,
            include_numbers=True,
            label_direction=DOWN
        )
        self.play(Create(droite), run_time=2)
        self.wait(0.5)

        # Point zéro exclu
        point_zero = Circle(
            radius=0.15,
            color=COL_EXCLU,
            fill_opacity=0
        ).move_to(droite.n2p(0))

        texte_exclu = Text(
            "exclu",
            font_size=24,
            color=COL_EXCLU
        ).next_to(point_zero, UP, buff=0.3)

        self.play(
            Create(point_zero),
            Write(texte_exclu),
            run_time=1.2
        )
        self.play(
            Indicate(point_zero, color=COL_EXCLU, scale_factor=1.5),
            run_time=1
        )
        self.wait(1)

        # Flèches des deux côtés
        fleche_gauche = Arrow(
            droite.n2p(-0.2),
            droite.n2p(-3.5),
            color=COL_RESULT,
            buff=0
        )
        fleche_droite = Arrow(
            droite.n2p(0.2),
            droite.n2p(3.5),
            color=COL_RESULT,
            buff=0
        )

        self.play(
            GrowArrow(fleche_gauche),
            GrowArrow(fleche_droite),
            run_time=1.5
        )

        conclusion = Text(
            "Tous les réels sauf 0",
            font_size=28,
            color=COL_RESULT
        ).to_edge(DOWN, buff=0.8)
        self.play(Write(conclusion), run_time=1)
        self.wait(1.5)
```

EXEMPLE POUR GRAPHE DE FONCTION :

Texte prof : "La fonction f(x) = x² est définie sur tout R"
Durée : 25 secondes

```python
from manim import *

class LessonAnimation(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        COL_MAIN = "#4fc3f7"
        COL_RESULT = "#81c784"

        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 1],
            axis_config={"color": "#b0bec5"},
            x_length=8,
            y_length=6
        )
        labels = axes.get_axis_labels(
            x_label="x",
            y_label="f(x)"
        )

        self.play(Create(axes), Write(labels), run_time=2)

        courbe = axes.plot(
            lambda x: x**2,
            color=COL_MAIN,
            x_range=[-3, 3]
        )

        formule = MathTex(
            "f(x) = x^2",
            color=WHITE,
            font_size=40
        ).to_corner(UR, buff=0.5)

        self.play(
            Create(courbe),
            Write(formule),
            run_time=2.5
        )
        self.wait(1)

        conclusion = Text(
            "Df = ℝ  (définie partout)",
            font_size=30,
            color=COL_RESULT
        ).to_edge(DOWN, buff=0.5)
        self.play(Write(conclusion), run_time=1)
        self.wait(1.5)
```
"""

def analyser_transcription(transcription: dict, niveau: str, matiere: str) -> dict:
    """Agent 1 — Analyse et découpe la transcription en segments typés"""

    segments_formates = "\n".join([
        f"[{seg['start']}s - {seg['end']}s] {seg['text']}"
        for seg in transcription["segments"]
    ])

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=ANALYSE_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
Matière: {matiere}
Niveau: {niveau}
Durée totale: {transcription['duree_totale']} secondes

Transcription:
{segments_formates}
            """
        }]
    )

    contenu = response.content[0].text.strip()
    
    # Afficher la réponse brute pour debug
    print("Réponse brute de Claude :")
    print(contenu[:200])
    
    # Nettoyer si Claude enveloppe dans des backticks
    if contenu.startswith("```"):
        contenu = contenu.split("```")[1]
        if contenu.startswith("json"):
            contenu = contenu[4:]
        contenu = contenu.strip()

    return json.loads(contenu)

def generer_slide(texte_prof: str, niveau: str, matiere: str) -> dict:
    """Agent 2a — Génère le contenu d'une slide via OpenAI"""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SLIDE_PROMPT},
            {"role": "user", "content": f"""
Matière: {matiere}
Niveau: {niveau}
Texte du prof: {texte_prof}
            """}
        ]
    )

    return json.loads(response.choices[0].message.content)

def generer_code_manim(texte_prof: str, duree: float, matiere: str) -> str:
    """Agent 2b — Génère le code Manim via Anthropic"""

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=MANIM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
Matière: {matiere}
Texte du prof: {texte_prof}
Durée du segment: {duree} secondes
            """
        }]
    )

    code = response.content[0].text
    # Nettoyer les backticks si Claude en ajoute
    code = code.replace("```python", "").replace("```", "").strip()
    return code


def orchestrer(transcription: dict, niveau: str, matiere: str) -> dict:
    """Orchestre les 3 agents et retourne le plan de production complet"""

    print("Étape 1 : Analyse de la transcription...")
    plan = analyser_transcription(transcription, niveau, matiere)

    print("Étape 2 : Génération du contenu...")
    timeline_enrichie = []

    for i, segment in enumerate(plan["segments"]):
        print(f"  Segment {i+1}/{len(plan['segments'])} — {segment['type']}")
        duree = segment["timestamp_fin"] - segment["timestamp_debut"]

        if segment["type"] == "slide":
            contenu = generer_slide(
                segment["texte_prof"],
                niveau,
                matiere
            )
            timeline_enrichie.append({
                "timestamp_debut": segment["timestamp_debut"],
                "timestamp_fin": segment["timestamp_fin"],
                "type": "slide",
                "contenu": contenu
            })

        elif segment["type"] == "manim":
            code = generer_code_manim(
                segment["texte_prof"],
                duree,
                matiere
            )
            timeline_enrichie.append({
                "timestamp_debut": segment["timestamp_debut"],
                "timestamp_fin": segment["timestamp_fin"],
                "type": "manim",
                "code_manim": code,
                "duree": duree
            })

    plan["timeline"] = timeline_enrichie
    print("Terminé !")
    return plan


CHAT_PROMPT = """
Tu es l'assistant IA d'Albius, une plateforme de génération de vidéos pédagogiques animées.
Tu aides l'utilisateur à affiner les annotations sur les segments de son cours.

Tu peux :
- Suggérer des modifications de tags (SLIDE, MANIM, ANIMATION) sur des segments spécifiques
- Recommander des effets visuels (ZOOM, 3D, ROTATION, APPARITION PROGRESSIVE, FONDU)
- Expliquer l'impact de chaque choix sur le rendu vidéo
- Proposer des descriptions d'animations Manim

Quand l'utilisateur demande de modifier des annotations, intègre les modifications dans ta réponse
entre des balises <annotations> et </annotations> au format JSON.
Le JSON doit contenir la liste COMPLÈTE des annotations avec les modifications appliquées.

Si aucune annotation n'est modifiée, ne retourne pas de balise <annotations>.

Réponds en français, de façon concise et utile.
"""


def orchestrer_avec_annotations(
    transcription: dict,
    annotations: list,
    instructions_chat: str,
    niveau: str,
    matiere: str
) -> dict:
    """Orchestre la génération en tenant compte des annotations utilisateur"""

    if not annotations:
        return orchestrer(transcription, niveau, matiere)

    segments = transcription["segments"]
    annotations_map = {a["segment_index"]: a for a in annotations}

    plan = {
        "titre_cours": f"Cours de {matiere} — {niveau}",
        "niveau": niveau,
        "matiere": matiere,
        "timeline": []
    }

    timeline_enrichie = []

    for i, segment in enumerate(segments):
        ann = annotations_map.get(i, {})
        tag = ann.get("tag", "SLIDE")
        type_seg = ann.get("type", "slide")
        description = ann.get("description", "")
        contenu_slide_user = ann.get("contenu_slide")
        effets = ann.get("effets", [])

        duree = segment["end"] - segment["start"]
        texte_prof = segment["text"]

        print(f"  Segment {i+1}/{len(segments)} — tag:{tag}")

        if type_seg == "slide":
            if contenu_slide_user and contenu_slide_user.get("titre"):
                contenu = contenu_slide_user
            else:
                prompt_enrichi = texte_prof
                if description:
                    prompt_enrichi += f"\n\nInstruction utilisateur: {description}"
                if instructions_chat:
                    prompt_enrichi += f"\nInstructions globales: {instructions_chat}"
                contenu = generer_slide(prompt_enrichi, niveau, matiere)

            timeline_enrichie.append({
                "timestamp_debut": segment["start"],
                "timestamp_fin": segment["end"],
                "type": "slide",
                "contenu": contenu
            })

        else:
            instructions_effets = []
            if tag == "ZOOM" or "ZOOM" in effets:
                instructions_effets.append("ZOOM: utilise MovingCameraScene, self.camera.animate.scale(0.5) avec run_time=2")
            if "ZOOM LENT" in effets:
                instructions_effets.append("ZOOM LENT: utilise MovingCameraScene, self.camera.animate.scale(0.4) avec run_time=3.5")
            if tag == "3D" or "3D" in effets:
                instructions_effets.append("3D OBLIGATOIRE: hériter de ThreeDScene, utiliser ThreeDAxes, set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)")
            if tag == "ROTATION" or "ROTATION" in effets:
                instructions_effets.append("ROTATION: utiliser Rotate(objet, angle=PI, axis=OUT)")
            if "APPARITION PROGRESSIVE" in effets:
                instructions_effets.append("APPARITION PROGRESSIVE: AnimationGroup avec FadeIn et lag_ratio=0.2")
            if "FONDU" in effets:
                instructions_effets.append("FONDU: FadeIn/FadeOut avec run_time élevé")

            contexte_manim = texte_prof
            if description:
                contexte_manim += f"\n\nVisualisation souhaitée: {description}"
            if instructions_effets:
                contexte_manim += "\n\nEffets OBLIGATOIRES:\n" + "\n".join(f"- {e}" for e in instructions_effets)
            if instructions_chat:
                contexte_manim += f"\n\nInstructions globales: {instructions_chat}"

            code = generer_code_manim(contexte_manim, duree, matiere)

            timeline_enrichie.append({
                "timestamp_debut": segment["start"],
                "timestamp_fin": segment["end"],
                "type": "manim",
                "code_manim": code,
                "duree": duree
            })

    plan["timeline"] = timeline_enrichie
    return plan


def chat_avec_annotations(
    transcription: dict,
    annotations: list,
    messages: list,
    user_message: str,
    niveau: str,
    matiere: str
) -> dict:
    """Répond au chat en pouvant modifier les annotations"""

    segments_formates = "\n".join([
        f"[Segment {i}] [{seg['start']}s - {seg['end']}s] {seg['text']}"
        for i, seg in enumerate(transcription["segments"])
    ])

    annotations_json = json.dumps(annotations, ensure_ascii=False, indent=2)

    contexte_initial = f"""Cours: {matiere} — {niveau}
Durée: {transcription.get('duree_totale', '?')} secondes

TRANSCRIPTION:
{segments_formates}

ANNOTATIONS ACTUELLES:
{annotations_json}"""

    historique = [
        {"role": "user", "content": contexte_initial},
        {"role": "assistant", "content": "Je suis prêt à t'aider à affiner les annotations de ton cours."}
    ]

    for msg in messages:
        historique.append({"role": msg["role"], "content": msg["content"]})

    historique.append({"role": "user", "content": user_message})

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=CHAT_PROMPT,
        messages=historique
    )

    response_text = response.content[0].text
    updated_annotations = annotations

    if "<annotations>" in response_text and "</annotations>" in response_text:
        try:
            start = response_text.index("<annotations>") + len("<annotations>")
            end = response_text.index("</annotations>")
            annotations_str = response_text[start:end].strip()
            updated_annotations = json.loads(annotations_str)
            response_text = response_text[:response_text.index("<annotations>")].strip()
        except Exception as e:
            print(f"Erreur parsing annotations chat: {e}")

    return {
        "response": response_text,
        "updated_annotations": updated_annotations
    }


# ═══════════════════════════════════════════════════════════════════
# NOUVELLE ARCHITECTURE — SCÈNE CONTINUE (style 3Blue1Brown)
# ═══════════════════════════════════════════════════════════════════

SCENE_ANALYSE_PROMPT = """
Tu es un expert en pédagogie et en animation mathématique (style 3Blue1Brown).
On te donne la transcription complète d'un cours avec timestamps, ainsi que les
annotations de l'utilisateur (effets visuels demandés, descriptions).

Analyse ce cours en profondeur et retourne UNIQUEMENT un JSON valide avec ce format :

{
  "titre_cours": "titre court et percutant",
  "sujet_central": "ce dont parle vraiment le cours en 1 phrase simple",
  "decor_base": "description du décor visuel persistant qui sera présent du début à la fin (ex: axes, triangle, titre en haut...)",
  "fil_conducteur": "ce qui relie visuellement tous les segments — l'élément qui évolue tout au long du cours",
  "segments_enrichis": [
    {
      "index": 0,
      "timestamp_debut": 0.0,
      "timestamp_fin": 20.0,
      "texte_prof": "ce que dit le prof dans ce segment",
      "elements_visuels": "description précise des éléments à afficher/animer dans ce segment",
      "transition_depuis_precedent": null,
      "elements_persistants": "ce qui reste à l'écran APRÈS ce segment pour servir d'ancre au suivant"
    }
  ]
}

PRINCIPES CLEFS :
- La scène ne se remet JAMAIS à zéro
- Chaque segment ENRICHIT la scène existante
- Pense à la progression visuelle : du vide vers le complet
- Le décor_base est établi dans les premiers segments et persiste
- Respecte les annotations utilisateur (effets ZOOM, 3D, ROTATION...)

Réponds UNIQUEMENT en JSON valide, sans aucun texte autour.
"""

SCENE_MANIM_PROMPT = """
Tu es un expert Manim Community Edition v0.18+ et un motion designer pédagogique (style 3Blue1Brown).

Tu dois générer UNE SEULE classe LessonAnimation qui couvre l'INTÉGRALITÉ du cours.
La scène est CONTINUE : elle évolue progressivement sans jamais se réinitialiser.

═══════════════════════════════════════════════════════════════════
PRINCIPE FONDAMENTAL — SCÈNE CONTINUE
═══════════════════════════════════════════════════════════════════
- Un décor de base est établi dès le début et PERSISTE
- Chaque segment ENRICHIT ce décor (nouvelles couches, transformations)
- Certains éléments restent comme fil conducteur visuel
- Les transitions sont fluides : animate.move_to(), ReplacementTransform, etc.
- PAS de FadeOut général entre segments — on TRANSFORME ou on AJOUTE
- Pense à un tableau noir qui se remplit progressivement

═══════════════════════════════════════════════════════════════════
SYNCHRONISATION TEMPORELLE OBLIGATOIRE
═══════════════════════════════════════════════════════════════════
- Marque chaque segment avec un commentaire : # ══ SEGMENT N [Xs → Ys] ══
- La somme (durée_animations + self.wait()) DOIT égaler (timestamp_fin - timestamp_debut)
- Calcule toujours la durée restante : self.wait(duree_segment - duree_animations)
- Exemple : segment de 30s avec 8s d'animations → self.wait(22)
- Ne dépasse JAMAIS la durée totale du cours

═══════════════════════════════════════════════════════════════════
PALETTE OBLIGATOIRE
═══════════════════════════════════════════════════════════════════
COL_MAIN   = "#4fc3f7"   # concept principal, axes, éléments centraux
COL_RESULT = "#81c784"   # résultats, conclusions, réponses
COL_ACCENT = "#ffb74d"   # éléments importants, formules clés, labels
COL_EXCLU  = "#ef5350"   # erreurs, exclusions, mises en garde
COL_SEC    = "#b0bec5"   # éléments secondaires, textes de contexte
Fond : "#1a1a2e"

═══════════════════════════════════════════════════════════════════
TECHNIQUES RECOMMANDÉES
═══════════════════════════════════════════════════════════════════
- Write / FadeIn(shift=UP*0.3) pour faire apparaître du texte
- Create / DrawBorderThenFill pour les formes géométriques
- objet.animate.move_to() / .scale() / .shift() pour déplacer
- ReplacementTransform pour les évolutions de formules
- Indicate / Circumscribe pour attirer l'attention sur un élément clé
- self.wait() pour les pauses pédagogiques importantes (min 1s)
- NumberLine pour la droite des réels, Axes pour les graphes

═══════════════════════════════════════════════════════════════════
EFFETS SPÉCIAUX (UNIQUEMENT si explicitement demandés)
═══════════════════════════════════════════════════════════════════
ZOOM : hériter de MovingCameraScene
  self.play(self.camera.animate.scale(0.5).move_to(cible), run_time=2)

ZOOM LENT : MovingCameraScene, run_time élevé
  self.play(self.camera.animate.scale(0.4).move_to(cible), run_time=3.5)

3D : hériter de ThreeDScene
  self.set_camera_orientation(phi=75*DEGREES, theta=-45*DEGREES)
  Utiliser ThreeDAxes, Surface, ParametricCurve, Sphere

ROTATION : self.play(Rotate(objet, angle=PI, axis=OUT), run_time=2)

APPARITION PROGRESSIVE : AnimationGroup avec lag_ratio
  self.play(AnimationGroup(*[FadeIn(el, shift=UP*0.2) for el in elements], lag_ratio=0.15))

FONDU : self.play(FadeIn(objet, run_time=1.5))

═══════════════════════════════════════════════════════════════════
CONTRAINTES TECHNIQUES
═══════════════════════════════════════════════════════════════════
- Classe nommée TOUJOURS "LessonAnimation"
- Pour ZOOM : hériter de MovingCameraScene
- Pour 3D : hériter de ThreeDScene
- Sinon : hériter de Scene
- self.camera.background_color = "#1a1a2e" en début de construct()
- Textes en français
- Code Python complet et valide, sans erreurs de syntaxe
- Durée totale ≈ durée_totale du cours (±2 secondes)

Réponds UNIQUEMENT avec le code Python brut. Aucun backtick, aucune explication.

═══════════════════════════════════════════════════════════════════
EXEMPLE DE SCÈNE CONTINUE — Pythagore (75 secondes)
═══════════════════════════════════════════════════════════════════

from manim import *

class LessonAnimation(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        COL_MAIN   = "#4fc3f7"
        COL_RESULT = "#81c784"
        COL_ACCENT = "#ffb74d"
        COL_EXCLU  = "#ef5350"
        COL_SEC    = "#b0bec5"

        # ══ SEGMENT 0 [0s → 20s] — Introduction ══
        # Durée : 20s | Animations : ~3s | Wait : 17s
        titre = Text("Théorème de Pythagore", font_size=48, color=COL_MAIN)
        sous_titre = Text("4ème — Mathématiques", font_size=24, color=COL_SEC).next_to(titre, DOWN, buff=0.3)

        self.play(Write(titre), run_time=2)
        self.play(FadeIn(sous_titre, shift=DOWN*0.2), run_time=1)
        self.wait(17)

        # ══ SEGMENT 1 [20s → 45s] — Triangle rectangle ══
        # Durée : 25s | Animations : ~5s | Wait : 20s
        # Transition : le titre monte, on dessine le triangle
        self.play(
            titre.animate.to_edge(UP, buff=0.4).scale(0.55),
            FadeOut(sous_titre),
            run_time=1.5
        )
        triangle = Polygon(
            [-2, -1.5, 0], [2, -1.5, 0], [-2, 1.5, 0],
            color=COL_MAIN, fill_color=COL_MAIN, fill_opacity=0.08, stroke_width=2.5
        )
        angle_droit = Square(0.35, color=COL_RESULT, stroke_width=2).move_to([-1.82, -1.32, 0])

        self.play(Create(triangle), run_time=2)
        self.play(Create(angle_droit), run_time=0.8)
        label_90 = Text("90°", font_size=22, color=COL_RESULT).next_to(angle_droit, UR, buff=0.1)
        self.play(FadeIn(label_90), run_time=0.7)
        self.wait(20)

        # ══ SEGMENT 2 [45s → 65s] — La formule a²+b²=c² ══
        # Durée : 20s | Animations : ~5.5s | Wait : 14.5s
        # Transition : on garde le triangle, on ajoute les labels et la formule
        label_a = Text("a", font_size=32, color=COL_ACCENT).move_to([-2.5, 0, 0])
        label_b = Text("b", font_size=32, color=COL_ACCENT).move_to([0, -1.9, 0])
        label_c = Text("c", font_size=32, color=COL_MAIN).move_to([0.4, 0.2, 0])

        self.play(
            AnimationGroup(FadeIn(label_a), FadeIn(label_b), FadeIn(label_c), lag_ratio=0.2),
            run_time=1.5
        )
        formule = MathTex("a^2 + b^2 = c^2", font_size=54, color=WHITE).to_edge(RIGHT, buff=1).shift(UP * 0.5)
        self.play(Write(formule), run_time=2.5)
        self.play(Circumscribe(formule, color=COL_ACCENT, buff=0.2), run_time=1.5)
        self.wait(14.5)

        # ══ SEGMENT 3 [65s → 75s] — Exemple numérique ══
        # Durée : 10s | Animations : ~3s | Wait : 7s
        exemple = MathTex("3^2 + 4^2 = 5^2", font_size=40, color=COL_RESULT).to_edge(RIGHT, buff=1).shift(DOWN * 0.8)
        calcul  = MathTex("9 + 16 = 25", font_size=32, color=COL_SEC).next_to(exemple, DOWN, buff=0.3)

        self.play(ReplacementTransform(formule.copy(), exemple), run_time=1.5)
        self.play(Write(calcul), run_time=1)
        conclusion = Text("✓ Vérifié !", font_size=28, color=COL_RESULT).next_to(calcul, DOWN, buff=0.4)
        self.play(FadeIn(conclusion, shift=UP*0.2), run_time=0.5)
        self.wait(7)
"""

CHAT_INTELLIGENT_PROMPT = """
Tu es l'assistant IA d'Albius, une plateforme de génération de vidéos pédagogiques animées.
Tu aides l'utilisateur à affiner sa vidéo. Tu as accès à la transcription complète,
aux annotations actuelles et au contexte de la conversation.

Tu réponds TOUJOURS de cette façon :
1. D'abord un message clair et concis en français (1-3 phrases)
2. Puis une balise <type> indiquant l'action à effectuer
3. Optionnellement des balises de données selon le type

LES 3 TYPES DE RÉPONSE :

TYPE "annotations" — modifications légères des annotations, pas de regénération :
  → Changer SLIDE ↔ MANIM sur des segments
  → Ajouter/enlever des effets visuels (ZOOM, 3D, ROTATION...)
  → Modifier les descriptions de segments
  → Répondre à une question (pas d'action)
  → Inclure <annotations>[JSON complet des annotations modifiées]</annotations>

TYPE "regenerer_segment" — refaire un segment spécifique visuellement :
  → L'utilisateur veut un changement visuel marqué sur UN segment
  → Ex: "rends le segment 3 plus dynamique", "mets une animation 3D au segment 2"
  → Inclure <segment_index>N</segment_index>
  → Inclure <annotations>[JSON si tu modifies aussi les annotations]</annotations>

TYPE "regenerer_tout" — refonte globale :
  → L'utilisateur veut tout refaire avec un style différent
  → Ex: "refais toute la vidéo avec plus d'animations", "change complètement le style"
  → Inclure <annotations>[JSON si tu modifies les annotations]</annotations>

FORMAT OBLIGATOIRE :
[ton message à l'utilisateur]
<type>annotations|regenerer_segment|regenerer_tout</type>
<annotations>[...]</annotations>     ← optionnel selon type
<segment_index>N</segment_index>     ← optionnel, si regenerer_segment

RÈGLES :
- En l'absence de vidéo (mode annotation), type="annotations" uniquement
- Sois proactif : si la demande est floue, choisis le type le plus conservateur
- Quand tu modifies des annotations, inclus TOUJOURS le JSON complet (tous les segments)
- Ne regenere que si vraiment nécessaire (c'est long)

Réponds en français.
"""


def analyser_cours_global(
    transcription: dict,
    annotations: list,
    historique_chat: list,
    niveau: str,
    matiere: str
) -> dict:
    """Phase 1 — Analyse globale du cours et planification du scénario visuel"""

    segments_formates = "\n".join([
        f"[Segment {i}] [{seg['start']}s → {seg['end']}s] {seg['text']}"
        for i, seg in enumerate(transcription["segments"])
    ])

    annotations_formates = "\n".join([
        f"Segment {ann['segment_index']}: tag={ann.get('tag','SLIDE')}, "
        f"effets={ann.get('effets',[])}, "
        f"description=\"{ann.get('description','')}\""
        for ann in annotations
    ]) if annotations else "Aucune annotation — l'IA choisit librement"

    historique_formate = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in historique_chat
    ]) if historique_chat else "Aucune instruction supplémentaire"

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SCENE_ANALYSE_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
Matière : {matiere}
Niveau : {niveau}
Durée totale : {transcription['duree_totale']} secondes

TRANSCRIPTION :
{segments_formates}

ANNOTATIONS UTILISATEUR :
{annotations_formates}

INSTRUCTIONS CHAT :
{historique_formate}
            """
        }]
    )

    contenu = response.content[0].text.strip()
    print("Analyse globale reçue :", contenu[:120])

    if contenu.startswith("```"):
        contenu = contenu.split("```")[1]
        if contenu.startswith("json"):
            contenu = contenu[4:]
        contenu = contenu.strip()

    return json.loads(contenu)


def generer_scene_continue(
    plan_enrichi: dict,
    transcription: dict,
    annotations: list,
    niveau: str,
    matiere: str
) -> str:
    """Phase 2 — Génération du code Manim d'une scène continue unique"""

    segments_detail = "\n".join([
        f"""
SEGMENT {seg['index']} [{seg['timestamp_debut']}s → {seg['timestamp_fin']}s] (durée : {seg['timestamp_fin'] - seg['timestamp_debut']:.1f}s)
Texte prof : {seg['texte_prof']}
Éléments visuels : {seg['elements_visuels']}
Transition depuis précédent : {seg.get('transition_depuis_precedent') or 'Début de la scène'}
Persistant après : {seg.get('elements_persistants', '')}"""
        for seg in plan_enrichi["segments_enrichis"]
    ])

    effets_par_segment = {}
    for ann in annotations:
        idx = ann.get("segment_index", 0)
        effets = ann.get("effets", [])
        description = ann.get("description", "")
        if effets or description:
            effets_par_segment[idx] = {"effets": effets, "description": description}

    effets_detail = "\n".join([
        f"Segment {idx} : effets=[{', '.join(data['effets'])}]"
        + (f" | description : {data['description']}" if data['description'] else "")
        for idx, data in effets_par_segment.items()
    ]) if effets_par_segment else "Aucun effet spécial demandé"

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SCENE_MANIM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
Matière : {matiere}
Niveau : {niveau}
Durée totale : {transcription['duree_totale']} secondes

SUJET : {plan_enrichi['sujet_central']}
DÉCOR DE BASE : {plan_enrichi['decor_base']}
FIL CONDUCTEUR : {plan_enrichi['fil_conducteur']}

SCÉNARIO PAR SEGMENT :
{segments_detail}

EFFETS SPÉCIAUX DEMANDÉS PAR SEGMENT :
{effets_detail}

Génère la classe LessonAnimation complète qui couvre exactement {transcription['duree_totale']} secondes.
"""
        }]
    )

    code = response.content[0].text
    code = code.replace("```python", "").replace("```", "").strip()
    return code


def orchestrer_scene(
    transcription: dict,
    annotations: list,
    historique_chat: list,
    niveau: str,
    matiere: str
) -> dict:
    """
    Orchestre la génération d'une scène Manim continue unique.
    Phase 1 : analyse globale → scénario enrichi
    Phase 2 : génération du code Manim complet
    """
    print("Phase 1 : Analyse globale du cours...")
    plan_enrichi = analyser_cours_global(
        transcription, annotations, historique_chat, niveau, matiere
    )

    print("Phase 2 : Génération du code Manim continu...")
    code_manim = generer_scene_continue(
        plan_enrichi, transcription, annotations, niveau, matiere
    )

    return {
        "titre_cours": plan_enrichi["titre_cours"],
        "niveau": niveau,
        "matiere": matiere,
        "sujet_central": plan_enrichi["sujet_central"],
        "code_manim": code_manim,
        "segments_enrichis": plan_enrichi["segments_enrichis"],
        "duree_totale": transcription["duree_totale"]
    }


def chat_intelligent(
    message: str,
    transcription: dict,
    annotations: list,
    _plan_actuel: dict,
    video_url: str,
    historique: list,
    niveau: str,
    matiere: str
) -> dict:
    """Chat contextuel — retourne type + message + annotations modifiées + segment_index"""

    segments_formates = "\n".join([
        f"[Segment {i}] [{seg['start']}s → {seg['end']}s] {seg['text']}"
        for i, seg in enumerate(transcription["segments"])
    ])
    annotations_json = json.dumps(annotations, ensure_ascii=False, indent=2)

    contexte_initial = f"""Cours : {matiere} — {niveau}
Durée : {transcription.get('duree_totale', '?')} secondes
Vidéo : {video_url or 'Pas encore générée'}

TRANSCRIPTION :
{segments_formates}

ANNOTATIONS ACTUELLES :
{annotations_json}"""

    historique_msgs = [
        {"role": "user",      "content": contexte_initial},
        {"role": "assistant", "content": "Je suis prêt à t'aider à affiner ta vidéo."}
    ]
    for msg in historique:
        historique_msgs.append({"role": msg["role"], "content": msg["content"]})
    historique_msgs.append({"role": "user", "content": message})

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=CHAT_INTELLIGENT_PROMPT,
        messages=historique_msgs
    )

    texte = response.content[0].text

    # Extraction du type
    result_type = "annotations"
    if "<type>" in texte and "</type>" in texte:
        s = texte.index("<type>") + len("<type>")
        e = texte.index("</type>")
        result_type = texte[s:e].strip()

    # Extraction des annotations modifiées
    annotations_modifiees = annotations
    if "<annotations>" in texte and "</annotations>" in texte:
        s = texte.index("<annotations>") + len("<annotations>")
        e = texte.index("</annotations>")
        try:
            annotations_modifiees = json.loads(texte[s:e].strip())
        except Exception as ex:
            print(f"Erreur parsing annotations chat : {ex}")

    # Extraction du segment_index
    segment_index = None
    if "<segment_index>" in texte and "</segment_index>" in texte:
        s = texte.index("<segment_index>") + len("<segment_index>")
        e = texte.index("</segment_index>")
        try:
            segment_index = int(texte[s:e].strip())
        except Exception:
            pass

    # Nettoyer le message (retirer tout ce qui est après le premier tag XML)
    reponse = texte
    for balise in ["<type>", "<annotations>", "<segment_index>"]:
        if balise in reponse:
            reponse = reponse[:reponse.index(balise)].strip()

    return {
        "type": result_type,
        "reponse": reponse,
        "annotations_modifiees": annotations_modifiees,
        "segment_index": segment_index
    }


# ═══════════════════════════════════════════════════════════════════
# REMOTION — Génération JSX (remplace Manim)
# ═══════════════════════════════════════════════════════════════════

REMOTION_PROMPT = """
Tu es un expert React, Remotion et motion design pédagogique.
Tu crées des vidéos pédagogiques animées dans le style 3Blue1Brown
adaptées aux élèves ivoiriens.

On te donne :
- La transcription complète du cours avec timestamps précis
- Un scénario visuel enrichi (décor_base, fil_conducteur, segments_enrichis)
- Les annotations de l'utilisateur (effets demandés, descriptions)
- La matière et le niveau scolaire
- L'URL de l'audio du prof

Tu dois générer UN composant React Remotion COMPLET et FONCTIONNEL.

═══════════════════════════════════════════════════════════════════
STRUCTURE OBLIGATOIRE
═══════════════════════════════════════════════════════════════════

```jsx
import { useCurrentFrame, useVideoConfig, interpolate,
         spring, Sequence, AbsoluteFill } from 'remotion'

// Composants de segment optionnels pour l'organisation
const Segment0 = () => {
  const frame = useCurrentFrame()    // frame LOCAL (Sequence le remet à 0)
  const { fps } = useVideoConfig()
  // ... animations
  return <AbsoluteFill>...</AbsoluteFill>
}

export const LessonVideo = () => {
  const { fps } = useVideoConfig()

  return (
    <AbsoluteFill style={{ background: '#1a1a2e', fontFamily: 'Segoe UI, sans-serif' }}>
      {/* L'audio est mixé par FFmpeg après le rendu — pas de composant Audio ici */}

      <Sequence from={0} durationInFrames={20 * fps}>
        <Segment0 />
      </Sequence>

      <Sequence from={20 * fps} durationInFrames={25 * fps}>
        {/* ... */}
      </Sequence>
    </AbsoluteFill>
  )
}
```

═══════════════════════════════════════════════════════════════════
ANIMATIONS REMOTION — TECHNIQUES CLÉS
═══════════════════════════════════════════════════════════════════

1. APPARITION DE TEXTE :
   const opacity = interpolate(frame, [0, fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })
   const y = interpolate(frame, [0, fps * 0.5], [30, 0], { extrapolateRight: 'clamp' })
   → <div style={{ opacity, transform: `translateY(${y}px)` }}>texte</div>

2. SPRING (rebond naturel) :
   const scale = spring({ frame, fps, config: { damping: 10, stiffness: 80 } })
   → <div style={{ transform: `scale(${scale})` }}>élément</div>

3. ZOOM caméra :
   const scale = interpolate(frame, [fps * 2, fps * 4], [1, 1.8], { extrapolateRight: 'clamp' })
   → sur AbsoluteFill : style={{ transform: `scale(${scale})`, transformOrigin: 'center' }}

4. ROTATION :
   const rotation = interpolate(frame, [0, fps * 2], [0, 360], { extrapolateRight: 'clamp' })
   → style={{ transform: `rotate(${rotation}deg)` }}

5. DESSIN SVG PROGRESSIF (strokeDashoffset) :
   const pathLength = 300
   const drawn = interpolate(frame, [0, fps * 2], [pathLength, 0], { extrapolateRight: 'clamp' })
   →  <path strokeDasharray={pathLength} strokeDashoffset={drawn} ... />

6. APPARITION PROGRESSIVE DE LISTE :
   {items.map((item, i) => {
     const itemOpacity = interpolate(frame, [i * 10, i * 10 + 20], [0, 1], { extrapolateRight: 'clamp' })
     return <p style={{ opacity: itemOpacity }} key={i}>{item}</p>
   })}

7. TRANSITION ENTRE SEGMENTS — Les éléments du segment précédent disparaissent,
   les nouveaux apparaissent. Dans chaque Sequence, frame commence à 0.

═══════════════════════════════════════════════════════════════════
FORMULES MATHÉMATIQUES
═══════════════════════════════════════════════════════════════════
Écris les formules directement en Unicode dans du JSX :
- f(x) = x²  → <span>f(x) = x²</span>
- a² + b² = c²  → déjà en Unicode
- Df = ℝ \\ {'{'}0{'}'}  → en JSX : Df = ℝ \ &#123;0&#125;
- Fractions : utilise des div avec flexbox (numérateur/ligne/dénominateur)
- Racines : √x, ∫, ∑, π, ∞, ≤, ≥, ∈, ∉ directement en Unicode

Pour les graphes (axes + courbe) : utilise SVG inline animé.

═══════════════════════════════════════════════════════════════════
PALETTE OBLIGATOIRE
═══════════════════════════════════════════════════════════════════
Fond : #1a1a2e
Titres : #ffffff
Concept principal : #4fc3f7
Résultat/succès : #81c784
Accent/important : #ffb74d
Exclusion/erreur : #ef5350
Texte secondaire : #b0bec5

═══════════════════════════════════════════════════════════════════
EXEMPLES IVOIRIENS
═══════════════════════════════════════════════════════════════════
Quand c'est pertinent et naturel :
- "Un commerçant du marché d'Adjamé..."
- "La distance entre Abidjan et Yamoussoukro..."
- "Le prix du cacao en FCFA..."

═══════════════════════════════════════════════════════════════════
RÈGLES TECHNIQUES ABSOLUES
═══════════════════════════════════════════════════════════════════
- Export : export const LessonVideo  (named export, pas default)
- Seuls imports autorisés : remotion et react
- Pas de bibliothèques externes (pas de KaTeX, Chart.js, etc.)
- JSX valide sans erreurs de syntaxe
- Séquences Sequence couvrent l'intégralité du cours
- Le composant LessonVideo n'accepte AUCUN prop (l'audio est mixé par FFmpeg séparément)
- PAS de composant Audio — NE PAS importer Audio depuis remotion

Réponds UNIQUEMENT avec le code JSX complet. Aucun backtick, aucune explication.

═══════════════════════════════════════════════════════════════════
EXEMPLE COMPLET — Pythagore (75 secondes)
═══════════════════════════════════════════════════════════════════

import { useCurrentFrame, useVideoConfig, interpolate, spring, Sequence, AbsoluteFill } from 'remotion'

// Segment 0 [0→20s] : Introduction
const IntroSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titreO = interpolate(frame, [0, fps], [0, 1], { extrapolateRight: 'clamp' })
  const titreY = interpolate(frame, [0, fps], [40, 0], { extrapolateRight: 'clamp' })
  const sousTitreO = interpolate(frame, [fps * 0.8, fps * 1.5], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
      <h1 style={{ color: '#4fc3f7', fontSize: 72, margin: 0, opacity: titreO, transform: `translateY(${titreY}px)`, fontWeight: 'bold' }}>
        Théorème de Pythagore
      </h1>
      <p style={{ color: '#b0bec5', fontSize: 32, margin: 0, opacity: sousTitreO }}>
        4ème — Mathématiques
      </p>
    </AbsoluteFill>
  )
}

// Segment 1 [20→45s] : Triangle rectangle
const TriangleSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const drawTriangle = interpolate(frame, [0, fps * 2], [0, 1], { extrapolateRight: 'clamp' })
  const angleO = interpolate(frame, [fps * 2.5, fps * 3], [0, 1], { extrapolateRight: 'clamp' })
  const labelO = interpolate(frame, [fps * 3.5, fps * 4], [0, 1], { extrapolateRight: 'clamp' })

  // Triangle : [0,0] [4,0] [0,3] en unités SVG (400x300 viewport)
  const svgW = 600, svgH = 450
  const pts = { A: [80, 340], B: [480, 340], C: [80, 60] }
  const totalPath = 560 + 400 + 280  // approximation périmètre
  const drawn = interpolate(frame, [0, fps * 2], [totalPath, 0], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <svg width={svgW} height={svgH} viewBox={`0 0 ${svgW} ${svgH}`}>
        {/* Triangle */}
        <polygon
          points={`${pts.A[0]},${pts.A[1]} ${pts.B[0]},${pts.B[1]} ${pts.C[0]},${pts.C[1]}`}
          fill="#4fc3f708"
          stroke="#4fc3f7"
          strokeWidth={3}
          strokeDasharray={totalPath}
          strokeDashoffset={drawn}
        />
        {/* Angle droit */}
        <rect x={pts.A[0]} y={pts.A[1] - 30} width={30} height={30} fill="none" stroke="#81c784" strokeWidth={2.5} opacity={angleO} />
        {/* Label 90° */}
        <text x={pts.A[0] + 36} y={pts.A[1] - 6} fill="#81c784" fontSize={22} opacity={labelO}>90°</text>
      </svg>
    </AbsoluteFill>
  )
}

// Segment 2 [45→65s] : Formule a²+b²=c²
const FormuleSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const labelsO = interpolate(frame, [0, fps * 0.8], [0, 1], { extrapolateRight: 'clamp' })
  const formuleO = interpolate(frame, [fps, fps * 1.8], [0, 1], { extrapolateRight: 'clamp' })
  const formuleScale = spring({ frame: Math.max(0, frame - fps), fps, config: { damping: 12, stiffness: 100 } })
  const cadreO = interpolate(frame, [fps * 2.5, fps * 3], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 80 }}>
      {/* Triangle avec labels */}
      <svg width={360} height={280} viewBox="0 0 600 450">
        <polygon points="80,340 480,340 80,60" fill="#4fc3f708" stroke="#4fc3f7" strokeWidth={3} />
        <rect x={80} y={310} width={30} height={30} fill="none" stroke="#81c784" strokeWidth={2.5} />
        <text x={40} y={210} fill="#ffb74d" fontSize={28} opacity={labelsO} fontStyle="italic">a</text>
        <text x={270} y={385} fill="#ffb74d" fontSize={28} opacity={labelsO} fontStyle="italic">b</text>
        <text x={295} y={215} fill="#4fc3f7" fontSize={28} opacity={labelsO} fontStyle="italic">c</text>
      </svg>
      {/* Formule */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{
          opacity: formuleO,
          transform: `scale(${formuleScale})`,
          fontSize: 64, color: '#ffffff', fontWeight: 'bold',
          border: `3px solid #ffb74d`,
          borderRadius: 12, padding: '16px 32px',
          opacity: formuleO * cadreO || formuleO,
        }}>
          a² + b² = c²
        </div>
      </div>
    </AbsoluteFill>
  )
}

// Segment 3 [65→75s] : Exemple 3-4-5
const ExempleSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const ex1O = interpolate(frame, [0, fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })
  const ex2O = interpolate(frame, [fps, fps * 1.5], [0, 1], { extrapolateRight: 'clamp' })
  const checkO = interpolate(frame, [fps * 2, fps * 2.5], [0, 1], { extrapolateRight: 'clamp' })
  const checkScale = spring({ frame: Math.max(0, frame - fps * 2), fps })

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 24 }}>
      <p style={{ color: '#b0bec5', fontSize: 28, opacity: ex1O }}>Exemple : triangle 3-4-5</p>
      <p style={{ color: '#ffffff', fontSize: 52, opacity: ex2O, fontWeight: 'bold' }}>
        3² + 4² = 5²
      </p>
      <p style={{ color: '#b0bec5', fontSize: 36, opacity: ex2O }}>
        9 + 16 = 25  ✓
      </p>
      <p style={{ color: '#81c784', fontSize: 32, opacity: checkO, transform: `scale(${checkScale})`, fontWeight: 'bold' }}>
        Vérifié !
      </p>
    </AbsoluteFill>
  )
}

export const LessonVideo = () => {
  const { fps } = useVideoConfig()

  return (
    <AbsoluteFill style={{ background: '#1a1a2e', fontFamily: 'Segoe UI, sans-serif' }}>
      <Sequence from={0} durationInFrames={20 * fps}>
        <IntroSegment />
      </Sequence>

      <Sequence from={20 * fps} durationInFrames={25 * fps}>
        <TriangleSegment />
      </Sequence>

      <Sequence from={45 * fps} durationInFrames={20 * fps}>
        <FormuleSegment />
      </Sequence>

      <Sequence from={65 * fps} durationInFrames={10 * fps}>
        <ExempleSegment />
      </Sequence>
    </AbsoluteFill>
  )
}

IMPORTANT : Génère un composant CONCIS et COMPLET.
- Maximum 400 lignes de code
- Pas de commentaires excessifs
- Pas de répétition de code
- Le composant DOIT être syntaxiquement complet — ne jamais couper à mi-chemin
- Si le cours est long, regroupe les segments similaires plutôt que de tout détailler
"""


def generer_composant_remotion(
    plan_enrichi: dict,
    transcription: dict,
    annotations: list,
    niveau: str,
    matiere: str
) -> str:
    """Génère le composant JSX Remotion complet via Claude"""

    segments_detail = "\n".join([
        f"""SEGMENT {seg['index']} [{seg['timestamp_debut']}s → {seg['timestamp_fin']}s] (durée : {seg['timestamp_fin'] - seg['timestamp_debut']:.1f}s)
Texte prof : {seg['texte_prof']}
Éléments visuels : {seg['elements_visuels']}
Transition : {seg.get('transition_depuis_precedent') or 'Ouverture de la scène'}
Persistant : {seg.get('elements_persistants', '')}"""
        for seg in plan_enrichi.get("segments_enrichis", [])
    ])

    effets_par_segment = {}
    for ann in annotations:
        idx = ann.get("segment_index", 0)
        effets = ann.get("effets", [])
        desc = ann.get("description", "")
        if effets or desc:
            effets_par_segment[idx] = {"effets": effets, "description": desc}

    effets_detail = "\n".join([
        f"Segment {idx} : [{', '.join(d['effets'])}]" + (f" — {d['description']}" if d['description'] else "")
        for idx, d in effets_par_segment.items()
    ]) if effets_par_segment else "Aucun effet spécial demandé"

    response = anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=16000,
        system=REMOTION_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
Matière : {matiere}
Niveau : {niveau}
Durée totale : {transcription['duree_totale']} secondes

SUJET : {plan_enrichi.get('sujet_central', '')}
DÉCOR DE BASE : {plan_enrichi.get('decor_base', '')}
FIL CONDUCTEUR : {plan_enrichi.get('fil_conducteur', '')}

SCÉNARIO PAR SEGMENT :
{segments_detail}

EFFETS DEMANDÉS PAR SEGMENT :
{effets_detail}

Génère le composant LessonVideo JSX complet pour {transcription['duree_totale']} secondes.
RAPPEL IMPORTANT : pas de composant <Audio>, pas d'import Audio, LessonVideo() sans props.
"""
        }]
    )

    code = response.content[0].text.strip()
    # Nettoyer les backticks si Claude en ajoute
    if "```" in code:
        parts = code.split("```")
        for part in parts:
            if "import" in part and "remotion" in part:
                code = part
                if code.startswith("jsx") or code.startswith("javascript"):
                    code = code[code.index("\n") + 1:]
                break
    return code.strip()


ANALYSER_PLAN_PROMPT = """
Tu es un expert en pédagogie et en motion design éducatif.
On te donne la transcription d'un cours audio avec timestamps.

Analyse ce cours et retourne UNIQUEMENT un JSON valide avec ce format exact :

{
  "titre_cours": "titre court et percutant (max 8 mots)",
  "sujet_central": "ce dont parle le cours en 1 phrase simple",
  "decor_base": "droite_reelle | plan_cartesien | tableau | schema | texte",
  "palette": "scientifique | chaleureux | dynamique",
  "structure_narrative": "comment le cours progresse logiquement (1-2 phrases)",
  "segments_enrichis": [
    {
      "index": 0,
      "timestamp_debut": 0.0,
      "timestamp_fin": 28.3,
      "type": "slide | animation",
      "resume": "une ligne décrivant ce segment",
      "elements_visuels": ["élément concret 1", "élément concret 2"],
      "effets": []
    }
  ]
}

RÈGLES decor_base :
- "droite_reelle" : ensembles de définition, intervalles, valeurs réelles
- "plan_cartesien" : fonctions, graphes, courbes, coordonnées
- "tableau" : tableaux de valeurs, de signes, de variations
- "schema" : géométrie, triangles, cercles, formes
- "texte" : définitions, langues, histoire, philosophie

RÈGLES palette :
- "scientifique" : maths, physique, SVT
- "chaleureux" : histoire, géo, français, philo
- "dynamique" : cours très interactif ou visuel

RÈGLES type de segment :
- "slide" : introduction, définition, liste, exemple textuel
- "animation" : visualisation géométrique, graphe, droite réelle, formule animée

RÈGLES elements_visuels :
- Liste de 1 à 4 éléments visuels concrets visibles à l'écran
- Exemples : "titre animé", "droite réelle avec point exclu à 0", "graphe de f(x)"

RÈGLES effets :
- [] si aucun effet spécial
- Sinon parmi : ["zoom", "rotation", "3d", "apparition_progressive"]

Réponds UNIQUEMENT en JSON valide, sans aucun texte autour.
"""


def analyser_pour_plan(transcription: dict, niveau: str, matiere: str) -> dict:
    """Route /analyser — retourne un plan structuré consultable dans PlanPreview"""

    segments_formates = "\n".join([
        f"[{seg['start']}s → {seg['end']}s] {seg['text']}"
        for seg in transcription["segments"]
    ])

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=ANALYSER_PLAN_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""
Matière : {matiere}
Niveau : {niveau}
Durée totale : {transcription['duree_totale']} secondes

TRANSCRIPTION :
{segments_formates}
            """
        }]
    )

    contenu = response.content[0].text.strip()
    print("Plan reçu :", contenu[:150])

    if contenu.startswith("```"):
        contenu = contenu.split("```")[1]
        if contenu.startswith("json"):
            contenu = contenu[4:]
        contenu = contenu.strip()

    return json.loads(contenu)


def _convertir_plan_utilisateur(plan_utilisateur: dict, transcription: dict) -> dict:
    """Convertit le format PlanPreview vers le format interne attendu par generer_composant_remotion"""

    segments_raw = transcription.get("segments", [])
    segments_convertis = []

    for seg in plan_utilisateur.get("segments_enrichis", []):
        t_debut = seg.get("timestamp_debut", 0)
        t_fin   = seg.get("timestamp_fin",   0)

        # Recompose le texte prof depuis les segments Whisper couverts
        texte_prof = " ".join(
            s["text"] for s in segments_raw
            if s["start"] >= t_debut - 0.5 and s["end"] <= t_fin + 0.5
        ).strip() or seg.get("resume", "")

        ev = seg.get("elements_visuels", [])
        elements_str = ", ".join(ev) if isinstance(ev, list) else str(ev)

        effets = seg.get("effets", [])
        effets_str = f"Effets demandés : {', '.join(effets)}" if effets else ""

        segments_convertis.append({
            "index":                   seg.get("index", 0),
            "timestamp_debut":         t_debut,
            "timestamp_fin":           t_fin,
            "texte_prof":              texte_prof,
            "elements_visuels":        (elements_str or seg.get("resume", ""))
                                       + (" — " + effets_str if effets_str else ""),
            "transition_depuis_precedent": None if seg.get("index", 0) == 0
                                           else "Transition depuis segment précédent",
            "elements_persistants":    "",
        })

    return {
        "titre_cours":       plan_utilisateur.get("titre_cours", ""),
        "sujet_central":     plan_utilisateur.get("sujet_central", ""),
        "decor_base":        plan_utilisateur.get("decor_base", ""),
        "fil_conducteur":    plan_utilisateur.get("structure_narrative", ""),
        "segments_enrichis": segments_convertis,
    }


def orchestrer_remotion(
    transcription: dict,
    annotations: list,
    historique_chat: list,
    niveau: str,
    matiere: str,
    plan_enrichi: dict = None
) -> dict:
    """
    Orchestre la génération d'un composant Remotion.
    Phase 1 : analyse globale (Claude) — sautée si plan_enrichi fourni
    Phase 2 : génération du JSX complet (Claude Opus)
    """
    if plan_enrichi is not None:
        print("Phase 1 : plan utilisateur fourni, conversion en cours...")
        plan_interne = _convertir_plan_utilisateur(plan_enrichi, transcription)
    else:
        print("Phase 1 : Analyse globale du cours...")
        plan_interne = analyser_cours_global(
            transcription, annotations, historique_chat, niveau, matiere
        )

    print("Phase 2 : Génération du composant Remotion...")
    composant_jsx = generer_composant_remotion(
        plan_interne, transcription, annotations, niveau, matiere
    )

    return {
        "titre_cours":      plan_interne["titre_cours"],
        "niveau":           niveau,
        "matiere":          matiere,
        "sujet_central":    plan_interne["sujet_central"],
        "composant_jsx":    composant_jsx,
        "segments_enrichis": plan_interne.get("segments_enrichis", []),
        "duree_totale":     transcription["duree_totale"],
    }


def chat_remotion(
    message: str,
    transcription: dict,
    annotations: list,
    composant_jsx: str,
    historique: list,
    niveau: str,
    matiere: str
) -> dict:
    """
    Chat contextuel Remotion.
    Retourne : { reponse, action, annotations_modifiees, regenerer }
    action ∈ { "modifier_annotations", "regenerer", "info" }
    """
    segments_formates = "\n".join([
        f"[Segment {i}] [{seg['start']}s → {seg['end']}s] {seg['text']}"
        for i, seg in enumerate(transcription["segments"])
    ])
    annotations_json = json.dumps(annotations, ensure_ascii=False, indent=2)

    contexte_initial = f"""Cours : {matiere} — {niveau}
Durée : {transcription.get('duree_totale', '?')} secondes
Composant JSX généré : {"(disponible)" if composant_jsx else "(pas encore généré)"}

TRANSCRIPTION :
{segments_formates}

ANNOTATIONS ACTUELLES :
{annotations_json}"""

    system_prompt = """Tu es l'assistant IA d'Albius, plateforme de génération de vidéos pédagogiques.
Tu aides à affiner les vidéos Remotion JSX.

Tu réponds TOUJOURS :
1. Un message concis en français (1-3 phrases)
2. Une balise <action> : modifier_annotations | regenerer | info
3. Si modifier_annotations : <annotations>[JSON complet]</annotations>

"modifier_annotations" : changer tags, effets, descriptions — pas de regénération
"regenerer" : l'utilisateur veut un changement visuel réel
"info" : répondre à une question sans modifier quoi que ce soit

FORMAT :
[message]
<action>modifier_annotations|regenerer|info</action>
<annotations>[JSON complet si modifier_annotations]</annotations>

Réponds en français."""

    historique_msgs = [
        {"role": "user",      "content": contexte_initial},
        {"role": "assistant", "content": "Je suis prêt à t'aider à améliorer ta vidéo."}
    ]
    for msg in historique:
        historique_msgs.append({"role": msg["role"], "content": msg["content"]})
    historique_msgs.append({"role": "user", "content": message})

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=system_prompt,
        messages=historique_msgs
    )

    texte = response.content[0].text

    # Extraction de l'action
    action = "info"
    if "<action>" in texte and "</action>" in texte:
        s = texte.index("<action>") + len("<action>")
        e = texte.index("</action>")
        action = texte[s:e].strip()

    # Extraction des annotations modifiées
    annotations_modifiees = annotations
    if "<annotations>" in texte and "</annotations>" in texte:
        s = texte.index("<annotations>") + len("<annotations>")
        e = texte.index("</annotations>")
        try:
            annotations_modifiees = json.loads(texte[s:e].strip())
        except Exception as ex:
            print(f"Erreur parsing annotations : {ex}")

    # Nettoyer le message
    reponse = texte
    for balise in ["<action>", "<annotations>"]:
        if balise in reponse:
            reponse = reponse[:reponse.index(balise)].strip()

    return {
        "reponse": reponse,
        "action": action,
        "annotations_modifiees": annotations_modifiees,
        "regenerer": action == "regenerer"
    }

def modifier_composant_existant(
    composant_jsx: str,
    instruction: str,
    transcription: dict,
    niveau: str,
    matiere: str
) -> str:
    """
    Modifie le composant Remotion existant selon l'instruction
    au lieu d'en générer un nouveau from scratch.
    """

    response = anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=16000,
        system="""Tu es un expert React et Remotion.
On te donne un composant Remotion JSX existant et une instruction de modification.

Tu dois MODIFIER le composant existant — pas en créer un nouveau.
Garde toute la structure existante et applique uniquement les changements demandés.

RÈGLES ABSOLUES :
- Retourne le composant COMPLET et FONCTIONNEL
- Ne coupe jamais le code à mi-chemin
- Toutes les accolades et parenthèses doivent être équilibrées
- export const LessonVideo doit toujours être présent
- Maximum 500 lignes
- Retourne UNIQUEMENT le code JSX, rien d'autre
""",
        messages=[{
            "role": "user",
            "content": f"""
Matière: {matiere}
Niveau: {niveau}

INSTRUCTION DE MODIFICATION:
{instruction}

COMPOSANT ACTUEL À MODIFIER:
{composant_jsx}
            """
        }]
    )

    code = response.content[0].text.strip()
    if "```" in code:
        parties = code.split("```")
        for partie in parties:
            if "import" in partie and "remotion" in partie.lower():
                code = partie
                if code.startswith(("tsx", "jsx", "javascript")):
                    code = code[code.index("\n")+1:]
                break

    return code.strip()

if __name__ == "__main__":
    transcription_test = {
        "duree_totale": 75.0,
        "segments": [
            {"start": 0.0, "end": 8.0, "text": "Bonjour, aujourd'hui nous allons voir le théorème de Pythagore"},
            {"start": 8.0, "end": 30.0, "text": "Ce théorème s'applique uniquement aux triangles rectangles"},
            {"start": 30.0, "end": 55.0, "text": "Si on appelle a et b les deux côtés et c l'hypoténuse, alors a² + b² = c²"},
            {"start": 55.0, "end": 75.0, "text": "Prenons un exemple : un maçon à Abidjan veut vérifier que son angle est droit. Si un côté fait 3m et l'autre 4m, la diagonale doit faire 5m"}
        ]
    }

    resultat = orchestrer(transcription_test, "4ème", "Mathématiques")
    print(json.dumps(resultat, ensure_ascii=False, indent=2))