import { resolve } from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "electron-vite";

export default defineConfig({
  main: {},
  preload: {},
  renderer: {
    resolve: {
      alias: {
        "@renderer": resolve("src/renderer"),
        "@features": resolve("src/renderer/features"),
        "@store": resolve("src/renderer/store"),
        "@lib": resolve("src/renderer/lib"),
      },
    },
    plugins: [tailwindcss(), react()],
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            "vendor-react": ["react", "react-dom", "zustand"],
            "vendor-utils": ["lucide-react", "clsx", "tailwind-merge"],
            "vendor-markdown": [
              "react-markdown",
              "rehype-highlight",
              "rehype-katex",
              "remark-breaks",
              "remark-cjk-friendly",
              "remark-gfm",
              "remark-math",
              "highlight.js",
              "katex",
            ],
          },
        },
      },
    },
  },
});
