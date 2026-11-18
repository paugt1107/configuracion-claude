// Renderiza una escena 3D fotograma a fotograma: node render.mjs <spec.json> <carpeta-salida> [fps]
// Escribe f00000.jpg, f00001.jpg… (1080x1920). El tiempo es exacto (no depende de la velocidad de la máquina).
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const DIR = path.dirname(fileURLToPath(import.meta.url));
const [specPath, outDir, fpsArg] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
const fps = Number(fpsArg || 30);
fs.mkdirSync(outDir, { recursive: true });

const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".otf": "font/otf" };
const server = http.createServer((req, res) => {
  const p = path.join(DIR, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!p.startsWith(DIR) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "content-type": TYPES[path.extname(p)] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
});
await new Promise((ok) => server.listen(0, "127.0.0.1", ok));
const port = server.address().port;

const opts = { args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] };
if (process.env.CHROMIUM_PATH) opts.executablePath = process.env.CHROMIUM_PATH;
const browser = await chromium.launch(opts);
try {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("[escena3d]", e.message));
  await page.addInitScript((s) => { window.SPEC = s; }, spec);
  await page.goto(`http://127.0.0.1:${port}/escena.html`);
  await page.waitForFunction(() => window.LISTO === true, null, { timeout: 60000 });
  const n = Math.max(1, Math.round(spec.dur * fps));
  for (let i = 0; i < n; i++) {
    await page.evaluate((t) => window.frame(t), i / fps);
    await page.screenshot({ path: path.join(outDir, `f${String(i).padStart(5, "0")}.jpg`), type: "jpeg", quality: 90 });
  }
  console.log(`[escena3d] ${n} fotogramas`);
} finally {
  await browser.close();
  server.close();
}
