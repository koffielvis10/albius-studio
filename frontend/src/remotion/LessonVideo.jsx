import { useCurrentFrame, useVideoConfig, Audio, interpolate, spring, Sequence, AbsoluteFill } from 'remotion'

const Segment0 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titleText = "Ensemble de Définition d'une Fonction"
  const lettersShown = Math.floor(interpolate(frame, [0, fps * 2], [0, titleText.length], { extrapolateRight: 'clamp' }))
  const subtitleO = interpolate(frame, [fps * 2.5, fps * 3.5], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20 }}>
      <h1 style={{ color: '#ffffff', fontSize: 56, margin: 0, fontWeight: 'bold', textAlign: 'center', letterSpacing: 2 }}>
        {titleText.slice(0, lettersShown)}
        <span style={{ opacity: frame % 30 < 15 ? 1 : 0 }}>|</span>
      </h1>
      <p style={{ color: '#b0bec5', fontSize: 28, margin: 0, opacity: subtitleO }}>
        Seconde — Mathématiques
      </p>
    </AbsoluteFill>
  )
}

const Title = ({ golden = false }) => (
  <div style={{ position: 'absolute', top: 30, left: 0, right: 0, textAlign: 'center' }}>
    <h1 style={{ color: golden ? '#ffd700' : '#ffffff', fontSize: 36, margin: 0, fontWeight: 'bold', textShadow: golden ? '0 0 20px #ffd700' : 'none' }}>
      Ensemble de Définition — Df
    </h1>
  </div>
)

const Segment1 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const boxO = interpolate(frame, [0, fps * 0.8], [0, 1], { extrapolateRight: 'clamp' })
  const boxScale = spring({ frame, fps, config: { damping: 12, stiffness: 80 } })
  const arrowProgress = interpolate(frame, [fps, fps * 3], [0, 1], { extrapolateRight: 'clamp' })
  const labelO = interpolate(frame, [fps * 2, fps * 3], [0, 1], { extrapolateRight: 'clamp' })
  const xPos = interpolate(frame, [fps * 2, fps * 4], [-80, 60], { extrapolateRight: 'clamp' })
  const yPos = interpolate(frame, [fps * 2, fps * 4], [0, 0], { extrapolateRight: 'clamp' })
  const outputO = interpolate(frame, [fps * 5, fps * 6], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill>
      <Title />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 40 }}>
        {/* Input x */}
        <div style={{ position: 'relative', width: 120, display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
          <div style={{
            color: '#ffb74d', fontSize: 42, fontWeight: 'bold', fontStyle: 'italic',
            transform: `translateX(${xPos}px)`, opacity: labelO
          }}>x</div>
          <svg width={80} height={40} style={{ position: 'absolute', right: -40 }}>
            <line x1={0} y1={20} x2={60 * arrowProgress} y2={20} stroke="#ffb74d" strokeWidth={3} />
            {arrowProgress > 0.8 && <polygon points="55,12 70,20 55,28" fill="#ffb74d" />}
          </svg>
        </div>

        {/* Machine Box */}
        <div style={{
          width: 160, height: 120, background: 'linear-gradient(135deg, #1565c0, #0d47a1)',
          borderRadius: 16, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          opacity: boxO, transform: `scale(${boxScale})`, boxShadow: '0 8px 32px rgba(21,101,192,0.4)',
          border: '3px solid #4fc3f7', position: 'relative'
        }}>
          <div style={{ position: 'absolute', top: -35, color: '#b0bec5', fontSize: 18, fontWeight: 'bold' }}>MACHINE f</div>
          <span style={{ color: '#ffffff', fontSize: 56, fontWeight: 'bold', fontStyle: 'italic' }}>f</span>
        </div>

        {/* Output f(x) */}
        <div style={{ position: 'relative', width: 140, display: 'flex', alignItems: 'center' }}>
          <svg width={80} height={40}>
            <line x1={0} y1={20} x2={60 * arrowProgress} y2={20} stroke="#81c784" strokeWidth={3} />
            {arrowProgress > 0.8 && <polygon points="55,12 70,20 55,28" fill="#81c784" />}
          </svg>
          <div style={{ color: '#81c784', fontSize: 36, fontWeight: 'bold', marginLeft: 20, opacity: outputO }}>f(x)</div>
        </div>
      </div>
    </AbsoluteFill>
  )
}

