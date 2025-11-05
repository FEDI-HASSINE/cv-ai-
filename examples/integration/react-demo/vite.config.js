import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    strictPort: true, // Force le port 3000, ne pas essayer d'autres ports
    proxy: {
      // Optional: proxy API calls if needed
      // '/api': 'http://localhost:4000'
    }
  }
})
