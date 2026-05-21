import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { fetchProducts, deleteProduct, updateProduct } from '../store/slices/productSlice.js'
import { addToCart } from '../store/slices/cartSlice.js'
import { toast } from 'react-toastify'

const EMOJI = { Electronics: '💻', Clothing: '👕', 'Home & Kitchen': '🏠', Books: '📚', Sports: '⚽' }

export default function ProductsPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { items, loading, page } = useSelector(s => s.products)
  const { user } = useSelector(s => s.auth)
  const [currentPage, setCurrentPage] = useState(0)
  const [weightEdit, setWeightEdit] = useState(null) // { product, grams }

  const searchQuery = searchParams.get('search') || ''

  useEffect(() => {
    dispatch(fetchProducts({ page: currentPage, size: 12, search: searchQuery || undefined }))
  }, [dispatch, currentPage, searchQuery])

  const handleAddToCart = (product, e) => {
    e.stopPropagation()
    dispatch(addToCart({ id: product.id, name: product.name, price: product.price, sku: product.sku }))
    toast.success(`${product.name} added to cart 🛒`)
  }

  const handleDelete = async (product, e) => {
    e.stopPropagation()
    if (!window.confirm(`Delete "${product.name}"?`)) return
    const res = await dispatch(deleteProduct(product.id))
    if (deleteProduct.fulfilled.match(res)) toast.success('Product deleted')
    else toast.error('Failed to delete product')
  }

  const handleSaveWeight = async () => {
    if (!weightEdit) return
    const p = weightEdit.product
    const payload = {
      sku: p.sku, name: p.name, description: p.description,
      categoryId: p.categoryId, cost: p.cost, price: p.price,
      weightGrams: Number(weightEdit.grams),
      importance: p.importance, stockQuantity: p.stockQuantity,
      warehouseId: p.warehouseId || null,
    }
    const res = await dispatch(updateProduct({ id: p.id, payload }))
    if (updateProduct.fulfilled.match(res)) {
      toast.success(`⚖ Weight updated to ${weightEdit.grams}g`)
      setWeightEdit(null)
      dispatch(fetchProducts({ page: currentPage, size: 12 }))
    } else {
      toast.error('Failed to update weight')
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Products</h1>
          <div className="page-subtitle">
            {searchQuery ? `Search results for "${searchQuery}"` : `${page.totalElements || 0} products available`}
          </div>
        </div>
        {user?.role === 'ADMIN' && (
          <button className="btn btn-primary" onClick={() => navigate('/products/new')}>
            ➕ Add Product
          </button>
        )}
      </div>

      {loading ? (
        <div className="loader"><div className="spinner" /></div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📦</div>
          <div className="empty-state-title">No products found</div>
          <div className="empty-state-text">Try a different search or check back later.</div>
        </div>
      ) : (
        <>
          <div className="product-grid">
            {items.map(p => (
              <div key={p.id} className="product-card" onClick={() => navigate(`/products/${p.id}`)}>
                <div className="product-card-img">
                  {EMOJI[p.categoryName] || '📦'}
                </div>
                <div className="product-card-body">
                  <div className="product-card-sku">{p.sku}</div>
                  <div className="product-card-name">{p.name}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '8px 0' }}>
                    <span className={`badge ${p.importance === 'HIGH' ? 'badge-danger' : p.importance === 'MEDIUM' ? 'badge-warning' : 'badge-muted'}`}>
                      {p.importance}
                    </span>
                    <span className="badge badge-success">Stock: {p.stockQuantity}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 12 }}>
                    <div className="product-card-price">₹{Number(p.price).toLocaleString()}</div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      {user?.role === 'ADMIN' && (
                        <>
                          <button className="btn btn-secondary btn-sm"
                            title="Set weight"
                            onClick={(e) => { e.stopPropagation(); setWeightEdit({ product: p, grams: p.weightGrams || 0 }) }}>
                            ⚖
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={(e) => handleDelete(p, e)}>🗑</button>
                        </>
                      )}
                      <button className="btn btn-primary btn-sm" onClick={(e) => handleAddToCart(p, e)}>
                        🛒 Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {page.totalPages > 1 && (
            <div className="pagination">
              <button className="page-btn" disabled={currentPage === 0} onClick={() => setCurrentPage(p => p - 1)}>‹</button>
              {[...Array(page.totalPages)].map((_, i) => (
                <button key={i} className={`page-btn ${i === currentPage ? 'active' : ''}`} onClick={() => setCurrentPage(i)}>{i + 1}</button>
              ))}
              <button className="page-btn" disabled={currentPage >= page.totalPages - 1} onClick={() => setCurrentPage(p => p + 1)}>›</button>
            </div>
          )}
        </>
      )}

      {/* Weight Edit Modal */}
      {weightEdit && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex',
                      alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}
             onClick={() => setWeightEdit(null)}>
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 16,
                        padding: 32, minWidth: 320, boxShadow: '0 20px 60px rgba(0,0,0,0.4)' }}
               onClick={e => e.stopPropagation()}>
            <h3 style={{ fontWeight: 800, marginBottom: 8 }}>⚖ Set Product Weight</h3>
            <div style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 20 }}>
              {weightEdit.product.name}
            </div>
            <div className="form-group">
              <label className="form-label">Weight (grams)</label>
              <input className="form-input" type="number" min="0"
                value={weightEdit.grams}
                onChange={e => setWeightEdit(w => ({ ...w, grams: e.target.value }))}
                autoFocus />
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleSaveWeight}>
                💾 Save
              </button>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setWeightEdit(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
