import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchProductById, clearSelected } from '../store/slices/productSlice.js'
import { addToCart } from '../store/slices/cartSlice.js'
import { toast } from 'react-toastify'

export default function ProductDetailPage() {
  const { id } = useParams()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { selected: product, loading } = useSelector(s => s.products)

  useEffect(() => {
    dispatch(fetchProductById(id))
    return () => dispatch(clearSelected())
  }, [dispatch, id])

  const handleAddToCart = () => {
    dispatch(addToCart({ id: product.id, name: product.name, price: product.price, sku: product.sku }))
    toast.success(`${product.name} added to cart 🛒`)
  }

  if (loading) return <div className="loader"><div className="spinner" /></div>
  if (!product) return (
    <div className="empty-state">
      <div className="empty-state-icon">❌</div>
      <div className="empty-state-title">Product not found</div>
      <button className="btn btn-secondary" onClick={() => navigate('/products')}>← Back to Products</button>
    </div>
  )

  return (
    <div>
      <button className="btn btn-secondary btn-sm" onClick={() => navigate('/products')} style={{ marginBottom: 20 }}>
        ← Back to Products
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28 }}>
        {/* Image */}
        <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 120, minHeight: 300 }}>
          📦
        </div>

        {/* Details */}
        <div className="card">
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>{product.sku} · {product.categoryName}</div>
          <h1 style={{ fontSize: 26, fontWeight: 800, marginBottom: 12 }}>{product.name}</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7, marginBottom: 20 }}>
            {product.description || 'No description available.'}
          </p>

          <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
            <span className={`badge ${product.importance === 'HIGH' ? 'badge-danger' : product.importance === 'MEDIUM' ? 'badge-warning' : 'badge-muted'}`}>
              {product.importance} Priority
            </span>
            <span className="badge badge-success">In Stock: {product.stockQuantity}</span>
            <span className="badge badge-info">{product.warehouseName || 'N/A'}</span>
          </div>

          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 36, fontWeight: 900, color: 'var(--accent)' }}>
              ₹{Number(product.price).toLocaleString()}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>
              Cost price: ₹{Number(product.cost).toLocaleString()} · Weight: {product.weightGrams}g
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn btn-primary" onClick={handleAddToCart} disabled={product.stockQuantity === 0}>
              🛒 Add to Cart
            </button>
            <button className="btn btn-secondary" onClick={() => navigate('/cart')}>
              View Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
