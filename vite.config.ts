import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import AutoImport from "unplugin-auto-import/vite";
import dotenv from "dotenv";
import * as path from "path";

dotenv.config({ path: "./.env" });

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    lib: {
      entry: "./static/client/main.tsx",
      name: "content_system",
    },
    outDir: "./static/build",
    minify: "esbuild",
    sourcemap: true,
  },
  define: {
    "process.env.NODE_ENV": '"production"',
    "process.env": {},
  },
  plugins: [
    react(),
    AutoImport({
      imports: ["react", "react-router-dom"],
      dts: true,
      eslintrc: {
        enabled: true,
      },
    }),
  ],
  resolve: {
    alias: { "@": path.resolve(__dirname, "static/client") },
  },
});
