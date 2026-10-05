/**
 * Dev server setup. Passes /api and /media requests through to the Python
 * backend on port 8000, so the frontend can use plain relative URLs.
 */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
      "/media": "http://localhost:8000",
    },
  },
});
