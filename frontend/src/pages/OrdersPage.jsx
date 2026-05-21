import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchOrders, fetchMyOrders, updateOrderStatus, updateShipmentStatus, rateShipment } from '../store/slices/orderSlice.js'
import { toast } from 'react-toastify'

const ORDER_STATUSES   = ['PENDING','CONFIRMED','PROCESSING','SHIPPED','DELIVERED','CANCELLED']
const SHIP_STATUSES    = ['PREPARING','IN_TRANSIT','OUT_FOR_DELIVERY','DELIVERED','FAILED']
const STATUS_COLOR = {
  PENDING:'badge-warning', CONFIRMED:'badge-info', PROCESSING:'badge-info',
  SHIPPED:'badge-info', DELIVERED:'badge-success', CANCELLED:'badge-danger',
  PREPARING:'badge-warning', IN_TRANSIT:'badge-info', OUT_FOR_DELIVERY:'badge-info', FAILED:'badge-danger',
}

/* ── Star Rating Component ─────────────────────────────────── */
function StarRating({ value, onChange, readonly = false }) {
  const [hover, setHover] = useState(0)
  return (
    <div style={{ display: 'flex', gap: 2 }}>
      {[1,2,3,4,5].map(star => (
        <span
          key={star}
          onClick={() => !readonly && onChange(star)}
          onMouseEnter={() => !readonly && setHover(star)}
          onMouseLeave={() => !readonly && setHover(0)}
          style={{
            fontSize: 20, cursor: readonly ? 'default' : 'pointer',
            color: star <= (hover || value || 0) ? '#ffd700' : '#3a3a5c',
            transition: 'color 0.15s',
          }}
        >★</span>
      ))}
    </div>
  )
}

/* ── Status Row Controls (Admin) ───────────────────────────── */
function AdminStatusControls({ order }) {
  const dispatch = useDispatch()
  const [orderSt,  setOrderSt]  = useState(order.status)
  const [shipSt,   setShipSt]   = useState(order.shipment?.status || 'PREPARING')
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    const promises = []
    if (orderSt !== order.status)
      promises.push(dispatch(updateOrderStatus({ id: order.id, status: orderSt })))
    if (order.shipment?.id && shipSt !== order.shipment.status)
      promises.push(dispatch(updateShipmentStatus({ id: order.shipment.id, status: shipSt })))
    const results = await Promise.all(promises)
    setSaving(false)
    const failed = results.some(r => r.error)
    failed ? toast.error('Failed to update status') : toast.success('✅ Status updated')
  }

  const changed = orderSt !== order.status || (order.shipment?.id && shipSt !== order.shipment.status)

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
      <select
        value={orderSt} onChange={e => setOrderSt(e.target.value)}
        style={{ background: '#1a1a35', border: '1px solid #3a3a5c', color: '#e0e0ff',
                 borderRadius: 6, padding: '4px 8px', fontSize: 12 }}>
        {ORDER_STATUSES.map(s => <option key={s}>{s}</option>)}
      </select>
      {order.shipment && (
        <select
          value={shipSt} onChange={e => setShipSt(e.target.value)}
          style={{ background: '#1a1a35', border: '1px solid #3a3a5c', color: '#e0e0ff',
                   borderRadius: 6, padding: '4px 8px', fontSize: 12 }}>
          {SHIP_STATUSES.map(s => <option key={s}>{s}</option>)}
        </select>
      )}
      <button
        className="btn btn-primary btn-sm"
        onClick={save} disabled={!changed || saving}
        style={{ whiteSpace: 'nowrap' }}>
        {saving ? '⏳' : '💾 Save'}
      </button>
    </div>
  )
}

/* ── Customer Star Rating ──────────────────────────────────── */
function CustomerRating({ order }) {
  const dispatch = useDispatch()
  const existing = order.shipment?.customerRating || 0
  const [rating, setRating] = useState(existing)
  const [submitted, setSubmitted] = useState(existing > 0)

  const submit = async (stars) => {
    setRating(stars)
    if (!order.shipment?.id) return
    const res = await dispatch(rateShipment({ id: order.shipment.id, rating: stars }))
    if (rateShipment.fulfilled.match(res)) {
      setSubmitted(true)
      toast.success('⭐ Thank you for your rating!')
    } else {
      toast.error('Failed to submit rating')
    }
  }

  const isDelivered = order.status === 'DELIVERED' || order.shipment?.status === 'DELIVERED'
  if (!isDelivered) return <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>—</span>
  return (
    <div>
      <StarRating value={rating} onChange={submit} readonly={submitted} />
      {submitted && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Rated {rating}/5</div>}
    </div>
  )
}

/* ── Main Page ─────────────────────────────────────────────── */
export default function OrdersPage() {
  const dispatch = useDispatch()
  const { items: orders, loading } = useSelector(s => s.orders)
  const { user } = useSelector(s => s.auth)
  const isAdmin = user?.role === 'ADMIN'
  const loadOrders = () => dispatch(isAdmin ? fetchOrders({ page: 0, size: 50 }) : fetchMyOrders({ page: 0, size: 50 }))

  useEffect(() => { loadOrders() }, [dispatch, isAdmin])

  if (loading) return <div className="loader"><div className="spinner" /></div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">{isAdmin ? '📋 All Orders' : '📋 My Orders'}</h1>
          <div className="page-subtitle">{orders.length} orders found</div>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={loadOrders}>
          🔄 Refresh
        </button>
      </div>

      {orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-title">No orders yet</div>
          <div className="empty-state-text">Place your first order to see it here.</div>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Order #</th>
                  {isAdmin && <th>Customer</th>}
                  <th>Date</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Tracking</th>
                  {isAdmin ? (
                    <th style={{ minWidth: 340 }}>Status Management</th>
                  ) : (
                    <>
                      <th>Status</th>
                      <th>Shipment</th>
                      <th>Your Rating</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id}>
                    <td>
                      <div style={{ fontWeight: 700, color: 'var(--accent)' }}>{order.orderNumber}</div>
                    </td>
                    {isAdmin && (
                      <td>
                        <span style={{ fontSize: 12, fontWeight: 700, color: '#e8e8ff', letterSpacing: '0.5px' }}>
                          {order.customerName || '—'}
                        </span>
                      </td>
                    )}
                    <td>
                      <span style={{ fontSize: 12, fontWeight: 700, color: '#e8e8ff', letterSpacing: '0.5px' }}>
                        {order.createdAt ? new Date(order.createdAt).toLocaleDateString('en-IN') : '—'}
                      </span>
                    </td>
                    <td style={{ fontSize: 13 }}>{order.items?.length || 0} item(s)</td>
                    <td style={{ fontWeight: 700 }}>₹{Number(order.totalAmount).toLocaleString()}</td>
                    <td>
                      <span style={{ fontSize: 12, fontWeight: 700, color: '#e8e8ff', letterSpacing: '0.5px', fontFamily: 'monospace' }}>
                        {order.shipment?.trackingNumber || '—'}
                      </span>
                    </td>
                    {isAdmin ? (
                      <td><AdminStatusControls order={order} /></td>
                    ) : (
                      <>
                        <td>
                          <span className={`badge ${STATUS_COLOR[order.status] || 'badge-muted'}`}>
                            {order.status}
                          </span>
                        </td>
                        <td>
                          {order.shipment ? (
                            <span className={`badge ${STATUS_COLOR[order.shipment.status] || 'badge-muted'}`}>
                              {order.shipment.status}
                            </span>
                          ) : '—'}
                        </td>
                        <td><CustomerRating order={order} /></td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
