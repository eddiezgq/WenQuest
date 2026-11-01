// 问渠轴承 web app (round 64). Served at /bearing/ on the academy domain; the API is /bearing/api/ on the same container.
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/bearing/',
  plugins: [vue()],
  server: { proxy: { '/bearing/api': { target: 'http://127.0.0.1:8000', rewrite: (p) => p.replace(/^\/bearing/, '') } } },
  build: { outDir: 'dist' },
})
