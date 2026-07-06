import { useState } from "react"
import axios from "axios"

const C = {
  bg: "#12122a", surface: "#1e1e3a", surface2: "#2a2a4e",
  accent: "#4fc3f7", success: "#81c784", warning: "#ffb74d",
  danger: "#ef5350", text: "#ffffff", textSec: "#b0bec5", border: "#2a2a4e",
}

const DECOR_LABELS = {
  droite_reelle:  { label: "Droite réelle",   color: "#4fc3f7" },
  plan_cartesien: { label: "Plan cartésien",  color: "#81c784" },
  tableau:        { label: "Tableau",         color: "#ffb74d" },
  schema:         { label: "Schéma",          color: "#ce93d8" },
  texte:          { label: "Texte",           color: "#b0bec5" },
}

const PALETTE_LABELS = {
  scientifique: { label: "Scientifique", color: "#4fc3f7" },
  chaleureux:   { label: "Chaleureux",   color: "#ffb74d" },
  dynamique:    { label: "Dynamique",    color: "#81c784" },
}

const EFFETS_DISPONIBLES = ["zoom", "rotation", "3d", "apparition_progressive"]

function fmt(s) {
  if (s == null) return "?"
  const m = Math.floor(s / 60)
  const sec = Math.round(s % 60)
  return m > 0 ? `${m}m${sec.toString().padStart(2, "0")}s` : `${sec}s`
}

function duree(seg) {
  return Math.round((seg.timestamp_fin ?? 0) - (seg.timestamp_debut ?? 0))
}

