import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// As telas falam com a API em Python (porta 8010). Em desenvolvimento, o Vite repassa /api para lá.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { proxy: { "/api": "http://127.0.0.1:8010" } },
});
