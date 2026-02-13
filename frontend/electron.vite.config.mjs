import { resolve } from 'path'
import { defineConfig } from 'electron-vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  main: {},
  preload: {},
  renderer: {
    resolve: {
      alias: {
        '@renderer': resolve('src/renderer'),
        '@features': resolve('src/renderer/features'),
        '@store': resolve('src/renderer/store'),
        '@lib': resolve('src/renderer/lib')
      }
    },
    plugins: [react()]
  }
})
