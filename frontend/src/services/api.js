import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Read token from localStorage (already persisted by authSlice) —
// avoids the circular import: api → store → authSlice → api
api.interceptors.request.use((config) => {
  const saved = JSON.parse(localStorage.getItem('auth') || 'null')
  const token = saved?.token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect without dispatching to store
      // (store may not be initialized yet due to circular dep)
      localStorage.removeItem('auth')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
