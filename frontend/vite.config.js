import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // browser calls /api/... -> dev server forwards to FastAPI, stripping /api
      '/api': { target: 'http://localhost:8000', rewrite: p => p.replace(/^\/api/, '') },
    },
  },
})