import vue from "@vitejs/plugin-vue";
import path from "path";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      "/api": {
        target: "http://192.168.119.128:5008",
        changeOrigin: true,
      },
      "/generate": {
        target: "http://192.168.119.128:5008",
        changeOrigin: true,
      },
      "/clean": {
        target: "http://192.168.119.128:5008",
        changeOrigin: true,
      },
      "/train": {
        target: "http://192.168.119.128:5008",
        changeOrigin: true,
      },
    },
  },
});
