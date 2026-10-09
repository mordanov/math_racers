import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  publicDir: "../assets",
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  test: {
    environment: "happy-dom",
    passWithNoTests: true,
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
});
