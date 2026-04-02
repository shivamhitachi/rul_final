import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/influx': {
        target: 'http://10.0.0.17:8181', // Your internal InfluxDB address
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/influx/, '')
      }
    }
  }
})