import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5185,  // 跟 poi-generator(5174)、hermes(5175)、node server.cjs(8081) 都错开
    host: '127.0.0.1',  // macOS Node 默认 IPv6-only,playwright 用 127.0.0.1
    strictPort: true,
    // Phase 2: 把 /api/game/v1/* 代理到 FastAPI(8000)
    // 让前端 fetch('/api/...') 自动走 8000,无需 CORS 配浏览器端
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 不重写路径(后端已经有 /api/game/v1 前缀)
      },
      // Phase 3: 静态资源(scene 图 / audio / sprite)统一走 FastAPI StaticFiles mount
      // 不走这个 proxy 的话,vite dev 会 fallback 到 SPA index.html(返回 text/html,不是 PNG)
      '/assets': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    target: 'es2022',
    sourcemap: false,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        // 把 maplibre-gl + pmtiles 拆成独立 chunk,首屏主 chunk 不背 ~700KB
        manualChunks: {
          'maplibre-gl': ['maplibre-gl'],
          'pmtiles': ['pmtiles'],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
  },
})