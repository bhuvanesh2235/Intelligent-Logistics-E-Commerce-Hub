import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { loginUser, clearError } from '../store/slices/authSlice.js'
import { toast } from 'react-toastify'

export default function LoginPage() {
  const dispatch = useDispatch()
  const { loading, error } = useSelector(s => s.auth)
  const [form, setForm] = useState({ username: '', password: '' })

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(clearError())
    const res = await dispatch(loginUser(form))
    if (loginUser.fulfilled.match(res)) {
      toast.success('Welcome back! 🎉')
    } else {
      toast.error(res.payload || 'Login failed')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">⚡ LogisticsHub</div>
        <div className="auth-tagline">Sign in to your intelligent logistics platform</div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input className="form-input" placeholder="Enter username"
              value={form.username} onChange={set('username')} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" placeholder="Enter password"
              value={form.password} onChange={set('password')} required />
          </div>
          {error && <div className="form-error" style={{ marginBottom: 12 }}>⚠ {error}</div>}
          <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
            {loading ? '⏳ Signing in...' : '🚀 Sign In'}
          </button>
        </form>

        <div className="auth-divider">or</div>

        <div style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--accent)', fontWeight: 700 }}>
            Create Account
          </Link>
        </div>

        <div style={{ marginTop: 24, padding: 14, background: 'rgba(108,99,255,0.08)', borderRadius: 10, fontSize: 12, color: 'var(--text-muted)' }}>
          <strong style={{ color: 'var(--text-secondary)' }}>Demo credentials:</strong><br />
          Admin: admin / Admin@123
        </div>
      </div>
    </div>
  )
}
