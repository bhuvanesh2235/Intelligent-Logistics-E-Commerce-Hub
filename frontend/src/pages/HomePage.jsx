import { Link } from 'react-router-dom'
import { useSelector } from 'react-redux'

const FEATURES = [
  { icon: '📦', title: 'Smart Inventory',   desc: 'Real-time stock tracking across all warehouses' },
  { icon: '🚚', title: 'Live Tracking',     desc: 'Track every shipment from dispatch to delivery' },
  { icon: '📊', title: 'Deep Analytics',    desc: 'Intelligent insights on orders and delivery KPIs' },
  { icon: '🔐', title: 'Secure Auth',       desc: 'JWT-based authentication with role-based access' },
  { icon: '⚡', title: 'Fast Checkout',     desc: 'Streamlined ordering with smart cart management' },
  { icon: '🤖', title: 'ML Pipeline',       desc: 'AI-powered preprocessing and feature engineering' },
]

export default function HomePage() {
  const { user } = useSelector(s => s.auth)

  return (
    <div>
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(108,99,255,0.15) 0%, rgba(0,212,170,0.08) 100%)',
        border: '1px solid var(--border)', borderRadius: 24,
        padding: '48px 40px', marginBottom: 32, position: 'relative', overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', top: -40, right: -40, fontSize: 160, opacity: 0.06 }}>⚡</div>
        <div className="badge badge-info" style={{ marginBottom: 16 }}>Module 1 — Foundation</div>
        <h1 style={{ fontSize: 40, fontWeight: 900, lineHeight: 1.2, marginBottom: 16 }}>
          Intelligent Logistics<br />
          <span style={{ background: 'linear-gradient(135deg, var(--accent), var(--accent-2))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            & E-Commerce Hub
          </span>
        </h1>
        <p style={{ fontSize: 16, color: 'var(--text-secondary)', maxWidth: 500, marginBottom: 28 }}>
          A production-ready logistics platform with React, Spring Boot, MySQL, JWT Auth, and an ML preprocessing pipeline.
        </p>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <Link to="/products" className="btn btn-primary">🛍 Browse Products</Link>
          {user?.role === 'ADMIN' && (
            <Link to="/admin" className="btn btn-secondary">📊 Admin Dashboard</Link>
          )}
          <Link to="/tracking" className="btn btn-secondary">🚚 Track Shipment</Link>
        </div>
      </div>

      {/* Quick KPIs */}
      <div className="kpi-grid" style={{ marginBottom: 32 }}>
        {[
          { label: 'Tech Stack', value: '5+',   icon: '🛠', change: 'React · Spring · MySQL' },
          { label: 'API Endpoints', value: '12', icon: '🔌', change: 'Auth · Products · Orders' },
          { label: 'ML Features', value: '9',   icon: '🧠', change: 'Engineered features' },
          { label: 'Modules', value: '1/3',     icon: '🗺', change: 'Foundation complete' },
        ].map(k => (
          <div className="kpi-card" key={k.label}>
            <div className="kpi-label">{k.label}</div>
            <div className="kpi-value">{k.value}</div>
            <div className="kpi-change">{k.change}</div>
            <div className="kpi-icon">{k.icon}</div>
          </div>
        ))}
      </div>

      {/* Features */}
      <div className="page-header">
        <div>
          <div className="page-title">Platform Features</div>
          <div className="page-subtitle">Everything built in Module 1</div>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px,1fr))', gap: 16 }}>
        {FEATURES.map(f => (
          <div className="card" key={f.title} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
            <div style={{ fontSize: 32, flexShrink: 0 }}>{f.icon}</div>
            <div>
              <div style={{ fontWeight: 700, marginBottom: 6 }}>{f.title}</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{f.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
