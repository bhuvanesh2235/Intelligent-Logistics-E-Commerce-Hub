import { useState } from 'react'
import api from '../services/api.js'
import { toast } from 'react-toastify'

const STATUS_STEPS = ['PREPARING', 'IN_TRANSIT', 'OUT_FOR_DELIVERY', 'DELIVERED']

/* ── Clickable Star Rating ──────────────────────────────────── */
function StarRating({ value, onChange, readonly = false, size = 28 }) {
  const [hover, setHover] = useState(0)
  return (
    <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
      {[1, 2, 3, 4, 5].map(star => (
        <span
          key={star}
          onClick={() => !readonly && onChange(star)}
          onMouseEnter={() => !readonly && setHover(star)}
          onMouseLeave={() => !readonly && setHover(0)}
          style={{
            fontSize: size,
            cursor: readonly ? 'default' : 'pointer',
            color: star <= (hover || value || 0) ? '#ffd700' : '#3a3a5c',
            transition: 'color 0.15s, transform 0.1s',
            transform: !readonly && hover === star ? 'scale(1.2)' : 'scale(1)',
            display: 'inline-block',
          }}
        >★</span>
      ))}
      {value > 0 && (
        <span style={{ fontSize: 13, color: 'var(--text-secondary)', marginLeft: 8 }}>
          {value}/5
        </span>
      )}
    </div>
  )
}

