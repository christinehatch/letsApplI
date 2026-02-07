import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Matches your architectural choice for the UI adapter
  root: "src/ui/app",

  server: {
    port: 5173,
    proxy: {
      // Bridges the Wall to your FastAPI bridge_server.py
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});