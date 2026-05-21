import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchAdminDashboard } from '../store/slices/orderSlice.js'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line, CartesianGrid,
} from 'recharts'

const COLORS = ['#6c63ff', '#00d4aa', '#ff6b6b', '#ffc107', '#a29bfe']

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#1a1a35', border: '1px solid #2a2a4a', borderRadius: 10, padding: '10px 14px', fontSize: 13 }}>
      <div style={{ color: '#a0a0c0', marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontWeight: 700 }}>{p.name}: {p.value}</div>
      ))}
    </div>
  )
}

export default function AdminDashboardPage() {
  const dispatch = useDispatch()
  const { dashboard, loading } = useSelector(s => s.orders)

  useEffect(() => { dispatch(fetchAdminDashboard()) }, [dispatch])

  if (loading) return <div className="loader"><div className="spinner" /></div>

  const orderStatusData = dashboard?.ordersByStatus
    ? Object.entries(dashboard.ordersByStatus).map(([name, value]) => ({ name, value }))
    : []

  const shipmentModeData = dashboard?.shipmentsByMode
    ? Object.entries(dashboard.shipmentsByMode).map(([name, value]) => ({ name, value }))
    : []

  // Mock trend data for demo
  const trendData = [
    { month: 'Jan', orders: 120, delivered: 98 },
    { month: 'Feb', orders: 145, delivered: 130 },
    { month: 'Mar', orders: 162, delivered: 150 },
    { month: 'Apr', orders: 189, delivered: 170 },
    { month: 'May', orders: 210, delivered: 195 },
  ]

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Admin Dashboard</h1>
          <div className="page-subtitle">Real-time logistics analytics and KPIs</div>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => dispatch(fetchAdminDashboard())}>
          🔄 Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        {[
          { label: 'Total Orders',    value: dashboard?.totalOrders    ?? '—', icon: '📋', change: 'All time' },
          { label: 'Total Products',  value: dashboard?.totalProducts  ?? '—', icon: '📦', change: 'Active listings' },
          { label: 'Total Users',     value: dashboard?.totalUsers     ?? '—', icon: '👥', change: 'Registered' },
          { label: 'Total Shipments', value: dashboard?.totalShipments ?? '—', icon: '🚚', change: 'All modes' },
          { label: 'On-Time Rate',    value: `${dashboard?.onTimeDeliveryRate ?? 0}%`, icon: '⏱', change: 'Delivery performance' },
        ].map(k => (
          <div className="kpi-card" key={k.label}>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-change">{k.change}</div>
            <div className="kpi-icon">{k.icon}</div>
          </div>
        ))}
      </div>

      {/* Charts Row 1 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* Orders by Status */}
        <div className="card">
          <h3 style={{ fontWeight: 800, marginBottom: 20 }}>📊 Orders by Status</h3>
          {orderStatusData.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={orderStatusData} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
                <XAxis dataKey="name" tick={{ fill: '#a0a0c0', fontSize: 11 }} />
                <YAxis tick={{ fill: '#a0a0c0', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" name="Orders" radius={[6, 6, 0, 0]}>
                  {orderStatusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Shipments by Mode */}
        <div className="card">
          <h3 style={{ fontWeight: 800, marginBottom: 20 }}>🚚 Shipments by Mode</h3>
          {shipmentModeData.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={shipmentModeData} dataKey="value" nameKey="name"
                  cx="50%" cy="50%" outerRadius={80} innerRadius={40} paddingAngle={4}>
                  {shipmentModeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="circle" wrapperStyle={{ color: '#a0a0c0', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Orders Trend */}
      <div className="card">
        <h3 style={{ fontWeight: 800, marginBottom: 20 }}>📈 Order & Delivery Trend (Demo)</h3>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={trendData} margin={{ top: 4, right: 20, bottom: 4, left: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
            <XAxis dataKey="month" tick={{ fill: '#a0a0c0', fontSize: 12 }} />
            <YAxis tick={{ fill: '#a0a0c0', fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: '#a0a0c0', fontSize: 12 }} />
            <Line type="monotone" dataKey="orders" stroke="#6c63ff" strokeWidth={2.5} dot={{ fill: '#6c63ff', r: 4 }} name="Total Orders" />
            <Line type="monotone" dataKey="delivered" stroke="#00d4aa" strokeWidth={2.5} dot={{ fill: '#00d4aa', r: 4 }} name="Delivered" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
