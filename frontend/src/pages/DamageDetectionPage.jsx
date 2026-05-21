/* DamageDetectionPage.jsx — CNN Package Damage Detection Dashboard */
import { useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { detectDamage, clearDamageResult } from '../store/slices/mlSlice.js'

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100)
  const col  = pct > 80 ? '#00d4aa' : pct > 60 ? '#ffa502' : '#e94560'
  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 13, color: '#a0a0c0' }}>
        <span>Confidence</span><span style={{ color: col, fontWeight: 700 }}>{pct}%</span>
      </div>
      <div style={{ background: '#2a2a4a', borderRadius: 8, height: 8, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, background: `linear-gradient(90deg,${col},${col}88)`, height: '100%', borderRadius: 8, transition: 'width 0.6s ease' }} />
      </div>
    </div>
  )
}

function PredictionBadge({ prediction }) {
  const isDamaged = prediction?.toLowerCase().includes('damaged') && !prediction?.toLowerCase().includes('non')
  return (
    <span style={{
      display: 'inline-block', padding: '6px 18px', borderRadius: 20, fontWeight: 800, fontSize: 15,
      background: isDamaged ? '#e9456033' : '#00d4aa33',
      color:      isDamaged ? '#e94560'   : '#00d4aa',
      border:     `2px solid ${isDamaged ? '#e94560' : '#00d4aa'}`,
    }}>
      {isDamaged ? '⚠️ Damaged' : '✅ Intact'}
    </span>
  )
}

export default function DamageDetectionPage() {
  const dispatch = useDispatch()
  const { damageResult, damageHistory, damageLoading, damageError } = useSelector(s => s.ml)
  const [preview, setPreview] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) return
    setPreview(URL.createObjectURL(file))
    dispatch(clearDamageResult())
    const fd = new FormData()
    fd.append('image', file)
    dispatch(detectDamage(fd))
  }

  const onDrop = (e) => {
    e.preventDefault(); setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Damage Detection</h1>
          <div className="page-subtitle">CNN-powered parcel damage classification (MobileNetV2)</div>
        </div>
        <span style={{ background: '#6c63ff22', color: '#6c63ff', padding: '6px 14px', borderRadius: 20, fontSize: 13, fontWeight: 700 }}>
          Model: MobileNetV2
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* Upload Panel */}
        <div className="card">
          <h3 style={{ fontWeight: 800, marginBottom: 16 }}>📤 Upload Package Image</h3>
          <div
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => fileRef.current.click()}
            style={{
              border: `2px dashed ${dragOver ? '#6c63ff' : '#2a2a4a'}`,
              borderRadius: 12, padding: '32px 20px', textAlign: 'center',
              cursor: 'pointer', transition: 'all 0.2s',
              background: dragOver ? '#6c63ff11' : '#16213e',
              marginBottom: 16,
            }}
          >
            <div style={{ fontSize: 48, marginBottom: 12 }}>📦</div>
            <div style={{ color: '#a0a0c0', fontSize: 14 }}>
              Drag &amp; drop an image here, or <span style={{ color: '#6c63ff' }}>click to browse</span>
            </div>
            <div style={{ color: '#666', fontSize: 12, marginTop: 8 }}>JPG, PNG, BMP, WebP — max 16MB</div>
          </div>
          <input ref={fileRef} type="file" accept="image/*" hidden onChange={e => handleFile(e.target.files[0])} />

          {preview && (
            <div style={{ textAlign: 'center' }}>
              <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: 280, borderRadius: 10, border: '2px solid #2a2a4a', objectFit: 'contain' }} />
            </div>
          )}
        </div>

        {/* Result Panel */}
        <div className="card">
          <h3 style={{ fontWeight: 800, marginBottom: 16 }}>🧠 CNN Prediction Result</h3>

          {damageLoading && (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <div className="spinner" style={{ margin: '0 auto 16px' }} />
              <div style={{ color: '#6c63ff', fontSize: 14 }}>Running MobileNetV2 inference…</div>
            </div>
          )}

          {damageError && (
            <div style={{ background: '#e9456022', border: '1px solid #e94560', borderRadius: 10, padding: 16, color: '#e94560' }}>
              ⚠️ API Error: {damageError}
              <div style={{ fontSize: 12, marginTop: 8, color: '#a0a0c0' }}>Start Flask API: python ml-damage-detection/app.py</div>
            </div>
          )}

          {!damageLoading && !damageError && !damageResult && (
            <div style={{ textAlign: 'center', padding: 60, color: '#a0a0c0' }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
              Upload an image to run damage detection
            </div>
          )}

          {damageResult && !damageLoading && (
            <div>
              <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <PredictionBadge prediction={damageResult.prediction} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                {[
                  { label: 'Prediction',    value: damageResult.prediction },
                  { label: 'Damage Prob',   value: `${(damageResult.damage_prob * 100).toFixed(1)}%` },
                  { label: 'Response Time', value: `${damageResult.response_time_ms}ms` },
                  { label: 'Class Index',   value: damageResult.class_index },
                ].map(({ label, value }) => (
                  <div key={label} style={{ background: '#1a1a35', borderRadius: 8, padding: '12px 14px' }}>
                    <div style={{ color: '#a0a0c0', fontSize: 11, marginBottom: 4 }}>{label}</div>
                    <div style={{ color: 'white', fontWeight: 700, fontSize: 15 }}>{value}</div>
                  </div>
                ))}
              </div>
              <ConfidenceBar value={damageResult.confidence} />
            </div>
          )}
        </div>
      </div>

      {/* Prediction History */}
      <div className="card">
        <h3 style={{ fontWeight: 800, marginBottom: 16 }}>📋 Prediction History</h3>
        {damageHistory.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 32 }}>No predictions yet</div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr>
                  {['#', 'Time', 'Prediction', 'Confidence', 'Damage Prob', 'Inference'].map(h => (
                    <th key={h} style={{ padding: '10px 12px', textAlign: 'left', color: '#a0a0c0', borderBottom: '1px solid #2a2a4a', fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {damageHistory.map((r, i) => {
                  const isDmg = r.prediction?.toLowerCase().includes('damaged') && !r.prediction?.toLowerCase().includes('non')
                  return (
                    <tr key={r.id} style={{ borderBottom: '1px solid #2a2a4a' }}>
                      <td style={{ padding: '10px 12px', color: '#a0a0c0' }}>{damageHistory.length - i}</td>
                      <td style={{ padding: '10px 12px', color: '#a0a0c0' }}>{r.timestamp}</td>
                      <td style={{ padding: '10px 12px' }}>
                        <span style={{ color: isDmg ? '#e94560' : '#00d4aa', fontWeight: 700 }}>
                          {isDmg ? '⚠️' : '✅'} {r.prediction}
                        </span>
                      </td>
                      <td style={{ padding: '10px 12px', color: 'white' }}>{(r.confidence * 100).toFixed(1)}%</td>
                      <td style={{ padding: '10px 12px', color: isDmg ? '#e94560' : '#00d4aa' }}>{(r.damage_prob * 100).toFixed(1)}%</td>
                      <td style={{ padding: '10px 12px', color: '#a0a0c0' }}>{r.response_time_ms}ms</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
