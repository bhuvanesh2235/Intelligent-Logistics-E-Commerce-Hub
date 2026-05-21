import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Spring Boot backend
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        // Exclude ML API paths — they go to Flask directly
        bypass: (req) => {
          if (req.url.startsWith('/api/v2') || req.url.startsWith('/api/v3')) return req.url
        },
      },
    },
  },
  define: {
    // Fallback values if .env is not present
    'import.meta.env.VITE_FORECAST_API_URL': JSON.stringify(process.env.VITE_FORECAST_API_URL || 'http://localhost:5001'),
    'import.meta.env.VITE_DAMAGE_API_URL':   JSON.stringify(process.env.VITE_DAMAGE_API_URL   || 'http://localhost:5002'),
  },
})

