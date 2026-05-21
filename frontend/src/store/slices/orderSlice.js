import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api.js'

export const fetchOrders = createAsyncThunk('orders/fetchAll', async (params = {}, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/orders', { params })
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch orders')
  }
})

export const createOrder = createAsyncThunk('orders/create', async (payload, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/orders', payload)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to create order')
  }
})

export const fetchAdminDashboard = createAsyncThunk('orders/dashboard', async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/admin/dashboard')
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch dashboard')
  }
})

// Customer: fetch only their own orders (GET /orders/my)
export const fetchMyOrders = createAsyncThunk('orders/fetchMy', async (params = {}, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/orders/my', { params })
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch your orders')
  }
})

// Admin: update Order status
export const updateOrderStatus = createAsyncThunk('orders/updateStatus', async ({ id, status }, { rejectWithValue }) => {
  try {
    const { data } = await api.put(`/orders/${id}`, null, { params: { status } })
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to update order status')
  }
})

// Admin: update Shipment status (PREPARING → IN_TRANSIT → OUT_FOR_DELIVERY → DELIVERED)
export const updateShipmentStatus = createAsyncThunk('orders/updateShipmentStatus', async ({ id, status }, { rejectWithValue }) => {
  try {
    const { data } = await api.put(`/shipments/${id}/status`, null, { params: { status } })
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to update shipment status')
  }
})

// Customer: submit star rating (1-5) for a delivered shipment
export const rateShipment = createAsyncThunk('orders/rateShipment', async ({ id, rating }, { rejectWithValue }) => {
  try {
    const { data } = await api.put(`/shipments/${id}/rate`, null, { params: { rating } })
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to submit rating')
  }
})

const orderSlice = createSlice({
  name: 'orders',
  initialState: { items: [], dashboard: null, page: {}, loading: false, error: null },
  reducers: { clearOrderError(state) { state.error = null } },
  extraReducers: (builder) => {
    builder
      .addCase(fetchOrders.pending,    (s) => { s.loading = true; s.error = null })
      .addCase(fetchOrders.fulfilled,  (s, a) => { s.loading = false; s.items = a.payload.content || []; s.page = { totalPages: a.payload.totalPages, number: a.payload.number } })
      .addCase(fetchOrders.rejected,   (s, a) => { s.loading = false; s.error = a.payload })
      .addCase(createOrder.pending,    (s) => { s.loading = true })
      .addCase(createOrder.fulfilled,  (s, a) => { s.loading = false; s.items.unshift(a.payload) })
      .addCase(createOrder.rejected,   (s, a) => { s.loading = false; s.error = a.payload })
      .addCase(fetchAdminDashboard.pending,   (s) => { s.loading = true })
      .addCase(fetchAdminDashboard.fulfilled, (s, a) => { s.loading = false; s.dashboard = a.payload })
      .addCase(fetchAdminDashboard.rejected,  (s, a) => { s.loading = false; s.error = a.payload })
      // fetchMyOrders shares same items list
      .addCase(fetchMyOrders.pending,    (s) => { s.loading = true; s.error = null })
      .addCase(fetchMyOrders.fulfilled,  (s, a) => { s.loading = false; s.items = a.payload.content || []; s.page = { totalPages: a.payload.totalPages, number: a.payload.number } })
      .addCase(fetchMyOrders.rejected,   (s, a) => { s.loading = false; s.error = a.payload })
      .addCase(updateOrderStatus.fulfilled, (s, a) => {
        const idx = s.items.findIndex(o => o.id === a.payload.id)
        if (idx !== -1) s.items[idx] = a.payload
      })
      .addCase(updateShipmentStatus.fulfilled, (s, a) => {
        s.items.forEach(order => {
          if (order.shipment?.trackingNumber === a.payload.trackingNumber) {
            order.shipment.status = a.payload.status
          }
        })
      })
      .addCase(rateShipment.fulfilled, (s, a) => {
        s.items.forEach(order => {
          if (order.shipment?.trackingNumber === a.payload.trackingNumber) {
            order.shipment.customerRating = a.payload.customerRating
          }
        })
      })
  },
})

export const { clearOrderError } = orderSlice.actions
export default orderSlice.reducer
