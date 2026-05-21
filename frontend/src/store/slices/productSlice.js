import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api.js'

export const fetchProducts = createAsyncThunk('products/fetchAll', async (params = {}, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/products', { params })
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to fetch products')
  }
})

export const fetchProductById = createAsyncThunk('products/fetchOne', async (id, { rejectWithValue }) => {
  try {
    const { data } = await api.get(`/products/${id}`)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Product not found')
  }
})

export const createProduct = createAsyncThunk('products/create', async (payload, { rejectWithValue }) => {
  try {
    const { data } = await api.post('/products', payload)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to create product')
  }
})

export const updateProduct = createAsyncThunk('products/update', async ({ id, payload }, { rejectWithValue }) => {
  try {
    const { data } = await api.put(`/products/${id}`, payload)
    return data
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to update product')
  }
})

export const deleteProduct = createAsyncThunk('products/delete', async (id, { rejectWithValue }) => {
  try {
    await api.delete(`/products/${id}`)
    return id
  } catch (err) {
    return rejectWithValue(err.response?.data?.message || 'Failed to delete product')
  }
})

const productSlice = createSlice({
  name: 'products',
  initialState: { items: [], selected: null, page: {}, loading: false, error: null },
  reducers: { clearSelected(state) { state.selected = null } },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending,    (s) => { s.loading = true; s.error = null })
      .addCase(fetchProducts.fulfilled,  (s, a) => { s.loading = false; s.items = a.payload.content || []; s.page = { totalPages: a.payload.totalPages, number: a.payload.number, totalElements: a.payload.totalElements } })
      .addCase(fetchProducts.rejected,   (s, a) => { s.loading = false; s.error = a.payload })
      .addCase(fetchProductById.pending,   (s) => { s.loading = true })
      .addCase(fetchProductById.fulfilled, (s, a) => { s.loading = false; s.selected = a.payload })
      .addCase(fetchProductById.rejected,  (s, a) => { s.loading = false; s.error = a.payload })
      .addCase(deleteProduct.fulfilled, (s, a) => { s.items = s.items.filter(p => p.id !== a.payload) })
  },
})

export const { clearSelected } = productSlice.actions
export default productSlice.reducer
