import { NavLink, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { logout } from '../../store/slices/authSlice.js'

const NAV = [
  { to: '/',         icon: '🏠', label: 'Home' },
  { to: '/products', icon: '📦', label: 'Products' },
  { to: '/cart',     icon: '🛒', label: 'Cart' },
  { to: '/orders',   icon: '📋', label: 'My Orders' },
  { to: '/tracking', icon: '🚚', label: 'Track Shipment' },
]

const ADMIN_NAV = [
  { to: '/admin',    icon: '📊', label: 'Admin Dashboard' },
]

const AI_NAV = [
  { to: '/forecast', icon: '📈', label: 'AI Forecast' },
  { to: '/damage',   icon: '🔍', label: 'Damage Detection' },
]

export default function Sidebar() {
  const { user } = useSelector(s => s.auth)
  const { items } = useSelector(s => s.cart)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-text">⚡ LogisticsHub</div>
        <div className="sidebar-logo-sub">Intelligent E-Commerce</div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Main Menu</div>
        {NAV.map(({ to, icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">{icon}</span>
            {label}
            {label === 'Cart' && items.length > 0 && (
              <span className="badge badge-info" style={{ marginLeft: 'auto', fontSize: 10 }}>
                {items.reduce((s, i) => s + i.quantity, 0)}
              </span>
            )}
          </NavLink>
        ))}

        {user?.role === 'ADMIN' && (
          <>
            <div className="nav-section-label" style={{ marginTop: 16 }}>Administration</div>
            {ADMIN_NAV.map(({ to, icon, label }) => (
              <NavLink key={to} to={to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <span className="nav-icon">{icon}</span>{label}
              </NavLink>
            ))}
            <div className="nav-section-label" style={{ marginTop: 16 }}>AI Modules</div>
            {AI_NAV.map(({ to, icon, label }) => (
              <NavLink key={to} to={to}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <span className="nav-icon">{icon}</span>{label}
              </NavLink>
            ))}
          </>
        )}
      </nav>

      <div className="sidebar-footer">
        <div style={{ padding: '10px 14px', marginBottom: 8, borderRadius: 10, background: 'rgba(108,99,255,0.08)' }}>
          <div style={{ fontSize: 13, fontWeight: 700 }}>{user?.username}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{user?.role}</div>
        </div>
        <button className="nav-item" onClick={handleLogout} style={{ color: 'var(--accent-3)' }}>
          <span className="nav-icon">🚪</span> Logout
        </button>
      </div>
    </aside>
  )
}
