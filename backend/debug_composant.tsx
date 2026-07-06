import { useCurrentFrame, useVideoConfig, interpolate, spring, Sequence, AbsoluteFill } from 'remotion'

const IntroSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titreO = interpolate(frame, [0, fps * 0.8], [0, 1], { extrapolateRight: 'clamp' })
  const titreY = interpolate(frame, [0, fps * 0.8], [50, 0], { extrapolateRight: 'clamp' })
  const titreScale = spring({ frame, fps, config: { damping: 12, stiffness: 100 } })

  const exemples = ['11', '22', '111', '121']
  
  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40 }}>
      <h1 style={{ 
        color: '#4fc3f7', 
        fontSize: 80, 
        margin: 0, 
        opacity: titreO, 
        transform: `translateY(${titreY}px) scale(${titreScale})`,
        fontWeight: 'bold',
        textShadow: '0 0 30px #4fc3f780'
      }}>
        Palindromes
      </h1>
      <p style={{ 
        color: '#b0bec5', 
        fontSize: 28, 
        margin: 0, 
        opacity: interpolate(frame, [fps * 0.5, fps * 1.2], [0, 1], { extrapolateRight: 'clamp' }) 
      }}>
        Nombres qui se lisent dans les deux sens
      </p>
      <div style={{ display: 'flex', gap: 40, marginTop: 20 }}>
        {exemples.map((ex, i) => {
          const delay = fps * 1.5 + i * fps * 0.4
          const o = interpolate(frame, [delay, delay + fps * 0.4], [0, 1], { extrapolateRight: 'clamp' })
          const s = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 10, stiffness: 120 } })
          return (
            <div key={i} style={{
              opacity: o,
              transform: `scale(${s})`,
              background: '#4fc3f720',
              border: '2px solid #4fc3f7',
              borderRadius: 16,
              padding: '16px 32px',
              fontSize: 48,
              color: '#ffffff',
              fontWeight: 'bold'
            }}>
              {ex}
            </div>
          )
        })}
      </div>
    </AbsoluteFill>
  )
}

const SommePalindromeSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titreO = interpolate(frame, [0, fps], [0, 1], { extrapolateRight: 'clamp' })
  const titreY = interpolate(frame, [0, fps], [30, 0], { extrapolateRight: 'clamp' })

  const exemples = [
    { a: '11', b: '22', res: '33' },
    { a: '121', b: '11', res: '132' },
    { a: '55', b: '66', res: '121' }
  ]

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40 }}>
      <h2 style={{ 
        color: '#ffb74d', 
        fontSize: 48, 
        margin: 0, 
        opacity: titreO,
        transform: `translateY(${titreY}px)`,
        fontWeight: 'bold'
      }}>
        Sommes de palindromes
      </h2>

      <p style={{ 
        color: '#b0bec5', 
        fontSize: 24, 
        opacity: interpolate(frame, [fps * 0.5, fps * 1.2], [0, 1], { extrapolateRight: 'clamp' }),
        margin: 0
      }}>
        Que se passe-t-il quand on additionne des palindromes ?
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 30, marginTop: 20 }}>
        {exemples.map((ex, i) => {
          const baseDelay = fps * 2 + i * fps * 2
          const n1O = interpolate(frame, [baseDelay, baseDelay + fps * 0.3], [0, 1], { extrapolateRight: 'clamp' })
          const plusO = interpolate(frame, [baseDelay + fps * 0.3, baseDelay + fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })
          const n2O = interpolate(frame, [baseDelay + fps * 0.5, baseDelay + fps * 0.8], [0, 1], { extrapolateRight: 'clamp' })
          const egalO = interpolate(frame, [baseDelay + fps * 0.8, baseDelay + fps * 1], [0, 1], { extrapolateRight: 'clamp' })
          const resO = interpolate(frame, [baseDelay + fps * 1, baseDelay + fps * 1.3], [0, 1], { extrapolateRight: 'clamp' })
          const resScale = spring({ frame: Math.max(0, frame - baseDelay - fps * 1), fps, config: { damping: 8 } })
          
          const isPalindrome = ex.res === ex.res.split('').reverse().join('')
          
          return (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 20, fontSize: 42 }}>
              <span style={{ color: '#4fc3f7', fontWeight: 'bold', opacity: n1O }}>{ex.a}</span>
              <span style={{ color: '#b0bec5', opacity: plusO }}>+</span>
              <span style={{ color: '#4fc3f7', fontWeight: 'bold', opacity: n2O }}>{ex.b}</span>
              <span style={{ color: '#b0bec5', opacity: egalO }}>=</span>
              <span style={{ 
                color: isPalindrome ? '#81c784' : '#ef5350', 
                fontWeight: 'bold', 
                opacity: resO,
                transform: `scale(${resScale})`,
                display: 'inline-block'
              }}>{ex.res}</span>
              <span style={{ 
                fontSize: 24, 
                color: isPalindrome ? '#81c784' : '#ef5350',
                opacity: resO
              }}>
                {isPalindrome ? '✓ palindrome' : '✗ pas palindrome'}
              </span>
            </div>
          )
        })}
      </div>

      <div style={{
        opacity: interpolate(frame, [fps * 9, fps * 10], [0, 1], { extrapolateRight: 'clamp' }),
        background: '#ef535020',
        border: '2px solid #ef5350',
        borderRadius: 16,
        padding: '16px 32px',
        marginTop: 20
      }}>
        <p style={{ color: '#ef5350', fontSize: 24, margin: 0, fontWeight: 'bold' }}>
          ⚠️ La somme n'est pas toujours un palindrome !
        </p>
      </div>
    </AbsoluteFill>
  )
}

const BinaireSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titreO = interpolate(frame, [0, fps * 0.8], [0, 1], { extrapolateRight: 'clamp' })
  const schemaO = interpolate(frame, [fps, fps * 2], [0, 1], { extrapolateRight: 'clamp' })

  const conversions = [
    { dec: 9, bin: '1001', isPal: true },
    { dec: 5, bin: '101', isPal: true },
    { dec: 7, bin: '111', isPal: true }
  ]

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40 }}>
      <h2 style={{ 
        color: '#4fc3f7', 
        fontSize: 48, 
        margin: 0, 
        opacity: titreO,
        fontWeight: 'bold'
      }}>
        Palindromes en base binaire
      </h2>

      <p style={{ 
        color: '#b0bec5', 
        fontSize: 24, 
        opacity: interpolate(frame, [fps * 0.5, fps * 1.2], [0, 1], { extrapolateRight: 'clamp' }),
        margin: 0
      }}>
        Certains nombres sont palindromes en binaire !
      </p>

      <div style={{ display: 'flex', gap: 60, marginTop: 30, opacity: schemaO }}>
        {conversions.map((conv, idx) => {
          const delay = fps * 2 + idx * fps * 1.5
          const cardO = interpolate(frame, [delay, delay + fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })
          const bits = conv.bin.split('')
          
          return (
            <div key={idx} style={{ 
              textAlign: 'center', 
              opacity: cardO,
              background: '#1a1a2e',
              border: '2px solid #4fc3f7',
              borderRadius: 16,
              padding: 20
            }}>
              <div style={{ fontSize: 48, color: '#ffffff', fontWeight: 'bold', marginBottom: 10 }}>{conv.dec}</div>
              <div style={{ fontSize: 16, color: '#b0bec5', marginBottom: 15 }}>décimal</div>
              <svg width={40} height={30}><path d="M 20 0 L 20 25" stroke="#ffb74d" strokeWidth={2} /><polygon points="14,20 20,30 26,20" fill="#ffb74d" /></svg>
              <div style={{ display: 'flex', gap: 4, justifyContent: 'center', marginTop: 10 }}>
                {bits.map((bit, i) => {
                  const bitDelay = delay + fps * 0.5 + i * fps * 0.15
                  const bitO = interpolate(frame, [bitDelay, bitDelay + fps * 0.2], [0, 1], { extrapolateRight: 'clamp' })
                  return (
                    <div key={i} style={{ opacity: bitO, background: bit === '1' ? '#81c78430' : '#ef535030', border: `2px solid ${bit === '1' ? '#81c784' : '#ef5350'}`, borderRadius: 6, width: 32, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, color: bit === '1' ? '#81c784' : '#ef5350', fontWeight: 'bold' }}>{bit}</div>
                  )
                })}
              </div>
              <div style={{ fontSize: 16, color: '#81c784', marginTop: 10, opacity: interpolate(frame, [delay + fps * 1.2, delay + fps * 1.5], [0, 1], { extrapolateRight: 'clamp' }) }}>← palindrome →</div>
            </div>
          )
        })}
      </div>
    </AbsoluteFill>
  )
}

const SommeBinaireSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titreO = interpolate(frame, [0, fps], [0, 1], { extrapolateRight: 'clamp' })
  const calcDecO = interpolate(frame, [fps * 1.5, fps * 2.5], [0, 1], { extrapolateRight: 'clamp' })
  const calcBinO = interpolate(frame, [fps * 4, fps * 5], [0, 1], { extrapolateRight: 'clamp' })
  const conclusionO = interpolate(frame, [fps * 7, fps * 8], [0, 1], { extrapolateRight: 'clamp' })

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 40 }}>
      <h2 style={{ color: '#ffb74d', fontSize: 42, margin: 0, opacity: titreO, fontWeight: 'bold' }}>Somme de palindromes binaires</h2>
      <div style={{ display: 'flex', gap: 80, marginTop: 20 }}>
        <div style={{ textAlign: 'center', opacity: calcDecO }}>
          <p style={{ color: '#b0bec5', fontSize: 20, margin: '0 0 15px 0' }}>En décimal</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 15, fontSize: 48 }}>
            <span style={{ color: '#4fc3f7', fontWeight: 'bold' }}>5</span><span style={{ color: '#b0bec5' }}>+</span><span style={{ color: '#4fc3f7', fontWeight: 'bold' }}>9</span><span style={{ color: '#b0bec5' }}>=</span><span style={{ color: '#81c784', fontWeight: 'bold' }}>14</span>
          </div>
        </div>
        <div style={{ textAlign: 'center', opacity: calcBinO }}>
          <p style={{ color: '#b0bec5', fontSize: 20, margin: '0 0 15px 0' }}>En binaire</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 15, fontSize: 36 }}>
            <span style={{ color: '#4fc3f7', fontWeight: 'bold', fontFamily: 'monospace' }}>101</span><span style={{ color: '#b0bec5' }}>+</span><span style={{ color: '#4fc3f7', fontWeight: 'bold', fontFamily: 'monospace' }}>1001</span><span style={{ color: '#b0bec5' }}>=</span><span style={{ color: '#ef5350', fontWeight: 'bold', fontFamily: 'monospace' }}>1110</span>
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 40, marginTop: 30, opacity: interpolate(frame, [fps * 5.5, fps * 6.5], [0, 1], { extrapolateRight: 'clamp' }) }}>
        <p style={{ color: '#81c784', fontSize: 18, margin: 0 }}>101 ← palindrome</p>
        <p style={{ color: '#81c784', fontSize: 18, margin: 0 }}>1001 ← palindrome</p>
        <p style={{ color: '#ef5350', fontSize: 18, margin: 0 }}>1110 ← pas palindrome !</p>
      </div>
      <div style={{ opacity: conclusionO, background: '#ffb74d20', border: '2px solid #ffb74d', borderRadius: 16, padding: '20px 40px', marginTop: 30 }}>
        <p style={{ color: '#ffb74d', fontSize: 26, margin: 0, fontWeight: 'bold', textAlign: 'center' }}>La somme de palindromes binaires n'est pas forcément un palindrome !</p>
      </div>
    </AbsoluteFill>
  )
}

const ConclusionSegment = () => {
  const frame = useCurrentFrame()
  const { fps } = useVideoConfig()

  const titreO = interpolate(frame, [0, fps], [0, 1], { extrapolateRight: 'clamp' })
  const titreScale = spring({ frame, fps, config: { damping: 12 } })

  const points = [
    { text: 'Les palindromes se lisent pareil dans les deux sens', color: '#4fc3f7' },
    { text: 'La somme de palindromes décimaux peut donner un non-palindrome', color: '#ef5350' },
    { text: 'Certains nombres sont palindromes en binaire (5, 7, 9...)', color: '#81c784' },
    { text: 'Les propriétés des palindromes changent selon la base !', color: '#ffb74d' }
  ]

  return (
    <AbsoluteFill style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 30 }}>
      <h2 style={{ color: '#4fc3f7', fontSize: 56, margin: 0, opacity: titreO, transform: `scale(${titreScale})`, fontWeight: 'bold' }}>À retenir</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 20, marginTop: 20 }}>
        {points.map((point, i) => {
          const delay = fps * 1.5 + i * fps * 1.2
          const o = interpolate(frame, [delay, delay + fps * 0.5], [0, 1], { extrapolateRight: 'clamp' })
          const x = interpolate(frame, [delay, delay + fps * 0.5], [-50, 0], { extrapolateRight: 'clamp' })
          return (
            <div key={i} style={{ opacity: o, transform: `translateX(${x}px)`, display: 'flex', alignItems: 'center', gap: 15 }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: point.color }} />
              <p style={{ color: '#ffffff', fontSize: 24, margin: 0 }}>{point.text}</p>
            </div>
          )
        })}
      </div>
    </AbsoluteFill>
  )
}

export const LessonVideo = () => {
  const { fps } = useVideoConfig()
  const totalDuration = 68

  return (
    <AbsoluteFill style={{ background: '#1a1a2e', fontFamily: 'Segoe UI, sans-serif' }}>
      <Sequence from={0} durationInFrames={Math.round(10 * fps)}>
        <IntroSegment />
      </Sequence>
      <Sequence from={Math.round(10 * fps)} durationInFrames={Math.round(16 * fps)}>
        <SommePalindromeSegment />
      </Sequence>
      <Sequence from={Math.round(26 * fps)} durationInFrames={Math.round(14 * fps)}>
        <BinaireSegment />
      </Sequence>
      <Sequence from={Math.round(40 * fps)} durationInFrames={Math.round(14 * fps)}>
        <SommeBinaireSegment />
      </Sequence>
      <Sequence from={Math.round(54 * fps)} durationInFrames={Math.round(14 * fps)}>
        <ConclusionSegment />
      </Sequence>
    </AbsoluteFill>
  )
}