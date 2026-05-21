import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { removeFromCart, updateQuantity, clearCart } from '../store/slices/cartSlice.js'

export default function CartPage() {
  const { items } = useSelector(s => s.cart)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const total = items.reduce((sum, i) => sum + Number(i.price) * i.quantity, 0)

  if (items.length === 0) return (
    <div className="empty-state">
      <div className="empty-state-icon">🛒</div>
      <div className="empty-state-title">Your cart is empty</div>
      <div className="empty-state-text">Add some products to get started.</div>
      <button className="btn btn-primary" onClick={() => navigate('/products')}>🛍 Browse Products</button>
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Shopping Cart</h1>
          <div className="page-subtitle">{items.length} item(s)</div>
        </div>
        <button className="btn btn-danger btn-sm" onClick={() => dispatch(clearCart())}>🗑 Clear Cart</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 24, alignItems: 'start' }}>
        {/* Items */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Price</th>
                  <th>Qty</th>
                  <th>Subtotal</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{item.name}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{item.sku}</div>
                    </td>
                    <td>₹{Number(item.price).toLocaleString()}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <button className="page-btn" onClick={() => item.quantity > 1 ? dispatch(updateQuantity({ id: item.id, quantity: item.quantity - 1 })) : dispatch(removeFromCart(item.id))}>−</button>
                        <span style={{ fontWeight: 700, minWidth: 20, textAlign: 'center' }}>{item.quantity}</span>
                        <button className="page-btn" onClick={() => dispatch(updateQuantity({ id: item.id, quantity: item.quantity + 1 }))}>+</button>
                      </div>
                    </td>
                    <td style={{ fontWeight: 700, color: 'var(--accent)' }}>
                      ₹{(Number(item.price) * item.quantity).toLocaleString()}
                    </td>
                    <td>
                      <button className="btn btn-danger btn-sm" onClick={() => dispatch(removeFromCart(item.id))}>🗑</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Summary */}
        <div className="card">
          <h2 style={{ fontSize: 18, fontWeight: 800, marginBottom: 20 }}>Order Summary</h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: 14, color: 'var(--text-secondary)' }}>
            <span>Subtotal ({items.reduce((s, i) => s + i.quantity, 0)} items)</span>
            <span>₹{total.toLocaleString()}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: 14, color: 'var(--text-secondary)' }}>
            <span>Shipping</span><span style={{ color: 'var(--accent-2)' }}>FREE</span>
          </div>
          <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 900, fontSize: 20, marginBottom: 24 }}>
            <span>Total</span>
            <span style={{ color: 'var(--accent)' }}>₹{total.toLocaleString()}</span>
          </div>
          <button className="btn btn-primary btn-full" onClick={() => navigate('/checkout')}>
            🚀 Proceed to Checkout
          </button>
          <button className="btn btn-secondary btn-full" onClick={() => navigate('/products')} style={{ marginTop: 10 }}>
            ← Continue Shopping
          </button>
        </div>
      </div>
    </div>
  )
}
