import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        strictPort: true,  // fail loudly instead of silently moving to 3001
        proxy: {
            '/api': {
                // Use 127.0.0.1 (not localhost): on Windows 'localhost' resolves
                // to IPv6 ::1 first, but uvicorn binds IPv4 -> ECONNREFUSED.
                target: 'http://127.0.0.1:8001',
                changeOrigin: true,
                rewrite: (path) => path
            }
        }
    }
})
