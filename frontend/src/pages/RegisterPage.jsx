import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { registerUser, clearError } from '../store/slices/authSlice.js'
import { toast } from 'react-toastify'

export default function RegisterPage() {
  const dispatch = useDispatch()
  const { loading, error } = useSelector(s => s.auth)
  const [form, setForm] = useState({ username: '', email: '', password: '', fullName: '', phone: '' })

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    dispatch(clearError())
    const res = await dispatch(registerUser(form))
    if (registerUser.fulfilled.match(res)) {
      toast.success('Account created successfully! 🎉')
    } else {
      toast.error(res.payload || 'Registration failed')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">⚡ LogisticsHub</div>
        <div className="auth-tagline">Create your account — it's free</div>

        <form onSubmit={handleSubmit}>
          {[
            { key: 'fullName', label: 'Full Name', placeholder: 'John Doe', type: 'text' },
            { key: 'username', label: 'Username',  placeholder: 'john_doe',  type: 'text' },
            { key: 'email',    label: 'Email',     placeholder: 'john@example.com', type: 'email' },
            { key: 'phone',    label: 'Phone',     placeholder: '+91-9876543210', type: 'tel' },
            { key: 'password', label: 'Password',  placeholder: 'Min 8 characters', type: 'password' },
          ].map(({ key, label, placeholder, type }) => (
            <div className="form-group" key={key}>
              <label className="form-label">{label}</label>
              <input className="form-input" type={type} placeholder={placeholder}
                value={form[key]} onChange={set(key)}
                required={key !== 'phone'} minLength={key === 'password' ? 8 : undefined} />
            </div>
          ))}

          {error && <div className="form-error" style={{ marginBottom: 12 }}>⚠ {error}</div>}
          <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
            {loading ? '⏳ Creating account...' : '✨ Create Account'}
          </button>
        </form>

        <div className="auth-divider">or</div>
        <div style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--accent)', fontWeight: 700 }}>Sign In</Link>
        </div>
      </div>
    </div>
  )
}
