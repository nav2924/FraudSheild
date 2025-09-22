import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// If you later run inside Docker and the backend service is named "dashboard",
// set IN_DOCKER=1 and this proxy will target http://dashboard:8050.
const inDocker = !!process.env.IN_DOCKER
const target = inDocker ? 'http://dashboard:8050' : 'http://localhost:8050'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/stats': target,
      '/verify': target,
      '/decisions': target,
      '/label': target,
    },
  },
})
