import { createSlice } from '@reduxjs/toolkit'

const saved = JSON.parse(localStorage.getItem('cart') || '[]')

const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: saved },
  reducers: {
    addToCart(state, action) {
      const existing = state.items.find(i => i.id === action.payload.id)
      if (existing) {
        existing.quantity += (action.payload.quantity || 1)
      } else {
        state.items.push({ ...action.payload, quantity: action.payload.quantity || 1 })
      }
      localStorage.setItem('cart', JSON.stringify(state.items))
    },
    removeFromCart(state, action) {
      state.items = state.items.filter(i => i.id !== action.payload)
      localStorage.setItem('cart', JSON.stringify(state.items))
    },
    updateQuantity(state, action) {
      const item = state.items.find(i => i.id === action.payload.id)
      if (item) item.quantity = action.payload.quantity
      localStorage.setItem('cart', JSON.stringify(state.items))
    },
    clearCart(state) {
      state.items = []
      localStorage.removeItem('cart')
    },
  },
})

export const { addToCart, removeFromCart, updateQuantity, clearCart } = cartSlice.actions
export default cartSlice.reducer