export default function ShipmentTrackingPage() {
  const [trackingNumber, setTrackingNumber] = useState('')
  const [shipment, setShipment]             = useState(null)
  const [loading, setLoading]               = useState(false)
  const [error, setError]                   = useState(null)
  const [rating, setRating]                 = useState(0)
  const [ratingSubmitted, setRatingSubmitted] = useState(false)
  const [ratingLoading, setRatingLoading]   = useState(false)

  const handleTrack = async (e) => {
    e.preventDefault()
    if (!trackingNumber.trim()) return
    setLoading(true); setError(null); setShipment(null)
    setRating(0); setRatingSubmitted(false)
    try {
      const { data } = await api.get(`/shipments/track/${trackingNumber.trim()}`)
      setShipment(data)
      // Pre-fill existing rating if already rated
      if (data.customerRating) {
        setRating(data.customerRating)
        setRatingSubmitted(true)
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Shipment not found')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitRating = async () => {
    if (!rating || !shipment?.id) return
    setRatingLoading(true)
    try {
      await api.put(`/shipments/${shipment.id}/rate`, null, { params: { rating } })
      setRatingSubmitted(true)
      toast.success('⭐ Thank you for your rating!')
      setShipment(s => ({ ...s, customerRating: rating }))
    } catch {
      toast.error('Failed to submit rating. Please try again.')
    } finally {
      setRatingLoading(false)
    }
  }

  const currentStep = shipment ? STATUS_STEPS.indexOf(shipment.status) : -1

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">📦 Track Shipment</h1>
          <div className="page-subtitle">Enter your tracking number to get real-time updates</div>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 640, marginBottom: 28 }}>
        <form onSubmit={handleTrack} style={{ display: 'flex', gap: 12 }}>
          <input className="form-input" placeholder="Enter tracking number — starts with TRK- (e.g. TRK-AB12CD34)"
            value={trackingNumber} onChange={e => setTrackingNumber(e.target.value)} />
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ flexShrink: 0 }}>
            {loading ? '⏳' : '🔍 Track'}
          </button>
        </form>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 10 }}>
          💡 Find your <strong>TRK-...</strong> tracking number in the <em>My Orders</em> page under the Tracking column.
        </div>
        {error && <div className="form-error" style={{ marginTop: 12 }}>⚠ {error}</div>}
      </div>

      {shipment && (
        <div>
          {/* Tracking Header */}
          <div className="card" style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Tracking Number</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--accent)' }}>{shipment.trackingNumber}</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
                  Order: {shipment.orderNumber} · Mode: {shipment.mode} · Carrier: {shipment.carrier || 'N/A'}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Est. Delivery</div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  {shipment.estimatedDelivery ? new Date(shipment.estimatedDelivery).toLocaleDateString('en-IN') : 'TBD'}
                </div>
                {shipment.deliveredOnTime !== null && (
                  <span className={`badge ${shipment.deliveredOnTime ? 'badge-success' : 'badge-danger'}`} style={{ marginTop: 6 }}>
                    {shipment.deliveredOnTime ? '✅ On Time' : '⚠ Delayed'}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Progress Steps */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h3 style={{ marginBottom: 24, fontWeight: 700 }}>Delivery Progress</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
              {STATUS_STEPS.map((step, idx) => (
                <div key={step} style={{ display: 'flex', alignItems: 'center', flex: idx < STATUS_STEPS.length - 1 ? 1 : 0 }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: idx <= currentStep ? 'linear-gradient(135deg, var(--accent), #8b5cf6)' : 'var(--bg-secondary)',
                      border: `2px solid ${idx <= currentStep ? 'var(--accent)' : 'var(--border)'}`,
                      fontSize: 16, transition: 'all 0.3s',
                    }}>
                      {idx < currentStep ? '✓' : idx === 0 ? '🏭' : idx === 1 ? '🚛' : idx === 2 ? '📬' : '🏠'}
                    </div>
                    <div style={{ fontSize: 10, fontWeight: 700, color: idx <= currentStep ? 'var(--accent)' : 'var(--text-muted)', textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.5px', maxWidth: 80 }}>
                      {step.replace(/_/g, ' ')}
                    </div>
                  </div>
                  {idx < STATUS_STEPS.length - 1 && (
                    <div style={{ flex: 1, height: 2, background: idx < currentStep ? 'var(--accent)' : 'var(--border)', margin: '0 4px', marginBottom: 28 }} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Details Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 20 }}>
            {[
              { label: 'Weight',         value: shipment.weightGrams ? `${shipment.weightGrams}g` : 'N/A' },
              { label: 'Current Rating', value: shipment.customerRating ? '⭐'.repeat(shipment.customerRating) : 'Not rated' },
              { label: 'Care Calls',     value: shipment.customerCareCalls ?? 0 },
              { label: 'Discount',       value: `${shipment.discountOffered ?? 0}%` },
            ].map(d => (
              <div className="kpi-card" key={d.label}>
                <div className="kpi-label">{d.label}</div>
                <div style={{ fontSize: 20, fontWeight: 800 }}>{d.value}</div>
              </div>
            ))}
          </div>

          {/* ── Customer Rating Section ─ only when DELIVERED ── */}
          {shipment.status === 'DELIVERED' && (
            <div className="card" style={{
              background: 'linear-gradient(135deg, rgba(108,99,255,0.08), rgba(0,212,170,0.06))',
              border: '1px solid rgba(108,99,255,0.25)',
            }}>
              <h3 style={{ fontWeight: 800, marginBottom: 6 }}>
                {ratingSubmitted ? '⭐ Your Rating' : '⭐ Rate Your Delivery Experience'}
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 20 }}>
                {ratingSubmitted
                  ? 'Thank you for your feedback! You can update your rating below.'
                  : 'How was your delivery experience? Tap a star to rate.'}
              </p>

              <StarRating
                value={rating}
                onChange={setRating}
                readonly={false}
                size={36}
              />

              {rating > 0 && !ratingSubmitted && (
                <button
                  className="btn btn-primary"
                  style={{ marginTop: 20 }}
                  onClick={handleSubmitRating}
                  disabled={ratingLoading}>
                  {ratingLoading ? '⏳ Submitting...' : `✅ Submit ${rating}-Star Rating`}
                </button>
              )}

              {ratingSubmitted && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ color: '#00d4aa', fontWeight: 700, fontSize: 14, marginBottom: 12 }}>
                    ✅ Rating submitted! Click stars to update.
                  </div>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={handleSubmitRating}
                    disabled={ratingLoading || rating === shipment.customerRating}>
                    {ratingLoading ? '⏳' : '🔄 Update Rating'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
