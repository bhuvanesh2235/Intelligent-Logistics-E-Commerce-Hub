import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { createProduct } from '../store/slices/productSlice.js'
import { toast } from 'react-toastify'

const IMPORTANCE = ['LOW', 'MEDIUM', 'HIGH']

// Sample categories from schema seed data — admin can adjust IDs
const CATEGORY_HINTS = [
  { id: 1, name: 'Electronics' },
  { id: 2, name: 'Clothing & Apparel' },
  { id: 3, name: 'Home & Garden' },
  { id: 4, name: 'Sports & Outdoors' },
  { id: 5, name: 'Books & Media' },
]

const empty = {
  sku: '', name: '', description: '',
  categoryId: '', cost: '', price: '',
  weightGrams: 0, importance: 'MEDIUM',
  stockQuantity: 0, warehouseId: '',
}

export default function ProductNewPage() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [form, setForm] = useState(empty)
  const [loading, setLoading] = useState(false)

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.categoryId) return toast.error('Please enter a Category ID')
    setLoading(true)
    const payload = {
      ...form,
      categoryId:    Number(form.categoryId),
      cost:          Number(form.cost),
      price:         Number(form.price),
      weightGrams:   Number(form.weightGrams),
      stockQuantity: Number(form.stockQuantity),
      warehouseId:   form.warehouseId ? Number(form.warehouseId) : null,
    }
    const res = await dispatch(createProduct(payload))
    setLoading(false)
    if (createProduct.fulfilled.match(res)) {
      toast.success(`✅ Product "${res.payload.name}" created!`)
      navigate('/products')
    } else {
      toast.error(res.payload || 'Failed to create product')
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">➕ Add New Product</h1>
          <div className="page-subtitle">Create a new inventory listing</div>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => navigate('/products')}>
          ← Back to Products
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 24, alignItems: 'start' }}>
        <form onSubmit={handleSubmit}>
          {/* Basic Info */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 20 }}>📦 Basic Information</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="form-group">
                <label className="form-label">SKU *</label>
                <input className="form-input" placeholder="e.g. ELEC-001" value={form.sku}
                  onChange={set('sku')} required maxLength={50} />
              </div>
              <div className="form-group">
                <label className="form-label">Product Name *</label>
                <input className="form-input" placeholder="Product name" value={form.name}
                  onChange={set('name')} required maxLength={200} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea className="form-textarea" rows={3} placeholder="Product description..."
                value={form.description} onChange={set('description')} />
            </div>
          </div>

          {/* Pricing */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 20 }}>💰 Pricing & Stock</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
              <div className="form-group">
                <label className="form-label">Cost Price (₹) *</label>
                <input className="form-input" type="number" min="0.01" step="0.01"
                  placeholder="0.00" value={form.cost} onChange={set('cost')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Selling Price (₹) *</label>
                <input className="form-input" type="number" min="0.01" step="0.01"
                  placeholder="0.00" value={form.price} onChange={set('price')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Stock Quantity</label>
                <input className="form-input" type="number" min="0"
                  value={form.stockQuantity} onChange={set('stockQuantity')} />
              </div>
            </div>
          </div>

          {/* Logistics */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 20 }}>🚚 Logistics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 16 }}>
              <div className="form-group">
                <label className="form-label">Category ID *</label>
                <input className="form-input" type="number" min="1"
                  placeholder="e.g. 1" value={form.categoryId} onChange={set('categoryId')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Warehouse ID</label>
                <input className="form-input" type="number" min="1"
                  placeholder="Optional" value={form.warehouseId} onChange={set('warehouseId')} />
              </div>
              <div className="form-group">
                <label className="form-label">Weight (grams)</label>
                <input className="form-input" type="number" min="0"
                  value={form.weightGrams} onChange={set('weightGrams')} />
              </div>
              <div className="form-group">
                <label className="form-label">Importance</label>
                <select className="form-input" value={form.importance} onChange={set('importance')}>
                  {IMPORTANCE.map(i => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
            </div>
          </div>

          <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
            {loading ? '⏳ Creating...' : '✅ Create Product'}
          </button>
        </form>

        {/* Category Reference */}
        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 800, marginBottom: 12 }}>📁 Category IDs</h3>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 2 }}>
            {CATEGORY_HINTS.map(c => (
              <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>{c.name}</span>
                <span style={{ fontWeight: 700, color: 'var(--accent)' }}>ID: {c.id}</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 16, padding: 12, background: 'rgba(108,99,255,0.08)', borderRadius: 8, fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
            💡 Warehouse ID is optional. Leave blank if not assigning to a specific warehouse.
          </div>
        </div>
      </div>
    </div>
  )
}
