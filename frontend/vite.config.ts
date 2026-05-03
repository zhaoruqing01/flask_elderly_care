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
    cors: true,
    port: 5173,
    open: true,
    proxy: {
      "/api": {
        target: "http://192.168.119.129:5008",
        changeOrigin: true,
      },
    },
    allowedHosts: ["localhost", "127.0.0.1", "t546a7f9.natappfree.cc"],
  },
});
