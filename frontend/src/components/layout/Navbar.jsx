import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector } from 'react-redux'

export default function Navbar() {
  const { user } = useSelector(s => s.auth)
  const [search, setSearch] = useState('')
  const navigate = useNavigate()

  const handleSearch = (e) => {
    e.preventDefault()
    if (search.trim()) navigate(`/products?search=${encodeURIComponent(search.trim())}`)
  }

  return (
    <header className="navbar">
      <form className="navbar-search" onSubmit={handleSearch}>
        <span>🔍</span>
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search products..."
        />
      </form>
      <div className="navbar-actions">
        <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
          Welcome, <strong style={{ color: 'var(--text-primary)' }}>{user?.username}</strong>
        </span>
        <div className="avatar">
          {user?.username?.[0]?.toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  )
}
