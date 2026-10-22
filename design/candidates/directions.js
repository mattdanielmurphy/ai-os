// Board v2: three seeded palette directions. Key colour = step 9 (the identity); Leonardo fills the other
// steps by contrast for light and dark. Each key is nudged until it is clearly unlike any stock colour.
import { Theme, Color, BackgroundColor } from '@adobe/leonardo-contrast-colors';
import { formatHex, differenceCiede2000, clampChroma } from 'culori';
import * as radix from '@radix-ui/colors';
import { writeFileSync } from 'fs';

const console_warn = console.warn; console.warn = () => {}; // Leonardo + Tailwind deprecation noise
const tw = (await import('tailwindcss/colors.js')).default;


const RATIOS = [1.04, 1.1, 1.22, 1.38, 1.55, 1.8, 2.2, 2.9, 3.6, 4.2, 5.6, 12];
const MIN_DE = 6;           // CIEDE2000 distance from every stock colour (2-3 is "just noticeable")
const BANNED = ['#c96442', '#c2502f']; const BANNED_DE = 12;

// Stock colours: every Tailwind v3 shade and every Radix step (light and dark).
const stock = [];
const DEPRECATED = new Set(['lightBlue', 'warmGray', 'trueGray', 'coolGray', 'blueGray']);
for (const [n, sc] of Object.entries(tw)) if (typeof sc === 'object' && !DEPRECATED.has(n))
  for (const [k, v] of Object.entries(sc)) stock.push([`Tailwind ${n}-${k}`, v]);
for (const [n, sc] of Object.entries(radix)) if (!/A$|P3/.test(n))
  for (const [k, v] of Object.entries(sc)) if (typeof v === "string" && v.startsWith('#')) stock.push([`Radix ${k}`, v]);
console.warn = (...a) => { if (!String(a[0]).startsWith('Leonardo')) console_warn(...a); };
const dE = differenceCiede2000();
const nearest = (hex) => stock.reduce((b, s) => { const d = dE(hex, s[1]); return d < b[1] ? [s[0], d, s[1]] : b; }, ['', 1e9]);

const hex = (l, c, h) => formatHex(clampChroma({ mode: 'oklch', l, c, h }, 'oklch'));
// Nudge hue/lightness a little until the key clears MIN_DE; keep the smallest change that works.
function settle(l, c, h) {
  let best = null;
  for (let r = 0; r <= 8; r++) for (const dh of [0, r, -r]) for (const dl of [0, 0.0075 * r, -0.0075 * r]) for (const dc of [0, 0.02, -0.02]) {
    const x = hex(l + dl, c + dc, h + dh), n = nearest(x);
    if (BANNED.some(b => dE(x, b) < BANNED_DE)) continue;
    if (n[1] >= MIN_DE) return { hex: x, near: n, moved: r || (dc ? 1 : 0) };
    if (!best || n[1] > best.near[1]) best = { hex: x, near: n, moved: -1 };
  }
  return best;
}

// [name, l, c, h, note]
const DIRECTIONS = {
  apothecary: { title: 'Apothecary glass', blurb: 'Old pharmacy bottles, tinctures and paper labels.', neutral: [0.55, 0.018, 85],
    hues: [['cobalt bottle', 0.46, 0.15, 266], ['tincture', 0.72, 0.17, 58], ['absinthe', 0.8, 0.16, 122], ['verdigris', 0.66, 0.09, 178],
      ['oxblood', 0.42, 0.13, 12], ['lavender oil', 0.68, 0.09, 305], ['uranium glass', 0.88, 0.18, 112], ['iodine', 0.5, 0.1, 340]] },
  prairie: { title: 'Prairie light', blurb: 'Edmonton sky, canola fields, winter dusk and aurora.', neutral: [0.55, 0.012, 240],
    hues: [['canola', 0.86, 0.17, 98], ['big sky', 0.7, 0.11, 238], ['winter dusk', 0.5, 0.09, 290], ['aspen', 0.66, 0.12, 138],
      ['sunset', 0.72, 0.17, 52], ['frost', 0.84, 0.07, 212], ['aurora', 0.76, 0.16, 160], ['fireweed', 0.62, 0.17, 345]] },
  synth: { title: 'Synth panel', blurb: 'Vintage synth knobs, patch cables and glowing displays.', neutral: [0.55, 0.008, 260],
    hues: [['signal red', 0.6, 0.21, 24], ['panel orange', 0.7, 0.19, 50], ['patch yellow', 0.85, 0.17, 95], ['phosphor', 0.8, 0.2, 148],
      ['VFD teal', 0.8, 0.13, 192], ['knob blue', 0.56, 0.14, 252], ['patch violet', 0.56, 0.15, 312], ['tape cream', 0.9, 0.04, 90]] },
};

function scalesFor(keyHex, neutralHex) {
  const bg = new BackgroundColor({ name: 'bg', colorKeys: [neutralHex], ratios: RATIOS });
  const col = new Color({ name: 'k', colorKeys: [keyHex], ratios: RATIOS, colorSpace: 'OKLCH', smooth: true });
  const mk = (lightness) => { const t = new Theme({ colors: [col], backgroundColor: bg, lightness }); return { bg: t.contrastColors[0].background, s: t.contrastColors[1].values.map(v => v.value) }; };
  const L = mk(98), D = mk(9);
  L.s[8] = keyHex; D.s[8] = keyHex; // identity colour stays exact in both modes
  return { light: L, dark: D };
}

const out = {};
for (const [id, dir] of Object.entries(DIRECTIONS)) {
  const nHex = hex(...dir.neutral);
  const neutral = scalesFor(nHex, nHex);
  out[id] = { title: dir.title, blurb: dir.blurb, neutral: { light: neutral.light.s, dark: neutral.dark.s, bgLight: neutral.light.bg, bgDark: neutral.dark.bg }, hues: [] };
  for (const [name, l, c, h] of dir.hues) {
    const k = settle(l, c, h), sc = scalesFor(k.hex, nHex);
    out[id].hues.push({ name, key: k.hex, nearest: k.near[0], nearestHex: k.near[2], distance: +k.near[1].toFixed(1), nudged: k.moved > 0, light: sc.light.s, dark: sc.dark.s });
    console.log(id.padEnd(11), name.padEnd(14), k.hex, 'nearest', k.near[0], k.near[1].toFixed(1), k.moved > 0 ? 'nudged' : '');
  }
}
writeFileSync(new URL('./directions.json', import.meta.url), JSON.stringify({ minDE: MIN_DE, stockCount: stock.length, directions: out }, null, 1));
console.log('stock colours checked:', stock.length);
