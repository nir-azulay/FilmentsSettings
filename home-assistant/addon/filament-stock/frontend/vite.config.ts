import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "./" produces relative asset URLs so the bundle works regardless of
// the URL prefix Home Assistant Ingress mounts the add-on under.
export default defineConfig({
  base: "./",
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
