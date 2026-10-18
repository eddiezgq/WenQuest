// 问渠凸轮 web app (round 39). Served at /cam/ on the academy domain; the API is /cam/api/ on the same container.
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/cam/',
  plugins: [vue()],
  server: { proxy: { '/cam/api': { target: 'http://127.0.0.1:8000', rewrite: (p) => p.replace(/^\/cam/, '') } } },
  build: { outDir: 'dist', chunkSizeWarningLimit: 900 },
})