const Segment2 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const shake = Math.sin(frame * 0.8) * (frame > fps * 2 ? 4 : 0)
  const errorO = interpolate(frame, [fps * 3, fps * 4], [0, 1], { extrapolateRight: 'clamp' })
  const boxRed = interpolate(frame, [fps * 3, fps * 4], [0, 1], { extrapolateRight: 'clamp' })
  const xEnter = interpolate(frame, [fps * 0.5, fps * 2], [-100, 60], { extrapolateRight: 'clamp' })
  const blink = frame % 20 < 10 ? 1 : 0.4
  const formulaO = interpolate(frame, [fps * 5, fps * 6], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill>
      <Title />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 30 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 40 }}>
          {/* Input 0 */}
          <div style={{ position: 'relative', width: 120, display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
            <div style={{
              color: '#ef5350', fontSize: 42, fontWeight: 'bold',
              transform: `translateX(${xEnter}px)`
            }}>x = 0</div>
            <svg width={80} height={40} style={{ position: 'absolute', right: -40 }}>
              <line x1={0} y1={20} x2={60} y2={20} stroke="#ef5350" strokeWidth={3} />
              <polygon points="55,12 70,20 55,28" fill="#ef5350" />
            </svg>
          </div>

          {/* Machine Box with error */}
          <div style={{
            width: 160, height: 120,
            background: `linear-gradient(135deg, ${boxRed > 0.5 ? '#c62828' : '#1565c0'}, ${boxRed > 0.5 ? '#b71c1c' : '#0d47a1'})`,
            borderRadius: 16, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            boxShadow: boxRed > 0.5 ? '0 8px 32px rgba(198,40,40,0.6)' : '0 8px 32px rgba(21,101,192,0.4)',
            border: `3px solid ${boxRed > 0.5 ? '#ef5350' : '#4fc3f7'}`, position: 'relative',
            transform: `translateX(${shake}px)`
          }}>
            <div style={{ position: 'absolute', top: -35, color: '#b0bec5', fontSize: 18, fontWeight: 'bold' }}>MACHINE f</div>
            <span style={{ color: '#ffffff', fontSize: 56, fontWeight: 'bold', fontStyle: 'italic' }}>f</span>
            {errorO > 0.5 && (
              <div style={{
                position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                background: '#ef5350', color: '#fff', padding: '8px 16px', borderRadius: 8,
                fontWeight: 'bold', fontSize: 20, opacity: blink
              }}>⚠ ERREUR !</div>
            )}
          </div>

          {/* Output blocked */}
          <div style={{ position: 'relative', width: 140, display: 'flex', alignItems: 'center' }}>
            <svg width={100} height={60}>
              <line x1={0} y1={30} x2={60} y2={30} stroke="#666" strokeWidth={3} />
              {errorO > 0.5 && (
                <>
                  <line x1={30} y1={10} x2={60} y2={50} stroke="#ef5350" strokeWidth={4} />
                  <line x1={60} y1={10} x2={30} y2={50} stroke="#ef5350" strokeWidth={4} />
                </>
              )}
            </svg>
          </div>
        </div>
        <p style={{ color: '#ffffff', fontSize: 32, margin: 0, opacity: formulaO }}>f(x) = 1/x</p>
      </div>
    </AbsoluteFill>
  )
}

