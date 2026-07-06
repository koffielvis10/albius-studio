import { useState } from "react"
import axios from "axios"

const NIVEAUX = ["6ème", "5ème", "4ème", "3ème", "Seconde", "Première", "Terminale"]
const MATIERES = ["Mathématiques", "Physique-Chimie", "SVT", "Histoire-Géographie", "Français", "Anglais", "Philosophie"]

const C = {
  surface: "#1e1e3a", surface2: "#2a2a4e",
  accent: "#4fc3f7", danger: "#ef5350",
  text: "#e0e0e0", textSec: "#b0bec5", border: "#3a3a6e",
}

const ETAPES = [
  { id: "upload",         label: "Upload de l'audio..." },
  { id: "transcription",  label: "Transcription Whisper en cours..." },
  { id: "analyse",        label: "Analyse du cours par l'IA..." },
]

export default function Upload({ onPlanOk, onErreur }) {
  const [audio, setAudio]     = useState(null)
  const [niveau, setNiveau]   = useState("Seconde")
  const [matiere, setMatiere] = useState("Mathématiques")
  const [loading, setLoading] = useState(false)
  const [etapeIdx, setEtapeIdx] = useState(0)
  const [erreur, setErreur]   = useState(null)

  function setEtape(id) {
    const idx = ETAPES.findIndex(e => e.id === id)
    if (idx >= 0) setEtapeIdx(idx)
  }

  async function handleSubmit() {
    if (!audio) { setErreur("Veuillez sélectionner un fichier audio"); return }
    setErreur(null)
    setLoading(true)
    setEtape("upload")

    const formData = new FormData()
    formData.append("audio", audio)
    formData.append("niveau", niveau)
    formData.append("matiere", matiere)

    try {
      // ── Étape 1 : Transcription Whisper ──
      setEtape("transcription")
      const transRes = await axios.post(
        "http://127.0.0.1:8000/transcrire",
        formData,
        { headers: { "Content-Type": "multipart/form-data" }, timeout: 1800000 }
      )
      if (transRes.data.status !== "success") {
        throw new Error(transRes.data.message || "Erreur de transcription")
      }
      const transcData = transRes.data

      // ── Étape 2 : Analyse du plan pédagogique ──
      setEtape("analyse")
      const analyseRes = await axios.post(
        "http://127.0.0.1:8000/analyser",
        {
          transcription: transcData.transcription,
          niveau:        transcData.niveau,
          matiere:       transcData.matiere,
        },
        { timeout: 1800000 }
      )
      if (analyseRes.data.status !== "success") {
        throw new Error(analyseRes.data.message || "Erreur d'analyse")
      }

      // ── Transition vers PlanPreview ──
      onPlanOk(transcData, analyseRes.data.plan)

    } catch (err) {
      setErreur(err.message || "Erreur. Vérifie que le backend tourne.")
      setLoading(false)
      setEtapeIdx(0)
    }
  }

  return (
    <div style={{
      maxWidth: 560, margin: "60px auto", padding: "40px",
      background: C.surface, borderRadius: 16,
      boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
    }}>
      <h1 style={{ color: C.accent, fontSize: 28, marginBottom: 6, fontWeight: 700 }}>
        Albius
      </h1>
      <p style={{ color: C.textSec, marginBottom: 32, fontSize: 15 }}>
        Transforme ton cours audio en vidéo pédagogique animée
      </p>

      {/* Fichier audio */}
      <div style={{ marginBottom: 22 }}>
        <label style={{ color: C.text, fontSize: 14, display: "block", marginBottom: 8 }}>
          Fichier audio du cours
        </label>
        <input
          type="file" accept="audio/*"
          onChange={e => setAudio(e.target.files[0])}
          disabled={loading}
          style={{
            width: "100%", padding: "12px",
            background: C.surface2, border: `1px solid ${C.border}`,
            borderRadius: 8, color: C.text, fontSize: 14,
            cursor: "pointer", boxSizing: "border-box",
          }}
        />
        {audio && (
          <p style={{ color: "#81c784", fontSize: 13, marginTop: 6 }}>✓ {audio.name}</p>
        )}
      </div>

      {/* Niveau */}
      <div style={{ marginBottom: 22 }}>
        <label style={{ color: C.text, fontSize: 14, display: "block", marginBottom: 8 }}>
          Niveau scolaire
        </label>
        <select
          value={niveau} onChange={e => setNiveau(e.target.value)} disabled={loading}
          style={{
            width: "100%", padding: "12px",
            background: C.surface2, border: `1px solid ${C.border}`,
            borderRadius: 8, color: C.text, fontSize: 14,
          }}
        >
          {NIVEAUX.map(n => <option key={n} value={n}>{n}</option>)}
        </select>
      </div>

      {/* Matière */}
      <div style={{ marginBottom: 32 }}>
        <label style={{ color: C.text, fontSize: 14, display: "block", marginBottom: 8 }}>
          Matière
        </label>
        <select
          value={matiere} onChange={e => setMatiere(e.target.value)} disabled={loading}
          style={{
            width: "100%", padding: "12px",
            background: C.surface2, border: `1px solid ${C.border}`,
            borderRadius: 8, color: C.text, fontSize: 14,
          }}
        >
          {MATIERES.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>

      {/* Erreur */}
      {erreur && (
        <div style={{
          background: "#3a1a1a", border: `1px solid ${C.danger}`,
          borderRadius: 8, padding: "12px 16px",
          color: C.danger, fontSize: 14, marginBottom: 20,
        }}>
          {erreur}
        </div>
      )}

      {/* Progression */}
      {loading && (
        <div style={{
          background: "#1a2a3a", border: `1px solid ${C.accent}`,
          borderRadius: 8, padding: "14px 16px", marginBottom: 20, textAlign: "center",
        }}>
          <div style={{ color: C.accent, fontSize: 14, marginBottom: 8 }}>
            ⏳ {ETAPES[etapeIdx]?.label}
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            {ETAPES.map((e, i) => (
              <div key={e.id} style={{
                height: 4, flex: 1, borderRadius: 2,
                background: i <= etapeIdx ? C.accent : C.surface2,
                transition: "background 0.4s",
              }} />
            ))}
          </div>
        </div>
      )}

      {/* Bouton */}
      <button
        onClick={handleSubmit}
        disabled={loading || !audio}
        style={{
          width: "100%", padding: "14px",
          background: loading || !audio ? C.surface2 : C.accent,
          color: loading || !audio ? "#666" : "#1a1a2e",
          border: "none", borderRadius: 8,
          fontSize: 16, fontWeight: 700,
          cursor: loading || !audio ? "not-allowed" : "pointer",
          transition: "all 0.2s",
        }}
      >
        {loading ? "Analyse en cours..." : "Analyser le cours →"}
      </button>
    </div>
  )
}
