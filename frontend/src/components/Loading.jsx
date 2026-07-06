import { useState, useEffect } from "react"

const C = { bg: "#12122a", accent: "#4fc3f7", textSec: "#b0bec5" }

const MESSAGES = [
  "Claude analyse la structure pédagogique...",
  "Génération des animations en cours...",
  "Remotion rend la vidéo image par image...",
  "Mixage de la voix avec les animations...",
  "Optimisation de la vidéo finale...",
]

export default function Loading({ etape, erreur, onRetour }) {
  const [msgIdx, setMsgIdx] = useState(0)
  const [dots, setDots] = useState("")

  // Rotation des messages toutes les 4s
  useEffect(() => {
    if (erreur) return
    const interval = setInterval(() => {
      setMsgIdx(i => (i + 1) % MESSAGES.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [erreur])

  // Dots animés
  useEffect(() => {
    if (erreur) return
    const interval = setInterval(() => {
      setDots(d => d.length >= 3 ? "" : d + ".")
    }, 500)
    return () => clearInterval(interval)
  }, [erreur])

  if (erreur) {
    return (
      <div style={{
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        height: "100vh", background: C.bg,
        fontFamily: "'Segoe UI', sans-serif",
        padding: "0 24px", textAlign: "center",
      }}>
        <div style={{ fontSize: 56, marginBottom: 24 }}>❌</div>
        <h2 style={{ color: "#ffffff", margin: "0 0 12px", fontSize: 22 }}>
          Erreur de génération
        </h2>
        <p style={{
          color: C.textSec, maxWidth: 520, marginBottom: 36,
          lineHeight: 1.65, fontSize: 14,
        }}>
          {erreur}
        </p>
        <button
          onClick={onRetour}
          style={{
            padding: "11px 32px", background: C.accent,
            color: "#1a1a2e", border: "none", borderRadius: 8,
            fontSize: 15, fontWeight: 700, cursor: "pointer",
          }}
        >
          ← Recommencer
        </button>
      </div>
    )
  }

  const messageActuel = etape || MESSAGES[msgIdx]

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      height: "100vh", background: C.bg,
      fontFamily: "'Segoe UI', sans-serif",
      padding: "0 24px", textAlign: "center",
    }}>
      {/* Spinner SVG */}
      <svg
        width={64} height={64}
        viewBox="0 0 64 64"
        style={{ marginBottom: 32 }}
      >
        <circle
          cx={32} cy={32} r={28}
          fill="none" stroke="#1e1e3a" strokeWidth={6}
        />
        <circle
          cx={32} cy={32} r={28}
          fill="none" stroke={C.accent} strokeWidth={6}
          strokeDasharray={176}
          strokeDashoffset={44}
          strokeLinecap="round"
          style={{
            transformOrigin: "center",
            animation: "spin 1.2s linear infinite",
          }}
        />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </svg>

      <h2 style={{ color: "#ffffff", margin: "0 0 16px", fontSize: 22, fontWeight: 700 }}>
        Génération en cours
      </h2>

      {/* Message rotatif */}
      <p style={{
        color: C.accent, fontSize: 15, margin: "0 0 8px",
        minHeight: 24, transition: "opacity 0.3s",
      }}>
        {messageActuel}{dots}
      </p>

      <p style={{ color: C.textSec, fontSize: 13, margin: "0 0 48px" }}>
        2 à 5 minutes selon la durée du cours
      </p>

      {/* Étapes visuelles */}
      <div style={{
        display: "flex", gap: 0, alignItems: "center",
        maxWidth: 480, width: "100%",
      }}>
        {[
          { label: "Transcription", done: true },
          { label: "Analyse",       done: true },
          { label: "Génération JSX", done: false },
          { label: "Rendu vidéo",   done: false },
        ].map((step, i, arr) => (
          <div key={i} style={{ display: "flex", alignItems: "center", flex: 1 }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", flex: 1 }}>
              <div style={{
                width: 28, height: 28, borderRadius: "50%",
                background: step.done ? C.accent : "#1e1e3a",
                border: `2px solid ${step.done ? C.accent : "#2a2a4e"}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12, color: step.done ? "#1a1a2e" : "#555",
                fontWeight: 700, marginBottom: 6,
              }}>
                {step.done ? "✓" : i + 1}
              </div>
              <span style={{ color: step.done ? C.accent : "#555", fontSize: 10, textAlign: "center" }}>
                {step.label}
              </span>
            </div>
            {i < arr.length - 1 && (
              <div style={{
                height: 2, flex: 0.5, marginBottom: 22,
                background: step.done ? C.accent : "#2a2a4e",
              }} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
