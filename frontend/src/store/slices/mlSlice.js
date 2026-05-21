// mlSlice.js — Redux Toolkit slice for ML API state
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

const FORECAST_URL = import.meta.env.VITE_FORECAST_API_URL || 'http://localhost:5001'
const DAMAGE_URL   = import.meta.env.VITE_DAMAGE_API_URL   || 'http://localhost:5002'

// ── Forecast thunks ───────────────────────────────────────────────────────────
export const fetchSalesForecast = createAsyncThunk(
  'ml/fetchSalesForecast',
  async (horizon = 7, { rejectWithValue }) => {
    try {
      const res = await fetch(`${FORECAST_URL}/api/v2/forecast/sales/quick?horizon=${horizon}`)
      if (!res.ok) throw new Error(`Forecast API error: ${res.status}`)
      return await res.json()
    } catch (err) {
      return rejectWithValue(err.message)
    }
  }
)

export const fetchShipmentForecast = createAsyncThunk(
  'ml/fetchShipmentForecast',
  async (horizon = 7, { rejectWithValue }) => {
    try {
      const res = await fetch(`${FORECAST_URL}/api/v2/forecast/shipments/quick?horizon=${horizon}`)
      if (!res.ok) throw new Error(`Forecast API error: ${res.status}`)
      return await res.json()
    } catch (err) {
      return rejectWithValue(err.message)
    }
  }
)

// ── Damage detection thunk ────────────────────────────────────────────────────
export const detectDamage = createAsyncThunk(
  'ml/detectDamage',
  async (formData, { rejectWithValue }) => {
    try {
      const res = await fetch(`${DAMAGE_URL}/api/v3/detect-damage`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || `HTTP ${res.status}`)
      }
      return await res.json()
    } catch (err) {
      return rejectWithValue(err.message)
    }
  }
)

// ── Slice ─────────────────────────────────────────────────────────────────────
const mlSlice = createSlice({
  name: 'ml',
  initialState: {
    // Forecast
    salesForecast:    null,
    shipmentForecast: null,
    forecastLoading:  false,
    forecastError:    null,
    // Damage
    damageResult:     null,
    damageHistory:    [],
    damageLoading:    false,
    damageError:      null,
  },
  reducers: {
    clearDamageResult(state) {
      state.damageResult = null
      state.damageError  = null
    },
    clearForecastError(state) {
      state.forecastError = null
    },
  },
  extraReducers: (builder) => {
    // Sales forecast
    builder
      .addCase(fetchSalesForecast.pending,   (s) => { s.forecastLoading = true;  s.forecastError = null })
      .addCase(fetchSalesForecast.fulfilled, (s, a) => { s.forecastLoading = false; s.salesForecast = a.payload })
      .addCase(fetchSalesForecast.rejected,  (s, a) => { s.forecastLoading = false; s.forecastError = a.payload })
    // Shipment forecast
    builder
      .addCase(fetchShipmentForecast.pending,   (s) => { s.forecastLoading = true })
      .addCase(fetchShipmentForecast.fulfilled, (s, a) => { s.forecastLoading = false; s.shipmentForecast = a.payload })
      .addCase(fetchShipmentForecast.rejected,  (s, a) => { s.forecastLoading = false; s.forecastError = a.payload })
    // Damage detection
    builder
      .addCase(detectDamage.pending,   (s) => { s.damageLoading = true;  s.damageError = null })
      .addCase(detectDamage.fulfilled, (s, a) => {
        s.damageLoading = false
        s.damageResult  = a.payload
        // Prepend to history (keep last 20)
        s.damageHistory = [
          { ...a.payload, id: Date.now(), timestamp: new Date().toLocaleTimeString() },
          ...s.damageHistory,
        ].slice(0, 20)
      })
      .addCase(detectDamage.rejected,  (s, a) => { s.damageLoading = false; s.damageError = a.payload })
  },
})

export const { clearDamageResult, clearForecastError } = mlSlice.actions
export default mlSlice.reducer
