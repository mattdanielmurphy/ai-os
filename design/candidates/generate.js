// Candidate master palette: OKLCH key colours -> Leonardo contrast-targeted 12-step scales, light + dark.
import { Theme, Color, BackgroundColor } from '@adobe/leonardo-contrast-colors';
import { formatHex, oklch } from 'culori';
import { writeFileSync } from 'fs';

// Step contrast targets against the app background (Radix-style jobs).
// 1-2 bg, 3-5 component bg, 6-8 borders, 9 solid, 10 solid hover, 11 low-contrast text, 12 high-contrast text.
const RATIOS = [1.04, 1.1, 1.22, 1.38, 1.55, 1.8, 2.2, 2.9, 3.6, 4.2, 5.6, 12];

// [name, hue°, chroma] in OKLCH. No hues 30-60 (terracotta/rust/coral/burnt orange band).
export const HUES = [
  ['crimson', 15, 0.19], ['rose', 5, 0.16], ['berry', 350, 0.17], ['plum', 325, 0.14],
  ['violet', 300, 0.15], ['iris', 285, 0.14], ['cobalt', 262, 0.16], ['blue', 250, 0.15],
  ['sky', 235, 0.12], ['cyan', 215, 0.11], ['teal', 190, 0.11], ['jade', 170, 0.12],
  ['green', 150, 0.15], ['fern', 135, 0.14], ['lime', 125, 0.17], ['olive', 115, 0.08],
  ['moss', 130, 0.06], ['citron', 105, 0.16], ['yellow', 95, 0.17], ['gold', 85, 0.14],
  ['honey', 75, 0.12], ['sage', 150, 0.04], ['slate', 250, 0.02], ['stone', 70, 0.012],
];

const key = (h, c, l = 0.62) => formatHex({ mode: 'oklch', l, c, h });
const bg = new BackgroundColor({ name: 'bg', colorKeys: [key(70, 0.012, 0.5)], ratios: RATIOS });
const colors = HUES.map(([name, h, c]) => new Color({
  name, colorKeys: [key(h, c * 0.6, 0.85), key(h, c), key(h, c * 0.7, 0.35)], ratios: RATIOS, colorSpace: 'OKLCH', smooth: true,
}));

const build = (lightness) => {
  const t = new Theme({ colors, backgroundColor: bg, lightness, contrast: 1 });
  const out = {};
  for (const c of t.contrastColors.slice(1)) out[c.name] = c.values.map(v => v.value);
  return { background: t.contrastColors[0].background, scales: out };
};
const data = { ratios: RATIOS, hues: HUES, light: build(98), dark: build(9) };
writeFileSync(new URL('./candidates.json', import.meta.url), JSON.stringify(data, null, 1));
console.log('light bg', data.light.background, 'dark bg', data.dark.background, Object.keys(data.light.scales).length, 'hues');
console.log('crimson light', data.light.scales.crimson.join(' '));
console.log('crimson dark', data.dark.scales.crimson.join(' '));
