import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { createOrder } from '../store/slices/orderSlice.js'
import { clearCart } from '../store/slices/cartSlice.js'
import { toast } from 'react-toastify'

export default function CheckoutPage() {
  const { items } = useSelector(s => s.cart)
  const { loading } = useSelector(s => s.orders)
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [address, setAddress] = useState('')
  const [notes, setNotes] = useState('')

  const total = items.reduce((s, i) => s + Number(i.price) * i.quantity, 0)

  // Stock validation is handled server-side by OrderService
  const handlePlaceOrder = async (e) => {
    e.preventDefault()
    if (items.length === 0) return toast.error('Your cart is empty!')

    const payload = {
      shippingAddress: address,
      notes,
      items: items.map(i => ({ productId: i.id, quantity: i.quantity })),
    }

    const res = await dispatch(createOrder(payload))
    if (createOrder.fulfilled.match(res)) {
      dispatch(clearCart())
      toast.success('Order placed successfully! 🎉')
      navigate('/orders')
    } else {
      toast.error(res.payload || 'Failed to place order')
    }
  }

  if (items.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🛒</div>
        <div className="empty-state-title">Nothing to checkout</div>
        <button className="btn btn-primary" onClick={() => navigate('/products')}>Browse Products</button>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Checkout</h1>
          <div className="page-subtitle">Complete your order</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 24, alignItems: 'start' }}>
        <form onSubmit={handlePlaceOrder}>
          <div className="card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 20 }}>📍 Shipping Details</h2>
            <div className="form-group">
              <label className="form-label">Delivery Address</label>
              <textarea className="form-textarea" rows={4}
                placeholder="Enter your full delivery address..."
                value={address} onChange={e => setAddress(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="form-label">Order Notes (Optional)</label>
              <input className="form-input" placeholder="Special instructions..."
                value={notes} onChange={e => setNotes(e.target.value)} />
            </div>
          </div>

          <div className="card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 16 }}>💳 Payment</h2>
            <div style={{ padding: '16px', background: 'rgba(108,99,255,0.08)', borderRadius: 10, fontSize: 14, color: 'var(--text-secondary)' }}>
              💡 Payment gateway integration is planned for Module 2. Orders are placed in demo mode.
            </div>
          </div>

          <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
            {loading ? '⏳ Placing order...' : `✅ Place Order — ₹${total.toLocaleString()}`}
          </button>
        </form>

        {/* Order Summary */}
        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 16 }}>🧾 Order Summary</h2>
          {items.map(item => (
            <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
              <span>{item.name} × {item.quantity}</span>
              <span style={{ fontWeight: 700 }}>₹{(Number(item.price) * item.quantity).toLocaleString()}</span>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 900, fontSize: 18, marginTop: 16, color: 'var(--accent)' }}>
            <span>Total</span>
            <span>₹{total.toLocaleString()}</span>
          </div>
          <div style={{ marginTop: 12, fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
            A tracking number will be auto-generated after order placement.
          </div>
        </div>
      </div>
    </div>
  )
}
