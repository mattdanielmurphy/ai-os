// Round 3: Hairline-based. The slide IS the page; subtle controls float on it at the bottom
// (full screen takes the whole page, controls included). Smaller graphics, no dot by the chapter label.
const f = (family, style) => ({ family, style });
const HK = { display: f('Hanken Grotesk', 'Medium'), body: f('Hanken Grotesk', 'Light'), label: f('Hanken Grotesk', 'Medium'), mono: f('Martian Mono', 'Light') };
const SL = { // Superlogical-ish tinted neutrals
  light: { bg: '#f5f5f4', ink: '#181d16', muted: '#737b6f', line: '#181d16', card: '#ebebe8', accent: '#181d16', g1: '#a58ac5', g2: '#cf6eb6', bars: ['#181d16', '#a58ac5', '#b9bdb5'] },
  dark: { bg: '#10120f', ink: '#ececea', muted: '#a3a8a0', line: '#ececea', card: '#1c1f1b', accent: '#ececea', g1: '#b9a3d6', g2: '#e08bcb', bars: ['#ececea', '#b9a3d6', '#4a4e47'] } };
const SPECS = [
  { name: '01 · Hairline, as is', column: true, monoLabel: true, gradient: true, bars: 'thin', total: 'rule', cap: false, ctl: 'row', fonts: HK, ...SL,
    pitch: 'Your favourite, fixed: the page is the slide, one centred column, mono only for the tiny label. Controls are one quiet line at the bottom: pause, progress, full screen.' },
  { name: '02 · Hairline, no mono', column: false, monoLabel: false, gradient: true, bars: 'thin', total: 'rule', cap: true, ctl: 'row', fonts: HK, ...SL,
    pitch: 'Same bones, left-aligned and wider, every word in Hanken Grotesk. A small subtitle sits under the content, not above it.' },
  { name: '03 · Hairline + soft card', column: true, monoLabel: false, gradient: false, bars: 'soft', total: 'card', cap: true, ctl: 'center', fonts: HK,
    pitch: 'The bit you liked from Caption first: soft rounded bars and a tinted total card, in dusk violet. Small subtitle under. Controls are a tiny centred cluster.',
    light: { bg: '#f5f5f6', ink: '#24232d', muted: '#6c6a79', line: '#24232d', card: '#e9e7f1', accent: '#625c89', bars: ['#625c89', '#92c1c6', '#cfcdd8'] },
    dark: { bg: '#121116', ink: '#e8e7ee', muted: '#a09eaf', line: '#e8e7ee', card: '#211f2a', accent: '#a39dd0', bars: ['#a39dd0', '#92c1c6', '#3f3d4a'] } },
  { name: '04 · Hairline + serif title', column: true, monoLabel: false, gradient: false, bars: 'thin', total: 'rule', cap: false, ctl: 'edge', titleFont: f('Instrument Serif', 'Regular'), titleScale: 1.25, fonts: HK,
    pitch: 'A touch of Gallery without the museum: only the headline and the big numbers are serif. Progress is a hairline along the very bottom edge; pause and full screen are small words in the corners.',
    light: { bg: '#f4f4f2', ink: '#1f2420', muted: '#6b726c', line: '#1f2420', card: '#e8e9e6', accent: '#376d61', bars: ['#376d61', '#60a192', '#bfc4bf'] },
    dark: { bg: '#111311', ink: '#e7eae6', muted: '#9ea59f', line: '#e7eae6', card: '#1d201d', accent: '#90c6b9', bars: ['#90c6b9', '#60a192', '#3f4540'] } },
  { name: '05 · Hairline + colour field', column: false, monoLabel: false, gradient: false, bars: 'soft', total: 'card', cap: true, ctl: 'segments', fonts: HK,
    pitch: 'Poster\'s colour, calmed down: the whole page is a pale cobalt wash, graphics kept small. Progress is eight thin segments along the bottom.',
    light: { bg: '#edf1f7', ink: '#14244a', muted: '#55658a', line: '#14244a', card: '#dde6f4', accent: '#1251b4', bars: ['#1251b4', '#83abeb', '#c4d0e4'] },
    dark: { bg: '#0b1530', ink: '#e1e9f8', muted: '#93a6cc', line: '#e1e9f8', card: '#13214a', accent: '#9dbdf1', bars: ['#9dbdf1', '#447ad5', '#2a3a63'] } },
  { name: '06 · Hairline, warm grey', column: true, monoLabel: true, gradient: true, bars: 'thin', total: 'rule', cap: true, ctl: 'row', fonts: HK,
    pitch: 'Hairline on warmer paper: brown-grey neutrals instead of green-black, a plum-to-lavender gradient on the key number, small subtitle.',
    light: { bg: '#f4f3f0', ink: '#2a2621', muted: '#776f66', line: '#2a2621', card: '#e9e6e1', accent: '#2a2621', g1: '#825172', g2: '#a58ac5', bars: ['#2a2621', '#825172', '#c4bfb7'] },
    dark: { bg: '#141210', ink: '#ece9e4', muted: '#a8a097', line: '#ece9e4', card: '#211e1a', accent: '#ece9e4', g1: '#c79abb', g2: '#b9a3d6', bars: ['#ece9e4', '#c79abb', '#4a453e'] } },
  { name: '07 · Hairline, dot bars', column: false, monoLabel: true, gradient: false, bars: 'dots', total: 'rule', cap: false, ctl: 'segments', fonts: HK,
    pitch: 'The lightest graphics: each cost is a hairline ending in a dot, like a chart drawn with a fine pen. Fireweed pink is the only colour.',
    light: { bg: '#f5f5f4', ink: '#1d1c1f', muted: '#75727a', line: '#1d1c1f', card: '#eaeaea', accent: '#b4479a', bars: ['#1d1c1f', '#b4479a', '#9b98a0'] },
    dark: { bg: '#121113', ink: '#ecebee', muted: '#a5a2aa', line: '#ecebee', card: '#1f1e21', accent: '#e08bcb', bars: ['#ecebee', '#e08bcb', '#6d6a72'] } },
  { name: '08 · Hairline, aspen', column: true, monoLabel: false, gradient: false, bars: 'thin', total: 'card', cap: true, ctl: 'edge', fonts: HK,
    pitch: 'Hairline with a calm green accent and a soft total card; corner controls and a bottom-edge progress line keep the middle completely clear.',
    light: { bg: '#f4f5f3', ink: '#1e2a1c', muted: '#68735f', line: '#1e2a1c', card: '#e6ebe2', accent: '#3f7a34', bars: ['#3f7a34', '#73a164', '#c3c9bd'] },
    dark: { bg: '#111410', ink: '#e5eae2', muted: '#9ca694', line: '#e5eae2', card: '#1c2119', accent: '#8fc37f', bars: ['#8fc37f', '#73a164', '#3e4639'] } },
];
let C, F;
const hex = h => { h = h.replace('#', ''); return { r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255 }; };
const solid = (h, o = 1) => [{ type: 'SOLID', color: hex(h), opacity: o }];
const grad = (a, b) => ({ type: 'GRADIENT_LINEAR', gradientTransform: [[1, 0, 0], [0, 1, 0]], gradientStops: [{ position: 0, color: { ...hex(a), a: 1 } }, { position: 1, color: { ...hex(b), a: 1 } }] });
function T(p, str, o) {
  const t = figma.createText(); t.fontName = o.font; t.fontSize = o.size; t.characters = str;
  t.fills = solid(o.color, o.opacity ?? 1);
  if (o.ls) t.letterSpacing = { unit: 'PERCENT', value: o.ls };
  if (o.lh) t.lineHeight = { unit: 'PERCENT', value: o.lh };
  if (o.align) t.textAlignHorizontal = o.align;
  p.appendChild(t);
  if (o.w) { t.textAutoResize = 'HEIGHT'; t.resize(o.w, t.height); }
  t.x = o.x || 0; t.y = o.y || 0; return t;
}
function R(p, o) {
  const n = figma.createRectangle(); n.resize(o.w, o.h);
  n.fills = o.fill ? solid(o.fill, o.o ?? 1) : [];
  if (o.stroke) { n.strokes = solid(o.stroke, o.so ?? 1); n.strokeWeight = o.sw || 1; n.strokeAlign = 'INSIDE'; }
  n.cornerRadius = o.r || 0; p.appendChild(n); n.x = o.x; n.y = o.y; return n;
}
function E(p, x, y, d, fill, o = 1) { const n = figma.createEllipse(); n.resize(d, d); n.fills = fill ? solid(fill, o) : []; p.appendChild(n); n.x = x; n.y = y; return n; }
function svg(p, s, x, y) { const n = figma.createNodeFromSvg(s); p.appendChild(n); n.x = x; n.y = y; return n; }
const CAP = 'Before, TV cost about two thousand dollars a year. Telus was nine hundred,';
const CAPFULL = CAP + ' Sportsnet plus alone is three fifty.';
// content block, built at y=0 inside a transparent frame, then centred on the page
function content(m, W, phone) {
  const box = figma.createFrame(); box.fills = []; box.clipsContent = false; box.name = 'Slide content';
  const cw = phone ? W - 48 : C.column ? 720 : 960;
  let y = 0;
  if (C.monoLabel) T(box, 'WHAT TV COSTS A YEAR NOW', { y, font: F.mono, size: phone ? 9.5 : 11, color: m.muted, ls: 8 });
  else T(box, 'What TV costs a year now', { y, font: F.label, size: phone ? 13 : 15, color: m.muted });
  y += phone ? 26 : 34;
  const tf = C.titleFont || F.display, ts = (phone ? 34 : 52) * (C.titleScale || 1);
  const t = T(box, 'Before: about $2,000', { y, font: tf, size: ts, color: m.ink, lh: 100, ls: C.titleFont ? 0 : -2, w: cw });
  const i = t.characters.indexOf('$2,000');
  t.setRangeFills(i, i + 6, C.gradient ? [grad(m.g1, m.g2)] : solid(m.accent));
  y += t.height + (phone ? 30 : 44);
  const rows = [['Telus TV (cancelled)', '$900', 1, '$75 a month'], ['Sportsnet+ alone', '$350', .39, 'per year'], ['Everything else: Apple One, Netflix, Prime…', '~$750', .83, 'estimate']];
  const maxW = phone ? 190 : C.column ? 440 : 520;
  const numFont = C.titleFont || F.display, ns = phone ? 19 : 24;
  rows.forEach((r, j) => {
    T(box, r[0], { y, font: F.label, size: phone ? 12 : 13, color: m.ink, opacity: .85 });
    y += phone ? 20 : 24;
    const bw = maxW * r[2];
    let bh;
    if (C.bars === 'thin') { bh = 6; R(box, { x: 0, y: y + 10, w: maxW, h: 1, fill: m.line, o: .12 }); R(box, { x: 0, y: y + 8, w: bw, h: 5, fill: m.bars[j], r: 3 }); bh = 20; }
    else if (C.bars === 'dots') { bh = 20; R(box, { x: 0, y: y + 10, w: bw, h: 1, fill: m.bars[j] }); E(box, bw - 5, y + 5.5, 10, m.bars[j]); }
    else { bh = phone ? 18 : 22; R(box, { x: 0, y, w: bw, h: bh, fill: m.bars[j], r: 6 }); }
    const a = T(box, r[1], { x: bw + (phone ? 10 : 14), y: y + bh / 2 - ns * .62, font: numFont, size: ns * (C.titleFont ? 1.15 : 1), color: m.ink });
    T(box, r[3], { x: a.x + a.width + 8, y: a.y + a.height * .42, font: F.body, size: phone ? 11 : 13, color: m.muted });
    y += bh + (phone ? 20 : 24);
  });
  y += phone ? 4 : 10;
  const tw = phone ? cw : C.column ? cw : 720;
  if (C.total === 'card') {
    const h = phone ? 64 : 70;
    R(box, { x: 0, y, w: tw, h, fill: m.card, r: 14 });
    T(box, 'With Telus gone: about $1,100 a year.', { x: phone ? 16 : 24, y: y + (phone ? 12 : 22), w: tw - (phone ? 32 : 48), font: F.display, size: phone ? 17 : 22, color: m.ink, lh: 120 });
    y += h;
  } else {
    R(box, { x: 0, y, w: tw, h: 1, fill: m.line, o: .16 });
    const tt = T(box, 'With Telus gone: about $1,100 a year.', { y: y + 16, w: tw, font: F.display, size: phone ? 18 : 24, color: m.ink, lh: 120 });
    y += 16 + tt.height;
  }
  if (C.cap) {
    y += phone ? 26 : 36;
    const c = T(box, CAPFULL, { y, w: phone ? cw : Math.min(tw, 640), font: F.body, size: phone ? 13 : 15, color: m.muted, lh: 140 });
    c.setRangeFills(0, CAP.length, solid(m.ink));
    y += c.height;
  }
  box.resizeWithoutConstraints(cw, y);
  return box;
}
function pauseIcon(p, m, x, y, d, ring) {
  if (ring) { const r = E(p, x, y, d, null); r.strokes = solid(m.ink, .25); r.strokeWeight = 1; }
  const s = Math.max(2, d * .1), h = d * .34;
  R(p, { x: x + d / 2 - s * 1.6, y: y + (d - h) / 2, w: s, h, fill: m.ink, r: 1 });
  R(p, { x: x + d / 2 + s * .6, y: y + (d - h) / 2, w: s, h, fill: m.ink, r: 1 });
}
function fsIcon(p, m, x, y, d, ring) {
  if (ring) { const r = E(p, x, y, d, null); r.strokes = solid(m.ink, .25); r.strokeWeight = 1; }
  const s = Math.round(d * .42), o = (d - s) / 2;
  const n = svg(p, `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" stroke="${m.ink}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`, x + o, y + o);
  return n;
}
function controls(p, m, W, H, phone) {
  const M = phone ? 20 : 40, frac = .19;
  const g = figma.createFrame(); g.name = 'Controls (float on the slide)'; g.fills = []; g.clipsContent = false; g.resize(W, H); p.appendChild(g); g.x = 0; g.y = 0;
  g.opacity = .78;
  if (C.ctl === 'row') {
    const y = H - (phone ? 66 : 64), d = phone ? 36 : 32;
    const x0 = phone ? M : C.column ? (W - 720) / 2 : 160, x1 = phone ? W - M : C.column ? (W + 720) / 2 : W - 160;
    pauseIcon(g, m, x0, y, d, true);
    R(g, { x: x0 + d + 16, y: y + d / 2, w: x1 - x0 - 2 * d - 32, h: 1, fill: m.ink, o: .15 });
    R(g, { x: x0 + d + 16, y: y + d / 2 - .5, w: (x1 - x0 - 2 * d - 32) * frac, h: 2, fill: m.ink, r: 1 });
    fsIcon(g, m, x1 - d, y, d, true);
  } else if (C.ctl === 'center') {
    const d = phone ? 40 : 36, y = H - (phone ? 70 : 66), cx = W / 2;
    pauseIcon(g, m, cx - d - 30, y, d, true);
    T(g, '2 / 8', { x: cx - 14, y: y + d / 2 - 9, font: F.label, size: 13, color: m.muted });
    fsIcon(g, m, cx + 30, y, d, true);
  } else if (C.ctl === 'edge') {
    R(g, { x: 0, y: H - 3, w: W, h: 3, fill: m.ink, o: .1 }); R(g, { x: 0, y: H - 3, w: W * frac, h: 3, fill: m.accent });
    const y = H - (phone ? 44 : 46);
    pauseIcon(g, m, M - 6, y - 4, 24, false);
    T(g, 'Pause', { x: M + 22, y, font: F.label, size: 13, color: m.ink });
    const t = T(g, 'Full screen', { x: 0, y, font: F.label, size: 13, color: m.ink }); t.x = W - M - t.width;
    fsIcon(g, m, t.x - 28, y - 4, 24, false);
  } else if (C.ctl === 'segments') {
    const y = H - (phone ? 60 : 56), d = 28, x0 = phone ? M : 160, x1 = phone ? W - M : W - 160;
    pauseIcon(g, m, x0, y, d, false);
    const sx = x0 + d + 12, sw = (x1 - d - 12 - sx - 7 * 4) / 8;
    for (let k = 0; k < 8; k++) { R(g, { x: sx + k * (sw + 4), y: y + d / 2 - 1, w: sw, h: 2, fill: m.ink, o: .15, r: 1 }); if (k <= 1) R(g, { x: sx + k * (sw + 4), y: y + d / 2 - 1, w: k ? sw * .45 : sw, h: 2, fill: m.accent, r: 1 }); }
    fsIcon(g, m, x1 - d, y, d, false);
  }
  return g;
}
function page(m, phone) {
  const W = phone ? 390 : 1440, H = phone ? 844 : 900;
  const fr = figma.createFrame(); fr.name = phone ? 'Phone · dark · 390' : 'Desktop · light · 1440';
  fr.resize(W, H); fr.fills = solid(m.bg); fr.clipsContent = true; if (phone) fr.cornerRadius = 44;
  if (phone) T(fr, '9:41', { x: 32, y: 16, font: F.label, size: 15, color: m.ink });
  const c = content(m, W, phone); fr.appendChild(c);
  const top = phone ? 70 : 60, bottom = H - (phone ? 96 : 100);
  c.x = phone ? 24 : C.column ? (W - 720) / 2 : 160;
  c.y = Math.round(top + Math.max(0, (bottom - top - c.height) / 2));
  controls(fr, m, W, H, phone);
  return fr;
}
const fams = new Map([['Instrument Serif|Regular', f('Instrument Serif', 'Regular')]]);
for (const s of SPECS) for (const k in s.fonts) fams.set(s.fonts[k].family + '|' + s.fonts[k].style, s.fonts[k]);
await Promise.all([...fams.values()].map(x => figma.loadFontAsync(x)));
const oldPg = figma.root.children.find(p => p.name.startsWith('Round 3')); if (oldPg) { await figma.setCurrentPageAsync(figma.root.children[0]); oldPg.remove(); }
const pg = figma.createPage(); pg.name = 'Round 3 · Hairline-based';
await figma.setCurrentPageAsync(pg);
const out = [];
for (let IDX = 0; IDX < SPECS.length; IDX++) {
  C = SPECS[IDX]; F = C.fonts;
  const board = figma.createFrame(); board.name = C.name; board.resize(2000, 1150); board.fills = solid('#e9e9e7');
  board.x = (IDX % 2) * 2100; board.y = Math.floor(IDX / 2) * 1250;
  T(board, C.name, { x: 40, y: 30, font: F.display, size: 44, color: '#1c1d1c', ls: -2 });
  T(board, C.pitch, { x: 40, y: 92, w: 1400, font: F.body, size: 18, color: '#3d3f3d', lh: 135 });
  const d = page(C.light, false); board.appendChild(d); d.x = 40; d.y = 210;
  const ph = page(C.dark, true); board.appendChild(ph); ph.x = 1540; ph.y = 210;
  out.push({ name: C.name, id: board.id });
}
return { page: pg.id, out };
