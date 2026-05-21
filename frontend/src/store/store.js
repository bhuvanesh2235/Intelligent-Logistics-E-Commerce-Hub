import { configureStore } from '@reduxjs/toolkit'
import authReducer    from './slices/authSlice.js'
import productReducer from './slices/productSlice.js'
import cartReducer    from './slices/cartSlice.js'
import orderReducer   from './slices/orderSlice.js'
import mlReducer      from './slices/mlSlice.js'

export const store = configureStore({
  reducer: {
    auth:     authReducer,
    products: productReducer,
    cart:     cartReducer,
    orders:   orderReducer,
    ml:       mlReducer,
  },
})