export default function PlanPreview({
  transcriptionData, planData, onPlanChange,
  onLoading, onEtapeLoading, onGenererOk, onErreur, onBack
}) {
  const { transcription, niveau, matiere, audio_filename } = transcriptionData
  const [segmentEdite, setSegmentEdite] = useState(null)

  function updateSegment(index, patch) {
    const nouveauxSegments = planData.segments_enrichis.map((seg, i) =>
      i === index ? { ...seg, ...patch } : seg
    )
    onPlanChange({ ...planData, segments_enrichis: nouveauxSegments })
  }

  function toggleEffet(segIndex, effet) {
    const seg = planData.segments_enrichis[segIndex]
    const effets = seg.effets || []
    updateSegment(segIndex, {
      effets: effets.includes(effet)
        ? effets.filter(e => e !== effet)
        : [...effets, effet]
    })
  }

  function lancerGeneration() {
    onLoading("Claude génère les animations...")

    axios.post("http://127.0.0.1:8000/generer", {
      transcription:   transcription,
      annotations:     [],
      niveau,
      matiere,
      audio_filename,
      historique_chat: [],
      plan_enrichi:    planData,
    }, { timeout: 1800000 })
      .then(res => {
        if (res.data.status !== "success") {
          throw new Error(res.data.message || "Erreur de génération")
        }
        onGenererOk(res.data)
      })
      .catch(err => {
        onErreur(err.message || "Erreur lors de la génération vidéo")
      })
  }

  const decor   = DECOR_LABELS[planData?.decor_base]   || { label: planData?.decor_base,  color: C.textSec }
  const palette = PALETTE_LABELS[planData?.palette]     || { label: planData?.palette,     color: C.textSec }
  const segments = planData?.segments_enrichis || []
  const dureeTotal = fmt(transcription?.duree_totale)

  return (
    <div style={{
      minHeight: "100vh", background: C.bg,
      fontFamily: "'Segoe UI', sans-serif",
      padding: "0 0 60px",
    }}>
      {/* ── Header ── */}
      <div style={{
        background: C.surface, borderBottom: `1px solid ${C.border}`,
        padding: "16px 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div>
          <h1 style={{ color: C.accent, fontSize: 22, margin: 0, fontWeight: 700 }}>
            Albius — Plan du cours
          </h1>
          <p style={{ color: C.textSec, margin: "3px 0 0", fontSize: 13 }}>
            {matiere} · {niveau} · {dureeTotal}
          </p>
        </div>
        <button
          onClick={onBack}
          style={{
            padding: "8px 18px", background: "transparent",
            border: `1px solid ${C.border}`, borderRadius: 8,
            color: C.textSec, cursor: "pointer", fontSize: 13,
          }}
        >
          ← Recommencer
        </button>
      </div>

      <div style={{ maxWidth: 800, margin: "0 auto", padding: "32px 24px" }}>
        {/* ── Titre détecté ── */}
        <div style={{
          background: C.surface, borderRadius: 12,
          padding: "24px 28px", marginBottom: 24,
          border: `1px solid ${C.border}`,
        }}>
          <h2 style={{ color: C.text, fontSize: 22, margin: "0 0 6px", fontWeight: 700 }}>
            {planData?.titre_cours || "Cours"}
          </h2>
          <p style={{ color: C.textSec, fontSize: 14, margin: "0 0 18px", lineHeight: 1.6 }}>
            {planData?.sujet_central}
          </p>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {/* Badge décor */}
            <span style={{
              background: decor.color + "22", color: decor.color,
              border: `1px solid ${decor.color}66`,
              padding: "4px 14px", borderRadius: 20, fontSize: 12, fontWeight: 600,
            }}>
              📐 {decor.label}
            </span>
            {/* Badge palette */}
            <span style={{
              background: palette.color + "22", color: palette.color,
              border: `1px solid ${palette.color}66`,
              padding: "4px 14px", borderRadius: 20, fontSize: 12, fontWeight: 600,
            }}>
              🎨 {palette.label}
            </span>
            {/* Badge durée */}
            <span style={{
              background: C.surface2, color: C.textSec,
              border: `1px solid ${C.border}`,
              padding: "4px 14px", borderRadius: 20, fontSize: 12,
            }}>
              ⏱ {dureeTotal}
            </span>
          </div>
        </div>

        {/* ── Structure narrative ── */}
        {planData?.structure_narrative && (
          <div style={{
            background: C.surface, borderRadius: 10,
            padding: "16px 20px", marginBottom: 24,
            border: `1px solid ${C.border}`,
          }}>
            <p style={{ color: C.textSec, fontSize: 11, margin: "0 0 8px", textTransform: "uppercase", letterSpacing: 1 }}>
              Structure narrative
            </p>
            <p style={{ color: C.text, fontSize: 14, margin: 0, lineHeight: 1.6 }}>
              {planData.structure_narrative}
            </p>
          </div>
        )}

        {/* ── Séquences ── */}
        <div style={{ marginBottom: 32 }}>
          <p style={{ color: C.textSec, fontSize: 11, margin: "0 0 14px", textTransform: "uppercase", letterSpacing: 1 }}>
            Séquences ({segments.length})
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {segments.map((seg, i) => {
              const isSlide = seg.type === "slide"
              const typeColor = isSlide ? C.success : C.accent
              const typeBg    = isSlide ? "#1a3a2a" : "#1a2a4a"
              const editing   = segmentEdite === i

              return (
                <div key={i} style={{
                  background: C.surface, borderRadius: 10,
                  border: `1px solid ${editing ? C.accent : C.border}`,
                  overflow: "hidden", transition: "border-color 0.2s",
                }}>
                  {/* En-tête de séquence */}
                  <div style={{
                    padding: "14px 18px",
                    display: "flex", alignItems: "center", gap: 12,
                  }}>
                    {/* Numéro */}
                    <span style={{
                      color: C.textSec, fontSize: 12, fontWeight: 700,
                      flexShrink: 0, width: 28, textAlign: "center",
                    }}>
                      {String(i + 1).padStart(2, "0")}
                    </span>

                    {/* Badge type */}
                    <span style={{
                      background: typeBg, color: typeColor,
                      border: `1px solid ${typeColor}66`,
                      padding: "3px 10px", borderRadius: 12,
                      fontSize: 11, fontWeight: 700, flexShrink: 0,
                    }}>
                      {isSlide ? "Slide" : "Animation"}
                    </span>

                    {/* Durée */}
                    <span style={{
                      color: C.textSec, fontSize: 12, flexShrink: 0,
                    }}>
                      {duree(seg)}s
                    </span>

                    {/* Résumé */}
                    <span style={{
                      color: C.text, fontSize: 13, flex: 1,
                      overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
                    }}>
                      {seg.resume}
                    </span>

                    {/* Timestamps */}
                    <span style={{ color: "#555", fontSize: 11, flexShrink: 0 }}>
                      {fmt(seg.timestamp_debut)} → {fmt(seg.timestamp_fin)}
                    </span>

                    {/* Bouton éditer */}
                    <button
                      onClick={() => setSegmentEdite(editing ? null : i)}
                      style={{
                        padding: "4px 10px", background: "transparent",
                        border: `1px solid ${editing ? C.accent : C.border}`,
                        borderRadius: 6, color: editing ? C.accent : C.textSec,
                        cursor: "pointer", fontSize: 12, flexShrink: 0,
                      }}
                    >
                      {editing ? "✓ OK" : "✏️"}
                    </button>
                  </div>

                  {/* Éléments visuels (badges) */}
                  {!editing && (seg.elements_visuels || []).length > 0 && (
                    <div style={{
                      padding: "0 18px 12px 58px",
                      display: "flex", flexWrap: "wrap", gap: 6,
                    }}>
                      {(seg.elements_visuels || []).map((ev, j) => (
                        <span key={j} style={{
                          background: C.surface2, color: C.textSec,
                          border: `1px solid ${C.border}`,
                          padding: "2px 9px", borderRadius: 12, fontSize: 11,
                        }}>
                          {ev}
                        </span>
                      ))}
                      {(seg.effets || []).map(ef => (
                        <span key={ef} style={{
                          background: "#1a2a3a", color: C.accent,
                          border: `1px solid ${C.accent}44`,
                          padding: "2px 9px", borderRadius: 12, fontSize: 11, fontWeight: 600,
                        }}>
                          ⚡ {ef}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Éditeur inline */}
                  {editing && (
                    <div style={{
                      padding: "0 18px 18px 18px",
                      borderTop: `1px solid ${C.border}`,
                    }}>
                      {/* Type */}
                      <div style={{ marginTop: 14, marginBottom: 12 }}>
                        <p style={labelStyle}>Type de rendu</p>
                        <div style={{ display: "flex", gap: 8 }}>
                          {["slide", "animation"].map(t => (
                            <button
                              key={t}
                              onClick={() => updateSegment(i, { type: t })}
                              style={{
                                padding: "7px 18px",
                                background: seg.type === t
                                  ? (t === "slide" ? "#1a3a2a" : "#1a2a4a")
                                  : "transparent",
                                color: seg.type === t
                                  ? (t === "slide" ? C.success : C.accent)
                                  : C.textSec,
                                border: `1px solid ${seg.type === t
                                  ? (t === "slide" ? C.success : C.accent)
                                  : C.border}`,
                                borderRadius: 8, cursor: "pointer",
                                fontSize: 13, fontWeight: seg.type === t ? 700 : 400,
                                textTransform: "capitalize",
                              }}
                            >
                              {t === "slide" ? "Slide" : "Animation"}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Résumé */}
                      <div style={{ marginBottom: 12 }}>
                        <p style={labelStyle}>Résumé</p>
                        <input
                          type="text"
                          value={seg.resume || ""}
                          onChange={e => updateSegment(i, { resume: e.target.value })}
                          style={{
                            width: "100%", padding: "8px 12px",
                            background: C.surface2, border: `1px solid ${C.border}`,
                            borderRadius: 8, color: C.text, fontSize: 13,
                            boxSizing: "border-box", fontFamily: "inherit",
                          }}
                        />
                      </div>

                      {/* Effets */}
                      {seg.type === "animation" && (
                        <div>
                          <p style={labelStyle}>Effets visuels</p>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                            {EFFETS_DISPONIBLES.map(ef => {
                              const actif = (seg.effets || []).includes(ef)
                              return (
                                <button
                                  key={ef}
                                  onClick={() => toggleEffet(i, ef)}
                                  style={{
                                    padding: "5px 12px",
                                    background: actif ? "#1a2a3a" : "transparent",
                                    color: actif ? C.accent : C.textSec,
                                    border: `1px solid ${actif ? C.accent : C.border}`,
                                    borderRadius: 20, cursor: "pointer",
                                    fontSize: 11, fontWeight: actif ? 700 : 400,
                                  }}
                                >
                                  {actif ? "✓ " : ""}{ef.replace("_", " ")}
                                </button>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* ── Bouton Générer ── */}
        <button
          onClick={lancerGeneration}
          style={{
            width: "100%", padding: "16px",
            background: C.accent, color: "#1a1a2e",
            border: "none", borderRadius: 10,
            fontSize: 17, fontWeight: 700, cursor: "pointer",
            boxShadow: `0 4px 20px ${C.accent}44`,
            transition: "box-shadow 0.2s",
          }}
        >
          Générer la vidéo →
        </button>
        <p style={{
          color: C.textSec, fontSize: 12, textAlign: "center",
          margin: "10px 0 0",
        }}>
          2 à 5 minutes · Claude crée les animations · Remotion rend la vidéo
        </p>
      </div>
    </div>
  )
}

const labelStyle = {
  color: "#b0bec5", fontSize: 11, margin: "0 0 8px",
  textTransform: "uppercase", letterSpacing: 1,
}