const Segment3 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const shake = Math.sin(frame * 0.5) * 2
  const defO = interpolate(frame, [fps * 2, fps * 3], [0, 1], { extrapolateRight: 'clamp' })
  const defY = interpolate(frame, [fps * 2, fps * 3], [50, 0], { extrapolateRight: 'clamp' })
  const divZeroO = interpolate(frame, [fps * 0.5, fps * 1.5], [0, 1], { extrapolateRight: 'clamp' })
  const divZeroFade = interpolate(frame, [fps * 4, fps * 5], [1, 0], { extrapolateRight: 'clamp' })
  const highlightW = interpolate(frame, [fps * 5, fps * 7], [0, 100], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill>
      <Title />
      {/* Small machine at top */}
      <div style={{ position: 'absolute', top: 100, left: '50%', transform: 'translateX(-50%) scale(0.6)', display: 'flex', alignItems: 'center', gap: 20 }}>
        <span style={{ color: '#ef5350', fontSize: 28 }}>0</span>
        <div style={{
          width: 100, height: 70, background: '#c62828', borderRadius: 12,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          border: '2px solid #ef5350', transform: `translateX(${shake}px)`
        }}>
          <span style={{ color: '#fff', fontSize: 24, fontWeight: 'bold' }}>⚠</span>
        </div>
        <span style={{ color: '#666', fontSize: 24, textDecoration: 'line-through' }}>f(x)</span>
      </div>
      <p style={{ position: 'absolute', top: 190, left: '50%', transform: 'translateX(-50%)', color: '#fff', fontSize: 22 }}>f(x) = 1/x</p>

      {/* Division by zero warning */}
      <div style={{ position: 'absolute', top: 240, left: '50%', transform: 'translateX(-50%)', opacity: divZeroO * divZeroFade }}>
        <p style={{ color: '#ef5350', fontSize: 26, margin: 0 }}>Diviser par 0 → impossible ❌</p>
      </div>

      {/* Definition box */}
      <div style={{
        position: 'absolute', bottom: 80, left: '50%', transform: `translateX(-50%) translateY(${defY}px)`,
        opacity: defO, background: '#1a1a2e', border: '3px solid #ffffff',
        borderRadius: 16, padding: '24px 40px', maxWidth: 700, textAlign: 'center',
        boxShadow: '0 0 30px rgba(255,255,255,0.2)'
      }}>
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <div style={{
            position: 'absolute', top: 0, left: 0, height: '100%', width: `${highlightW}%`,
            background: 'rgba(255,183,77,0.3)', borderRadius: 4
          }} />
          <p style={{ color: '#ffffff', fontSize: 28, margin: 0, position: 'relative', zIndex: 1 }}>
            Df = {'{'} toutes les valeurs x que f accepte sans erreur {'}'}
          </p>
        </div>
      </div>
    </AbsoluteFill>
  )
}

const Segment4 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const axisO = interpolate(frame, [0, fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })
  const curveLength = 400
  const curveDrawn = interpolate(frame, [fps * 0.5, fps * 3], [curveLength, 0], { extrapolateRight: 'clamp' })
  const circleO = interpolate(frame, [fps * 4, fps * 5], [0, 1], { extrapolateRight: 'clamp' })
  const circleScale = spring({ frame: Math.max(0, frame - fps * 4), fps, config: { damping: 10 } })
  const highlightProgress = interpolate(frame, [fps * 6, fps * 8], [0, 1], { extrapolateRight: 'clamp' })
  const labelO = interpolate(frame, [fps * 7, fps * 8], [0, 1], { extrapolateRight: 'clamp' })

  const generateHyperbola = () => {
    let path1 = '', path2 = ''
    for (let i = 20; i <= 180; i += 2) {
      const x = i
      const y = 200 - (3000 / (i - 200))
      if (y > 20 && y < 380) {
        path1 += (path1 === '' ? 'M' : 'L') + `${x},${y} `
      }
    }
    for (let i = 220; i <= 380; i += 2) {
      const x = i
      const y = 200 - (3000 / (i - 200))
      if (y > 20 && y < 380) {
        path2 += (path2 === '' ? 'M' : 'L') + `${x},${y} `
      }
    }
    return { path1, path2 }
  }
  const { path1, path2 } = generateHyperbola()

  return (
    <AbsoluteFill>
      <Title />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <svg width={500} height={440} viewBox="0 0 400 400">
          {/* Axes */}
          <g opacity={axisO}>
            <line x1={20} y1={200} x2={380} y2={200} stroke="#fff" strokeWidth={2} />
            <line x1={200} y1={20} x2={200} y2={380} stroke="#fff" strokeWidth={2} />
            <polygon points="375,195 385,200 375,205" fill="#fff" />
            <polygon points="195,25 200,15 205,25" fill="#fff" />
            <text x={385} y={215} fill="#fff" fontSize={16}>x</text>
            <text x={210} y={30} fill="#fff" fontSize={16}>y</text>
            <text x={205} y={215} fill="#b0bec5" fontSize={14}>0</text>
          </g>

          {/* Hyperbola */}
          <path d={path1} fill="none" stroke="#4fc3f7" strokeWidth={3}
            strokeDasharray={curveLength} strokeDashoffset={curveDrawn} />
          <path d={path2} fill="none" stroke="#4fc3f7" strokeWidth={3}
            strokeDasharray={curveLength} strokeDashoffset={curveDrawn} />

          {/* Circle around origin */}
          <circle cx={200} cy={200} r={25} fill="none" stroke="#ef5350" strokeWidth={3}
            opacity={circleO} transform={`scale(${circleScale})`} style={{ transformOrigin: '200px 200px' }} />
          <text x={230} y={235} fill="#ef5350" fontSize={14} opacity={circleO}>0 exclu ❌</text>

          {/* Highlighted x-axis (Df) */}
          <line x1={20} y1={200} x2={20 + 180 * highlightProgress} y2={200} stroke="#81c784" strokeWidth={6} strokeLinecap="round" />
          <line x1={380} y1={200} x2={380 - 180 * highlightProgress} y2={200} stroke="#81c784" strokeWidth={6} strokeLinecap="round" />

          {/* Df label */}
          <text x={300} y={170} fill="#81c784" fontSize={20} fontWeight="bold" opacity={labelO}>
            Df = ℝ \ {'{'}0{'}'}
          </text>
        </svg>
      </div>
    </AbsoluteFill>
  )
}

