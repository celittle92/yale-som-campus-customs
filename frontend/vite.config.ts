import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // 5173 is taken by the workspace's other Vite app on this machine.
    port: 5174,
    // The API and the images both come from the FastAPI app. Proxying in development
    // keeps the front end on one origin, so there is no API key or CORS dance in the
    // browser and no backend URL baked into the bundle.
    proxy: {
      '/api': {
        // 8000 was already taken on this machine, so the API runs on 8010.
        target: process.env.CAMPUS_CUSTOMS_API ?? 'http://127.0.0.1:8010',
        changeOrigin: true,
      },
    },
  },
})
