// scripts/shots.ts - screenshots each screen's preview next to its design reference.
// usage: just shots [screen-id|all]   (needs `just run` first; SHOTS_BASE overrides the URL)
// Each shot uses a viewport as tall as the page, so fixed and sticky bars land where a user sees them.
import { chromium, type Page } from "playwright";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

type Screen = { id: string; name: string; reference: string; preview: string };

const sizes = [
  { name: "phone", width: 390, height: 844 },
  { name: "desktop", width: 1280, height: 800 },
];
const schemes = ["light", "dark"] as const;
const outDir = ".shots";

async function shoot(page: Page, url: string, width: number, height: number, path: string) {
  await page.setViewportSize({ width, height });
  await page.goto(url, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  const full = await page.evaluate(() => document.documentElement.scrollHeight);
  if (full > height) await page.setViewportSize({ width, height: full });
  await page.screenshot({ path });
}

async function main() {
  const screens: Screen[] = JSON.parse(readFileSync("docs/design/screens.json", "utf8"));
  const want = process.argv[2] ?? "all";
  const base = process.env.SHOTS_BASE ?? "http://localhost:3000";
  const chosen = screens.filter((s) => want === "all" || s.id === want);
  if (chosen.length === 0) throw new Error(`no screen "${want}" in docs/design/screens.json`);
  mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const rows: string[] = [];
  for (const s of chosen) {
    for (const size of sizes) {
      for (const scheme of schemes) {
        const tag = `${s.id}-${size.name}-${scheme}`;
        const page = await browser.newPage({ colorScheme: scheme, reducedMotion: "reduce" });
        await shoot(page, pathToFileURL(resolve(s.reference)).href, size.width, size.height, `${outDir}/${tag}-ref.png`);
        await shoot(page, base + s.preview, size.width, size.height, `${outDir}/${tag}-impl.png`);
        await page.close();
        rows.push(`<tr><th>${s.id} · ${s.name}<br><small>${size.name} · ${scheme}</small></th>` +
          `<td><img src="${tag}-ref.png"></td><td><img src="${tag}-impl.png"></td></tr>`);
      }
    }
  }
  await browser.close();
  writeFileSync(`${outDir}/compare.html`, `<!doctype html><meta charset="utf-8"><title>Screens vs references</title>
<style>body{font:14px system-ui;margin:16px}table{border-collapse:collapse}th,td{border:1px solid #bbb;padding:8px;vertical-align:top;text-align:left}img{max-width:420px}</style>
<table><tr><th></th><th>Reference</th><th>Implementation</th></tr>${rows.join("\n")}</table>`);
  console.log(`wrote ${outDir}/compare.html (${rows.length} rows)`);
}

main().catch((e) => { console.error(e); process.exit(1); });
