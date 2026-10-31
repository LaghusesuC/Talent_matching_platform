import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listens on all network addresses (0.0.0.0)
    port: 5173,
    allowedHosts: true, // Allows all tunnel domains (e.g. .loca.lt, ngrok, cloudflare)
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/students': 'http://127.0.0.1:8000',
      '/jobs': 'http://127.0.0.1:8000',
      '/candidates': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
    },
  },
})