const Segment5 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const highlightProgress = 1
  const item1O = interpolate(frame, [fps * 0.5, fps * 1.5], [0, 1], { extrapolateRight: 'clamp' })
  const item1X = interpolate(frame, [fps * 0.5, fps * 1.5], [100, 0], { extrapolateRight: 'clamp' })
  const item2O = interpolate(frame, [fps * 2, fps * 3], [0, 1], { extrapolateRight: 'clamp' })
  const item2X = interpolate(frame, [fps * 2, fps * 3], [100, 0], { extrapolateRight: 'clamp' })
  const titleO = interpolate(frame, [0, fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill>
      <Title />
      <div style={{ display: 'flex', height: '100%', paddingTop: 80 }}>
        {/* Left: Graph */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width={320} height={320} viewBox="0 0 400 400">
            <line x1={20} y1={200} x2={380} y2={200} stroke="#fff" strokeWidth={2} />
            <line x1={200} y1={20} x2={200} y2={380} stroke="#fff" strokeWidth={2} />
            <path d="M30,350 Q100,220 180,205" fill="none" stroke="#4fc3f7" strokeWidth={3} />
            <path d="M220,195 Q300,180 370,50" fill="none" stroke="#4fc3f7" strokeWidth={3} />
            <circle cx={200} cy={200} r={20} fill="none" stroke="#ef5350" strokeWidth={2} />
            <line x1={20} y1={200} x2={20 + 180 * highlightProgress} y2={200} stroke="#81c784" strokeWidth={5} />
            <line x1={380} y1={200} x2={380 - 180 * highlightProgress} y2={200} stroke="#81c784" strokeWidth={5} />
            <text x={250} y={160} fill="#81c784" fontSize={16}>Df = ℝ \ {'{'}0{'}'}</text>
          </svg>
        </div>

        {/* Right: List */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', paddingRight: 40, gap: 24 }}>
          <h3 style={{ color: '#ef5350', fontSize: 28, margin: 0, textDecoration: 'underline', opacity: titleO }}>⛔ Cas interdits :</h3>
          
          <div style={{ opacity: item1O, transform: `translateX(${item1X}px)`, display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: '#ef5350', fontSize: 32 }}>÷</span>
            <p style={{ color: '#ffffff', fontSize: 22, margin: 0 }}>1. Division par 0 → dénominateur ≠ 0</p>
          </div>
          
          <div style={{ opacity: item2O, transform: `translateX(${item2X}px)`, display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: '#ffb74d', fontSize: 32 }}>√</span>
            <p style={{ color: '#ffffff', fontSize: 22, margin: 0 }}>2. Racine carrée de négatif → contenu ≥ 0</p>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  )
}

const Segment6 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const item3O = interpolate(frame, [fps * 0.5, fps * 1.5], [0, 1], { extrapolateRight: 'clamp' })
  const item3X = interpolate(frame, [fps * 0.5, fps * 1.5], [100, 0], { extrapolateRight: 'clamp' })
  const conclusionO = interpolate(frame, [fps * 2.5, fps * 3.5], [0, 1], { extrapolateRight: 'clamp' })
  const conclusionY = interpolate(frame, [fps * 2.5, fps * 3.5], [20, 0], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill>
      <Title />
      <div style={{ display: 'flex', height: '100%', paddingTop: 80 }}>
        {/* Left: Graph */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width={320} height={320} viewBox="0 0 400 400">
            <line x1={20} y1={200} x2={380} y2={200} stroke="#fff" strokeWidth={2} />
            <line x1={200} y1={20} x2={200} y2={380} stroke="#fff" strokeWidth={2} />
            <path d="M30,350 Q100,220 180,205" fill="none" stroke="#4fc3f7" strokeWidth={3} />
            <path d="M220,195 Q300,180 370,50" fill="none" stroke="#4fc3f7" strokeWidth={3} />
            <circle cx={200} cy={200} r={20} fill="none" stroke="#ef5350" strokeWidth={2} />
            <line x1={20} y1={200} x2={200 - 22} y2={200} stroke="#81c784" strokeWidth={5} />
            <line x1={200 + 22} y1={200} x2={380} y2={200} stroke="#81c784" strokeWidth={5} />
            <text x={250} y={160} fill="#81c784" fontSize={16}>Df = ℝ \ {'{'}0{'}'}</text>
          </svg>
        </div>

        {/* Right: Complete List */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', paddingRight: 40, gap: 20 }}>
          <h3 style={{ color: '#ef5350', fontSize: 28, margin: 0, textDecoration: 'underline' }}>⛔ Cas interdits :</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: '#ef5350', fontSize: 28 }}>÷</span>
            <p style={{ color: '#ffffff', fontSize: 20, margin: 0 }}>1. Division par 0 → dénominateur ≠ 0</p>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: '#ffb74d', fontSize: 28 }}>√</span>
            <p style={{ color: '#ffffff', fontSize: 20, margin: 0 }}>2. Racine carrée de négatif → contenu ≥ 0</p>
          </div>

          <div style={{ opacity: item3O, transform: `translateX(${item3X}px)`, display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: '#ab47bc', fontSize: 28, fontWeight: 'bold' }}>log</span>
            <p style={{ color: '#ffffff', fontSize: 20, margin: 0 }}>3. Logarithme → contenu {'>'} 0</p>
          </div>

          <div style={{ height: 2, background: '#4fc3f7', marginTop: 10, opacity: conclusionO }} />

          <p style={{
            color: '#81c784', fontSize: 24, margin: 0, fontWeight: 'bold',
            opacity: conclusionO, transform: `translateY(${conclusionY}px)`
          }}>✅ Tout le reste → forme Df</p>
        </div>
      </div>
    </AbsoluteFill>
  )
}

