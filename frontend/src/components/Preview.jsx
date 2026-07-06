import { useState, useRef, useEffect } from "react"
import axios from "axios"

const C = {
  bg: "#12122a", surface: "#1e1e3a", surface2: "#2a2a4e",
  accent: "#4fc3f7", success: "#81c784", warning: "#ffb74d",
  danger: "#ef5350", text: "#ffffff", textSec: "#b0bec5", border: "#2a2a4e",
}

const SUGGESTIONS = [
  "Rends la vidéo plus dynamique",
  "Ajoute plus d'animations SVG",
  "Simplifie le contenu",
  "Ajoute des exemples ivoiriens",
  "Améliore le segment final",
]

function fmt(s) {
  if (s == null) return "?"
  const m = Math.floor(s / 60)
  const sec = Math.round(s % 60)
  return m > 0 ? `${m}m${sec.toString().padStart(2, "0")}s` : `${sec}s`
}

export default function Preview({
  data, transcriptionData, annotations, onAnnotationsChange,
  onLoading, onEtapeLoading, onGenererOk, onErreur, onReset,
}) {
  const { plan } = data
  const [composantJsx, setComposantJsx] = useState(data.composant_jsx || "")
  const segments = plan?.segments_enrichis || []
  const { transcription, niveau, matiere, audio_filename } = transcriptionData || {}

  const [videoUrl, setVideoUrl]           = useState(data.video_url)
  const [segmentOuvert, setSegmentOuvert] = useState(null)
  const [messages, setMessages]           = useState([])
  const [inputChat, setInputChat]         = useState("")
  const [chatLoading, setChatLoading]     = useState(false)
  const chatRef = useRef(null)

  useEffect(() => {
    chatRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  function prefillModifier(i) {
    setInputChat(`Modifie la séquence ${i + 1} : `)
  }

  async function envoyerMessage(texte) {
    if (!texte.trim() || chatLoading) return
    const newMsgs = [...messages, { role: "user", content: texte }]
    setMessages(newMsgs)
    setInputChat("")
    setChatLoading(true)

    let annMod = annotations
    let reponse = ""
    let regenerer = false

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message:       texte,
        transcription,
        annotations,
        composant_jsx: composantJsx,
        historique:    messages,
        niveau,
        matiere,
      })
      reponse   = res.data.reponse || ""
      annMod    = res.data.annotations_modifiees || annotations
      regenerer = !!res.data.regenerer

      setMessages([...newMsgs, { role: "assistant", content: reponse }])
      if (annMod.length === annotations.length) onAnnotationsChange(annMod)
    } catch {
      setMessages([...newMsgs, { role: "assistant", content: "Erreur de connexion au serveur." }])
      setChatLoading(false)
      return
    }

    setChatLoading(false)

    if (regenerer) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Je lance la regénération de ta vidéo...",
      }])

      onLoading()
      onEtapeLoading?.("Regénération de la vidéo en cours...")

      axios.post("http://127.0.0.1:8000/generer", {
        transcription,
        annotations:   annMod,
        niveau,
        matiere,
        historique_chat: [...newMsgs, { role: "assistant", content: reponse }],
        audio_filename,
        composant_existant:       composantJsx,
        instruction_modification: texte,
        titre_cours: plan?.titre_cours || ""
      }, { timeout: 1800000 })
        .then(genRes => {
          if (genRes.data.status === "success") {
            setComposantJsx(genRes.data.composant_jsx || "")
            setVideoUrl(genRes.data.video_url || "")
            onGenererOk(genRes.data)
          } else {
            onErreur(genRes.data.message || "Erreur lors de la regénération")
          }
        })
        .catch(() => onErreur("Erreur réseau lors de la regénération"))
    }
  }

  return (
    <div style={{
      display: "flex", flexDirection: "column", height: "100vh",
      background: C.bg, fontFamily: "'Segoe UI', sans-serif", overflow: "hidden",
    }}>
      {/* ── Header ── */}
      <div style={{
        padding: "12px 24px", background: C.surface,
        borderBottom: `1px solid ${C.border}`,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        flexShrink: 0,
      }}>
        <div>
          <h1 style={{ color: C.accent, fontSize: 20, margin: 0, fontWeight: 700 }}>
            {plan?.titre_cours || "Cours généré"}
          </h1>
          <p style={{ color: C.textSec, margin: "2px 0 0", fontSize: 13 }}>
            {plan?.matiere} · {plan?.niveau} · {fmt(plan?.duree_totale)}
          </p>
        </div>
        <button onClick={onReset} style={{
          padding: "8px 20px", background: "transparent",
          border: `1px solid ${C.border}`, borderRadius: 8,
          color: C.textSec, cursor: "pointer", fontSize: 14,
        }}>
          ← Nouveau cours
        </button>
      </div>

      {/* ── Corps 2 colonnes ── */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {/* ── Colonne gauche 60% ── */}
        <div style={{
          flex: "0 0 60%", overflowY: "auto",
          borderRight: `1px solid ${C.border}`, padding: "20px 24px",
        }}>
          {/* Player */}
          {videoUrl && (
            <div style={{ marginBottom: 20 }}>
              <video
                key={videoUrl} controls
                style={{
                  width: "100%", borderRadius: 12, background: "#000",
                  maxHeight: 360, boxShadow: "0 4px 24px rgba(0,0,0,0.5)",
                }}
                src={videoUrl}
              />
            </div>
          )}

          {/* Badge succès */}
          <div style={{
            background: "#1a3a1a", border: `1px solid ${C.success}`,
            borderRadius: 10, padding: "10px 16px",
            color: C.success, fontSize: 13, marginBottom: 20,
          }}>
            ✅ Vidéo générée avec succès — Remotion
          </div>

          {/* Timeline bar */}
          {segments.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <p style={{
                color: C.textSec, fontSize: 11, margin: "0 0 8px",
                textTransform: "uppercase", letterSpacing: 1,
              }}>
                Séquences du cours
              </p>
              <div style={{
                display: "flex", height: 40, borderRadius: 8,
                overflow: "hidden", gap: 2, marginBottom: 16,
              }}>
                {segments.map((seg, i) => {
                  const debut = seg.timestamp_debut ?? 0
                  const fin   = seg.timestamp_fin   ?? debut
                  const w     = ((fin - debut) / (plan?.duree_totale || 1)) * 100
                  return (
                    <div
                      key={i}
                      onClick={() => setSegmentOuvert(segmentOuvert === i ? null : i)}
                      title={`Séquence ${i + 1} — ${fmt(debut)} → ${fmt(fin)}`}
                      style={{
                        width: `${Math.max(w, 2)}%`, minWidth: 22,
                        background: "#1a2a3a", borderTop: `3px solid ${C.accent}`,
                        cursor: "pointer",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 11, color: C.accent, fontWeight: 700,
                        opacity: segmentOuvert === null || segmentOuvert === i ? 1 : 0.35,
                        transition: "opacity 0.2s",
                      }}
                    >
                      {i + 1}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Accordéon des séquences */}
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {segments.map((seg, i) => {
              const ouvert = segmentOuvert === i
              const debut  = seg.timestamp_debut ?? 0
              const fin    = seg.timestamp_fin   ?? debut
              return (
                <div key={i} style={{
                  background: C.surface,
                  border: `1px solid ${ouvert ? C.accent : C.border}`,
                  borderRadius: 10, overflow: "hidden",
                  transition: "border-color 0.2s",
                }}>
                  <div
                    onClick={() => setSegmentOuvert(ouvert ? null : i)}
                    style={{
                      padding: "11px 14px", cursor: "pointer",
                      display: "flex", alignItems: "center", gap: 10,
                    }}
                  >
                    <span style={{
                      background: "#1a2a3a", color: C.accent,
                      padding: "2px 10px", borderRadius: 20,
                      fontSize: 11, fontWeight: 700, flexShrink: 0,
                    }}>
                      #{i + 1}
                    </span>
                    <span style={{ color: C.textSec, fontSize: 12, flexShrink: 0 }}>
                      {fmt(debut)} → {fmt(fin)}
                    </span>
                    <span style={{
                      color: C.text, fontSize: 12, flex: 1,
                      overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
                    }}>
                      {seg.elements_visuels || seg.texte_prof || ""}
                    </span>
                    <div style={{ display: "flex", gap: 6, alignItems: "center", flexShrink: 0 }}>
                      <button
                        onClick={e => {
                          e.stopPropagation()
                          prefillModifier(i)
                          document.getElementById("chat-input")?.focus()
                        }}
                        style={{
                          padding: "3px 10px", background: "transparent",
                          border: `1px solid ${C.border}`, borderRadius: 6,
                          color: C.textSec, cursor: "pointer", fontSize: 11,
                        }}
                        title="Préremplir le chat pour modifier cette séquence"
                      >
                        ✏️ Modifier
                      </button>
                      <span style={{ color: "#555", fontSize: 12 }}>
                        {ouvert ? "▲" : "▼"}
                      </span>
                    </div>
                  </div>

                  {ouvert && (
                    <div style={{
                      padding: "0 14px 14px",
                      borderTop: `1px solid ${C.border}`,
                    }}>
                      {seg.texte_prof && (
                        <p style={{
                          color: C.textSec, fontSize: 12, fontStyle: "italic",
                          margin: "12px 0 6px", lineHeight: 1.55,
                        }}>
                          "{seg.texte_prof}"
                        </p>
                      )}
                      {seg.elements_visuels && (
                        <p style={{ color: C.text, fontSize: 12, margin: "6px 0 3px" }}>
                          <span style={{ color: C.accent, fontWeight: 600 }}>Visuels : </span>
                          {seg.elements_visuels}
                        </p>
                      )}
                      {seg.elements_persistants && (
                        <p style={{ color: C.textSec, fontSize: 11, margin: "3px 0" }}>
                          <span style={{ color: C.warning, fontWeight: 600 }}>Persistant : </span>
                          {seg.elements_persistants}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* ── Colonne droite 40% — Chat ── */}
        <div style={{
          flex: 1, display: "flex", flexDirection: "column",
          background: C.surface, overflow: "hidden",
        }}>
          <div style={{
            padding: "12px 16px", borderBottom: `1px solid ${C.border}`, flexShrink: 0,
          }}>
            <p style={{
              color: C.textSec, fontSize: 11, margin: 0,
              textTransform: "uppercase", letterSpacing: 1,
            }}>
              Assistant IA
            </p>
          </div>

          <div style={{
            flex: 1, overflowY: "auto", padding: 14,
            display: "flex", flexDirection: "column", gap: 10,
          }}>
            {messages.length === 0 && (
              <div>
                <p style={{ color: C.textSec, fontSize: 13, margin: "0 0 14px", lineHeight: 1.5 }}>
                  Dis-moi comment améliorer ta vidéo, ou clique sur ✏️ Modifier pour cibler une séquence.
                </p>
                {SUGGESTIONS.map((s, i) => (
                  <button key={i} onClick={() => envoyerMessage(s)} style={{
                    display: "block", width: "100%",
                    padding: "8px 12px", marginBottom: 8,
                    background: C.surface2, border: `1px solid ${C.border}`,
                    borderRadius: 8, color: C.textSec, cursor: "pointer",
                    fontSize: 12, textAlign: "left", lineHeight: 1.4,
                  }}>
                    {s}
                  </button>
                ))}
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} style={{
                padding: "9px 13px", borderRadius: 10,
                background: msg.role === "user" ? "#1a2a4a" : C.surface2,
                color: msg.role === "user" ? C.accent : C.text,
                fontSize: 13, lineHeight: 1.5,
                alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
                maxWidth: "92%",
                border: `1px solid ${msg.role === "user" ? C.accent + "44" : C.border}`,
                whiteSpace: "pre-wrap",
              }}>
                {msg.content}
              </div>
            ))}

            {chatLoading && (
              <div style={{
                padding: "9px 13px", borderRadius: 10,
                background: C.surface2, color: C.textSec,
                fontSize: 13, alignSelf: "flex-start",
              }}>
                ⏳ Réflexion...
              </div>
            )}
            <div ref={chatRef} />
          </div>

          <div style={{
            padding: 10, borderTop: `1px solid ${C.border}`,
            display: "flex", gap: 8, flexShrink: 0,
          }}>
            <textarea
              id="chat-input"
              placeholder="Tape ta demande ici... (Entrée pour envoyer)"
              value={inputChat}
              onChange={e => setInputChat(e.target.value)}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  envoyerMessage(inputChat)
                }
              }}
              rows={2}
              style={{
                flex: 1, padding: "8px 10px", background: C.surface2,
                border: `1px solid ${C.border}`, borderRadius: 8,
                color: C.text, fontSize: 13, resize: "none", fontFamily: "inherit",
              }}
            />
            <button
              onClick={() => envoyerMessage(inputChat)}
              disabled={!inputChat.trim() || chatLoading}
              style={{
                padding: "8px 14px",
                background: inputChat.trim() && !chatLoading ? C.accent : C.surface2,
                color: inputChat.trim() && !chatLoading ? "#1a1a2e" : "#666",
                border: "none", borderRadius: 8,
                cursor: inputChat.trim() && !chatLoading ? "pointer" : "not-allowed",
                fontSize: 16, fontWeight: 700, alignSelf: "flex-end",
              }}
            >
              →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}