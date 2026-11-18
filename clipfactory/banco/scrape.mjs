// TOMMY · Recoge las URLs de imágenes OFICIALES de las páginas de Rockstar (renderiza la web como un navegador real).
// node scrape.mjs <salida.json> <url1> <url2> ...   → [{url, alt, pagina}]
import fs from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const [out, ...pages] = process.argv.slice(2);
const IMG = /\.(jpe?g|png|webp)(\?|$)/i;
const found = new Map();
const add = (url, alt, pagina) => {
  try { url = new URL(url, pagina).href; } catch { return; }
  if (!/rockstargames|akamaized/i.test(url) || !IMG.test(url)) return;
  if (/icon|logo-|favicon|sprite|avatar|badge|rating|esrb|pegi|flag/i.test(url) && !/vi|gta/i.test(alt)) return;
  if (!found.has(url)) found.set(url, { url, alt: alt || "", pagina });
};

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 }, locale: "es-ES",
  userAgent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" });
for (const pagina of pages) {
  const page = await ctx.newPage();
  page.on("response", (r) => { const ct = r.headers()["content-type"] || ""; if (ct.startsWith("image/")) add(r.url(), "", pagina); });
  try {
    await page.goto(pagina, { waitUntil: "networkidle", timeout: 60000 });
    for (const sel of ["button:has-text('Accept')", "button:has-text('Aceptar')", "#onetrust-accept-btn-handler"]) {
      await page.locator(sel).first().click({ timeout: 1500 }).catch(() => {});
    }
    for (let i = 0; i < 25; i++) { await page.mouse.wheel(0, 1600); await page.waitForTimeout(400); }
    const items = await page.evaluate(() => {
      const r = [];
      for (const im of document.querySelectorAll("img, source")) {
        const alt = im.getAttribute("alt") || im.closest("figure,a,div")?.getAttribute("aria-label") || "";
        if (im.src) r.push([im.src, alt]);
        for (const part of (im.getAttribute("srcset") || "").split(",")) { const u = part.trim().split(" ")[0]; if (u) r.push([u, alt]); }
      }
      for (const a of document.querySelectorAll("a[href]")) r.push([a.href, a.textContent.trim().slice(0, 80)]);
      for (const el of document.querySelectorAll("[style*='background']")) {
        const m = /url\(["']?([^"')]+)/.exec(el.getAttribute("style")); if (m) r.push([m[1], el.getAttribute("aria-label") || ""]);
      }
      const html = document.documentElement.innerHTML;
      for (const m of html.matchAll(/https?:\/\/[^"'\s\\)]+?\.(?:jpe?g|png|webp)/gi)) r.push([m[0], ""]);
      return r;
    });
    for (const [u, alt] of items) add(u, alt, pagina);
    console.log(`[banco] ${pagina} → ${found.size} imágenes acumuladas`);
  } catch (e) {
    console.log(`[banco] ${pagina} falló: ${e.message.split("\n")[0]}`);
  }
  await page.close();
}
await browser.close();
fs.writeFileSync(out, JSON.stringify([...found.values()], null, 1));