const Segment7 = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const bannerO = interpolate(frame, [0, fps * 1], [0, 1], { extrapolateRight: 'clamp' })
  const bannerY = interpolate(frame, [0, fps * 1], [60, 0], { extrapolateRight: 'clamp' })
  const waveO = interpolate(frame, [fps * 2, fps * 2.5], [0, 1], { extrapolateRight: 'clamp' })
  const waveRotate = Math.sin(frame * 0.3) * 15

  return (
    <AbsoluteFill>
      <Title golden />
      <div style={{ display: 'flex', height: '100%', paddingTop: 80, paddingBottom: 100 }}>
        {/* Left: Graph */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width={280} height={280} viewBox="0 0 400 400">
            <line x1={20} y1={200} x2={380} y2={200} stroke="#fff" strokeWidth={2} />
            <line x1={200} y1={20} x2={200} y2={380} stroke="#fff" strokeWidth={2} />
            <path d="M30,350 Q100,220 180,205" fill="none" stroke="#4fc3f7" strokeWidth={3} />
            <path d="M220,195 Q300,180 370,50" fill="none" stroke="#4fc3f7" strokeWidth={3} />
            <circle cx={200} cy={200} r={20} fill="none" stroke="#ef5350" strokeWidth={2} />
            <line x1={20} y1={200} x2={178} y2={200} stroke="#81c784" strokeWidth={5} />
            <line x1={222} y1={200} x2={380} y2={200} stroke="#81c784" strokeWidth={5} />
          </svg>
        </div>

        {/* Right: Complete List */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', paddingRight: 30, gap: 16 }}>
          <h3 style={{ color: '#ef5350', fontSize: 24, margin: 0, textDecoration: 'underline' }}>⛔ Cas interdits :</h3>
          <p style={{ color: '#ffffff', fontSize: 18, margin: 0 }}>1. Division par 0</p>
          <p style={{ color: '#ffffff', fontSize: 18, margin