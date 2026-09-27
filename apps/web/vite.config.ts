import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";

// In development the web app calls /api on the same origin; forward it to the gateway.
export default defineConfig({
  plugins: [uni()],
  server: {
    port: 5173,
    proxy: { "/api": { target: process.env.WQ_GATEWAY || "http://localhost:8090", changeOrigin: true } },
  },
});
