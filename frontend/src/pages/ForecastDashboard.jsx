/* ForecastDashboard.jsx — AI Sales & Shipment Forecasting Dashboard */
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchSalesForecast, fetchShipmentForecast } from '../store/slices/mlSlice.js'
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend, BarChart, Bar, Cell,
} from 'recharts'

const COLORS = ['#6c63ff','#00d4aa','#e94560','#ffa502','#a29bfe']

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#1a1a35', border: '1px solid #2a2a4a', borderRadius: 10, padding: '10px 14px', fontSize: 13 }}>
      <div style={{ color: '#a0a0c0', marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontWeight: 700 }}>{p.name}: {typeof p.value === 'number' ? p.value.toFixed(1) : p.value}</div>
      ))}
    </div>
  )
}

function TrendBadge({ trend }) {
  const m = { upward: ['#00d4aa','↑'], downward: ['#e94560','↓'], stable: ['#6c63ff','→'] }
  const [col, icon] = m[trend] || m.stable
  return <span style={{ background: col+'22', color: col, padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 700 }}>{icon} {trend}</span>
}

export default function ForecastDashboard() {
  const dispatch = useDispatch()
  const { salesForecast, shipmentForecast, forecastLoading, forecastError } = useSelector(s => s.ml)
  const [horizon, setHorizon] = useState(7)

  useEffect(() => {
    dispatch(fetchSalesForecast(horizon))
    dispatch(fetchShipmentForecast(horizon))
  }, [dispatch, horizon])

  const salesData = salesForecast?.chart_data?.map((d, i) => ({
    date: d.date?.slice(5) ?? `D${i+1}`, sales: d.value, upper: d.upper, lower: d.lower,
  })) ?? []

  const shipData = shipmentForecast?.chart_data?.map((d, i) => ({
    date: d.date?.slice(5) ?? `D${i+1}`, shipments: d.value,
  })) ?? []

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Forecast Dashboard</h1>
          <div className="page-subtitle">LSTM-powered sales &amp; shipment demand predictions</div>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <select value={horizon} onChange={e => setHorizon(Number(e.target.value))}
            style={{ background: '#16213e', color: 'white', border: '1px solid #2a2a4a', borderRadius: 8, padding: '8px 12px', fontSize: 14 }}>
            {[7,14,30].map(h => <option key={h} value={h}>{h}-Day Forecast</option>)}
          </select>
          <button className="btn btn-secondary btn-sm" onClick={() => { dispatch(fetchSalesForecast(horizon)); dispatch(fetchShipmentForecast(horizon)) }}>🔄 Refresh</button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        {[
          { label: 'Avg Daily Sales',     value: salesForecast?.avg_forecast?.toFixed(1)  ?? '—', icon: '📈', color: '#6c63ff', sub: `Peak Day ${salesForecast?.peak_day ?? '—'}` },
          { label: 'Peak Sales Value',    value: salesForecast?.peak_value                ?? '—', icon: '🏆', color: '#00d4aa', sub: 'Highest forecast point' },
          { label: 'Sales Trend',         value: salesForecast  ? <TrendBadge trend={salesForecast.trend}  /> : '—', icon: '📊', color: '#ffa502', sub: 'Direction' },
          { label: 'Avg Daily Shipments', value: shipmentForecast?.avg_forecast?.toFixed(1) ?? '—', icon: '🚚', color: '#e94560', sub: `Peak Day ${shipmentForecast?.peak_day ?? '—'}` },
          { label: 'Shipment Trend',      value: shipmentForecast ? <TrendBadge trend={shipmentForecast.trend} /> : '—', icon: '📦', color: '#a29bfe', sub: 'Demand direction' },
        ].map(k => (
          <div className="kpi-card" key={k.label} style={{ borderTop: `3px solid ${k.color}` }}>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
            <div className="kpi-change">{k.sub}</div>
            <div className="kpi-icon">{k.icon}</div>
          </div>
        ))}
      </div>

      {forecastError && (
        <div style={{ background: '#e9456022', border: '1px solid #e94560', borderRadius: 10, padding: '12px 16px', marginBottom: 20, color: '#e94560' }}>
          ⚠️ Forecast API offline — {forecastError}. Run: <code>python ml-forecasting/app.py</code>
        </div>
      )}

      {forecastLoading
        ? <div style={{ textAlign: 'center', padding: 40 }}><div className="spinner" style={{ margin: '0 auto 12px' }} />Loading AI forecasts…</div>
        : (
          <>
            <div className="card" style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontWeight: 800, margin: 0 }}>📈 Sales Volume Forecast</h3>
                {salesForecast && <TrendBadge trend={salesForecast.trend} />}
              </div>
              {salesData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <AreaChart data={salesData} margin={{ top: 4, right: 20, bottom: 4, left: 4 }}>
                    <defs>
                      <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6c63ff" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#6c63ff" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                    <XAxis dataKey="date" tick={{ fill: '#a0a0c0', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#a0a0c0', fontSize: 11 }} />
                    <Tooltip content={<Tip />} />
                    <Legend wrapperStyle={{ color: '#a0a0c0', fontSize: 12 }} />
                    <Area type="monotone" dataKey="upper" stroke="none" fill="#6c63ff11" name="Upper Bound" />
                    <Area type="monotone" dataKey="sales" stroke="#6c63ff" strokeWidth={2.5} fill="url(#sg)" name="Predicted Sales" dot={{ fill: '#6c63ff', r: 4 }} />
                    <Area type="monotone" dataKey="lower" stroke="none" fill="none" name="Lower Bound" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No data — start Flask API</div>}
            </div>

            <div className="card" style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontWeight: 800, margin: 0 }}>🚚 Shipment Demand Forecast</h3>
                {shipmentForecast && <TrendBadge trend={shipmentForecast.trend} />}
              </div>
              {shipData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <AreaChart data={shipData} margin={{ top: 4, right: 20, bottom: 4, left: 4 }}>
                    <defs>
                      <linearGradient id="shg" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00d4aa" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#00d4aa" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                    <XAxis dataKey="date" tick={{ fill: '#a0a0c0', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#a0a0c0', fontSize: 11 }} />
                    <Tooltip content={<Tip />} />
                    <Legend wrapperStyle={{ color: '#a0a0c0', fontSize: 12 }} />
                    <Area type="monotone" dataKey="shipments" stroke="#00d4aa" strokeWidth={2.5} fill="url(#shg)" name="Predicted Shipments" dot={{ fill: '#00d4aa', r: 4 }} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No data</div>}
            </div>

            {salesData.length > 0 && shipData.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                <div className="card">
                  <h3 style={{ fontWeight: 800, marginBottom: 16 }}>📊 Daily Sales Breakdown</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={salesData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                      <XAxis dataKey="date" tick={{ fill: '#a0a0c0', fontSize: 10 }} />
                      <YAxis tick={{ fill: '#a0a0c0', fontSize: 10 }} />
                      <Tooltip content={<Tip />} />
                      <Bar dataKey="sales" name="Sales" radius={[4,4,0,0]}>
                        {salesData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="card">
                  <h3 style={{ fontWeight: 800, marginBottom: 16 }}>📦 Daily Shipment Breakdown</h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={shipData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                      <XAxis dataKey="date" tick={{ fill: '#a0a0c0', fontSize: 10 }} />
                      <YAxis tick={{ fill: '#a0a0c0', fontSize: 10 }} />
                      <Tooltip content={<Tip />} />
                      <Bar dataKey="shipments" name="Shipments" radius={[4,4,0,0]}>
                        {shipData.map((_, i) => <Cell key={i} fill={['#00d4aa','#00b4d8','#6c63ff','#a29bfe','#ffa502'][i % 5]} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </>
        )
      }
    </div>
  )
}
