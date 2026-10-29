import { defineConfig } from "vite";

// base "./" keeps every asset URL relative, so the build works from any GitHub Pages path
// (https://user.github.io/openbd1/) as well as from a custom domain.
export default defineConfig({
  base: "./",
  build: { outDir: "dist", target: "es2022", chunkSizeWarningLimit: 700 }, // three.js alone is ~500 kB
});
