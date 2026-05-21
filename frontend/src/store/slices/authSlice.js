import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api.js'

const saved = JSON.parse(localStorage.getItem('auth') || 'null')

export const loginUser = createAsyncThunk('auth/login', async (creds, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/auth/login', creds)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Login failed')
  }
})

export const registerUser = createAsyncThunk('auth/register', async (payload, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/auth/register', payload)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Registration failed')
  }
})

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    token:   saved?.token   || null,
    user:    saved?.user    || null,
    loading: false,
    error:   null,
  },
  reducers: {
    logout(state) {
      state.token = null
      state.user  = null
      localStorage.removeItem('auth')
    },
    clearError(state) { state.error = null },
  },
  extraReducers: (builder) => {
    const handleAuth = (state, action) => {
      state.loading = false
      state.token   = action.payload.token
      state.user    = { username: action.payload.username, email: action.payload.email, role: action.payload.role, id: action.payload.userId }
      localStorage.setItem('auth', JSON.stringify({ token: state.token, user: state.user }))
    }
    builder
      .addCase(loginUser.pending,    (s) => { s.loading = true;  s.error = null })
      .addCase(loginUser.fulfilled,  handleAuth)
      .addCase(loginUser.rejected,   (s, a) => { s.loading = false; s.error = a.payload })
      .addCase(registerUser.pending,   (s) => { s.loading = true;  s.error = null })
      .addCase(registerUser.fulfilled, handleAuth)
      .addCase(registerUser.rejected,  (s, a) => { s.loading = false; s.error = a.payload })
  },
})

export const { logout, clearError } = authSlice.actions
export default authSlice.reducer
