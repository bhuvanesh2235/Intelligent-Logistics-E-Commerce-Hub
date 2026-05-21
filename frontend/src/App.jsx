import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import AppLayout from './components/layout/AppLayout.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import HomePage from './pages/HomePage.jsx'
import ProductsPage from './pages/ProductsPage.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'
import CartPage from './pages/CartPage.jsx'
import CheckoutPage from './pages/CheckoutPage.jsx'
import OrdersPage from './pages/OrdersPage.jsx'
import ShipmentTrackingPage from './pages/ShipmentTrackingPage.jsx'
import AdminDashboardPage from './pages/AdminDashboardPage.jsx'
import ForecastDashboard from './pages/ForecastDashboard.jsx'
import DamageDetectionPage from './pages/DamageDetectionPage.jsx'
import ProductNewPage from './pages/ProductNewPage.jsx'

function ProtectedRoute({ children, adminOnly = false }) {
  const { token, user } = useSelector(s => s.auth)
  if (!token) return <Navigate to="/login" replace />
  if (adminOnly && user?.role !== 'ADMIN') return <Navigate to="/" replace />
  return children
}

export default function App() {
  const { token } = useSelector(s => s.auth)
  return (
    <Routes>
      <Route path="/login"    element={!token ? <LoginPage />    : <Navigate to="/" />} />
      <Route path="/register" element={!token ? <RegisterPage /> : <Navigate to="/" />} />
      <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index element={<HomePage />} />
        <Route path="products"      element={<ProductsPage />} />
        <Route path="products/new"  element={<ProtectedRoute adminOnly><ProductNewPage /></ProtectedRoute>} />
        <Route path="products/:id"  element={<ProductDetailPage />} />
        <Route path="cart"        element={<CartPage />} />
        <Route path="checkout"    element={<CheckoutPage />} />
        <Route path="orders"      element={<OrdersPage />} />
        <Route path="tracking"    element={<ShipmentTrackingPage />} />
        <Route path="admin"       element={<ProtectedRoute adminOnly><AdminDashboardPage /></ProtectedRoute>} />
        <Route path="forecast"    element={<ProtectedRoute adminOnly><ForecastDashboard /></ProtectedRoute>} />
        <Route path="damage"      element={<ProtectedRoute adminOnly><DamageDetectionPage /></ProtectedRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

