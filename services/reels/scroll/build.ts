// Build a scroll-to-read reel into a claude.ai Artifact page (fragment HTML + audio files).
//   bun services/reels/scroll/build.ts reels/<id> [--no-voice]
// Reads <reel>/reel.json + <reel>/body.html, inlines the kit (kit/*.css, kit/*.js), records every [data-read]
// block once with Speechify (cached in scroll/cache/, keyed by voice + text) and writes out/<id>/index.html + audio/.
// Speechify code and the voice live in ~/projects/pages/tts.ts (same voice as the pages "scroll-read" mockup).
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";

const HERE = import.meta.dir;
const PAGES = process.env.PAGES_DIR || join(process.env.HOME!, "projects", "pages");
const { blocksOf, cacheKey, speechify } = await import(join(PAGES, "tts.ts"));

const args = process.argv.slice(2);
const dir = resolve(HERE, args.find(a => !a.startsWith("--")) || "");
const noVoice = args.includes("--no-voice");
const reel = JSON.parse(readFileSync(join(dir, "reel.json"), "utf8"));
const body = readFileSync(join(dir, "body.html"), "utf8");
const kit = (f: string) => readFileSync(join(HERE, "kit", f), "utf8");
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

const page = (config: object) => `<title>${esc(reel.title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@300;400;500;600&family=Martian+Mono:wght@400;500&family=Noto+Sans+Math&display=swap" rel="stylesheet">
<style>
${kit("player.css")}
${kit("reactions.css")}
${kit("ask.css")}
</style>
<div id="blob"></div>
<div id="stretch"></div>
<div id="dest"></div>
<div id="centre"></div>
<div id="pill">pull 0%</div>

<main id="text">
${body}
  <div class="end" id="end" hidden><div id="review"></div>— end —<br><button id="again">↺ Read again</button>${reel.next ? `<br><br>Next: ${reel.nextUrl ? `<a href="${esc(reel.nextUrl)}" target="_blank" rel="noopener">${esc(reel.next)}</a>` : esc(reel.next)}` : ""}</div>
</main>

<div class="ctl l">
  <button id="play" aria-label="Pause">❚❚</button>
  <label class="toggle" title="Narration recorded with a Speechify voice."><input type="checkbox" id="voice"> <span class="lbl">Read aloud</span><span id="wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span></label>
</div>
<div class="ctl r"><button id="tuneBtn" aria-expanded="false">Tune</button></div>
<div id="tune" hidden>
  <label>Reading speed <b id="wpmV"></b><input type="range" id="wpm" min="120" max="420" step="10"></label>
  <label>Skip threshold (screen %) <b id="thrV"></b><input type="range" id="thr" min="10" max="70" step="2"></label>
  <label>Pull strength <b id="pullV"></b><input type="range" id="pull" min="0" max="1" step=".05"></label>
  <label>In-transit fade (px) <b id="fadeV"></b><input type="range" id="fade" min="4" max="80" step="2"></label>
  <label>Fly speed <b id="flyV"></b><input type="range" id="fly" min=".05" max=".6" step=".01"></label>
</div>
<div id="bar"></div>
<div id="score" hidden></div>

<script>window.REEL = ${JSON.stringify(config)};</script>
<script>
${kit("player.js")}
</script>
<script>
${kit("reactions.js")}
</script>
<script>
${kit("ask.js")}
</script>
`;

const out = join(HERE, "out", reel.id), cache = join(HERE, "cache");
rmSync(join(out, "audio"), { recursive: true, force: true });   // out/ is build output: only this build's clips ship
mkdirSync(join(out, "audio"), { recursive: true }); mkdirSync(cache, { recursive: true });

// Block texts exactly as the page splits them (the pages helper reads a full HTML file).
const probe = join(out, "probe.html");
writeFileSync(probe, `<!doctype html><html><body><main id="text">${body}</main></body></html>`);
const blocks: string[] = blocksOf(probe);

function speechifyKey() {
  if (process.env.SPEECHIFY_API_KEY) return process.env.SPEECHIFY_API_KEY;
  const env = join(process.env.HOME!, "projects", "ai-os", ".env");     // loaded into memory only, never printed
  if (!existsSync(env)) return undefined;
  const line = readFileSync(env, "utf8").split("\n").find(l => l.startsWith("SPEECHIFY_API_KEY="));
  return line?.split("=").slice(1).join("=").trim().replace(/^["']|["']$/g, "");
}

const audio: Record<number, { src: string; marks: unknown }> = {};
if (!noVoice) {
  const key = speechifyKey();
  if (!key) throw new Error("SPEECHIFY_API_KEY missing (ai-os .env)");
  let made = 0;
  const todo = blocks.map((text, b) => ({ text, b }));
  // Two at a time, backing off when Speechify says 429 (too many requests).
  const say = async (text: string) => {
    for (let n = 0; ; n++) {
      try { return await speechify(text, key); }
      catch (e: any) { if (!/429/.test(String(e?.message)) || n >= 6) throw e; await Bun.sleep(2000 * 2 ** n); }
    }
  };
  for (let i = 0; i < todo.length; i += 2) {
    await Promise.all(todo.slice(i, i + 2).map(async ({ text, b }) => {
      const k = cacheKey(text), mp3 = join(cache, k + ".mp3"), js = join(cache, k + ".json");
      if (!existsSync(mp3) || !existsSync(js)) {
        const r = await say(text);
        writeFileSync(mp3, r.mp3); writeFileSync(js, JSON.stringify(r.marks)); made++;
      }
      copyFileSync(mp3, join(out, "audio", k + ".mp3"));
      audio[b] = { src: `audio/${k}.mp3`, marks: JSON.parse(readFileSync(js, "utf8")) };
    }));
  }
  console.log(`voice: ${blocks.length} blocks, ${made} newly recorded`);
}

const config = { id: reel.id, title: reel.title, ask: reel.ask, audio };
writeFileSync(join(out, "index.html"), page(config));
// A standalone copy for local headless tests (full document, same content).
writeFileSync(join(out, "test.html"), `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>${page(config)}</body></html>`);
writeFileSync(join(out, "files.json"), JSON.stringify(readdirSync(join(out, "audio")).map(f => ({ path: "audio/" + f }))));
console.log(`built ${basename(out)}: ${blocks.length} blocks → ${join(out, "index.html")}`);
