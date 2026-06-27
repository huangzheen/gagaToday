import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // 让 vite 5174 上的 <img src="/assets/..."> 走 8081 server.cjs
      // (server.cjs 支持 Range,用于 PMTiles,顺手也能 serve 普通图片)
      '/assets': {
        target: 'http://127.0.0.1:8081',
        changeOrigin: true,
      },
    },
  },
})
