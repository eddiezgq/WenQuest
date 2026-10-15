// Bundle the editor into dist/ (React + Excalidraw + editor; Excalidraw's fonts copied next to it, so nothing loads from a CDN).
import * as esbuild from "esbuild";
import { cpSync, rmSync, mkdirSync, copyFileSync } from "node:fs";
rmSync("dist", { recursive: true, force: true });
mkdirSync("dist", { recursive: true });
await esbuild.build({
  entryPoints: ["src/editor.jsx"], bundle: true, splitting: true, format: "esm", outdir: "dist", minify: true,
  define: { "process.env.NODE_ENV": '"production"', "process.env.IS_PREACT": '"false"' },
  loader: { ".woff2": "file", ".ttf": "file" }, jsx: "automatic", conditions: ["production"], logLevel: "warning",
});
cpSync("node_modules/@excalidraw/excalidraw/dist/prod/fonts", "dist/fonts", { recursive: true });
copyFileSync("../player.js", "dist/player.js");
copyFileSync("../../vendor/node_modules/roughjs/bundled/rough.js", "dist/rough.js");
copyFileSync("src/index.html", "dist/index.html");
console.log("built dist/");
