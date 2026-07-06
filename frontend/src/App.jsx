import { useState } from "react"
import Upload from "./components/Upload"
import PlanPreview from "./components/PlanPreview"
import Loading from "./components/Loading"
import Preview from "./components/Preview"

const C = { bg: "#12122a" }

export default function App() {
  const [etat, setEtat] = useState("upload") // "upload" | "plan" | "loading" | "preview"
  const [transcriptionData, setTranscriptionData] = useState(null)
  const [planData, setPlanData]           = useState(null)
  const [resultat, setResultat]           = useState(null)
  const [annotations, setAnnotations]     = useState([])
  const [erreurGen, setErreurGen]         = useState(null)
  const [etapeLoading, setEtapeLoading]   = useState("")

  function handlePlanOk(transcData, plan) {
    setTranscriptionData(transcData)
    setPlanData(plan)
    setAnnotations([])
    setEtat("plan")
  }

  function handleLoading(etape) {
    setErreurGen(null)
    setEtapeLoading(etape || "")
    setEtat("loading")
  }

  function handleEtapeLoading(etape) {
    setEtapeLoading(etape)
  }

  function handleGenererOk(data) {
    setResultat(data)
    setEtat("preview")
  }

  function handleErreurGen(msg) {
    setErreurGen(msg)
    setEtat("loading") // reste sur loading pour afficher l'erreur
  }

  function handleReset() {
    setEtat("upload")
    setTranscriptionData(null)
    setPlanData(null)
    setResultat(null)
    setAnnotations([])
    setErreurGen(null)
    setEtapeLoading("")
  }

  return (
    <div style={{ minHeight: "100vh", background: C.bg, fontFamily: "'Segoe UI', sans-serif" }}>
      {etat === "upload" && (
        <Upload
          onPlanOk={handlePlanOk}
          onErreur={handleErreurGen}
        />
      )}

      {etat === "plan" && (
        <PlanPreview
          transcriptionData={transcriptionData}
          planData={planData}
          onPlanChange={setPlanData}
          onLoading={handleLoading}
          onEtapeLoading={handleEtapeLoading}
          onGenererOk={handleGenererOk}
          onErreur={handleErreurGen}
          onBack={handleReset}
        />
      )}

      {etat === "loading" && (
        <Loading
          etape={etapeLoading}
          erreur={erreurGen}
          onRetour={handleReset}
        />
      )}

      {etat === "preview" && (
        <Preview
          data={resultat}
          transcriptionData={transcriptionData}
          annotations={annotations}
          onAnnotationsChange={setAnnotations}
          onLoading={() => { setErreurGen(null); setEtat("loading") }}
          onEtapeLoading={setEtapeLoading}
          onGenererOk={handleGenererOk}
          onErreur={handleErreurGen}
          onReset={handleReset}
        />
      )}
    </div>
  )
}
