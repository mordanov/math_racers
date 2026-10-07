import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  publicDir: "../assets",
  plugins: [react()],
  test: {
    environment: "happy-dom",
    passWithNoTests: true,
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
});
