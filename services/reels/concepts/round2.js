// Round 2 reel concepts: the whole page is the slide, a few floating controls, no monospace, warm.
// Paste into the Figma MCP use_figma tool. Builds 8 boards (desktop light 1440×900 + phone dark 390×844).
const f = (family, style) => ({ family, style });
const SPECS = [
  { name: '01 · Pill', ctl: 'pill', cap: 'bottom', radius: 12,
    pitch: 'One soft pill floats at the bottom: play, eight dots for the beats, full screen. A single subtitle line sits above it. Everything else is the slide.',
    fonts: { display: f('Hanken Grotesk', 'SemiBold'), body: f('Hanken Grotesk', 'Regular'), label: f('Hanken Grotesk', 'Medium') },
    fontLine: 'Hanken Grotesk', paletteLine: 'Apothecary warm greys + verdigris',
    light: { bg: '#f3f3f1', ink: '#35322b', muted: '#686359', line: '#d6d4d0', accent: '#376d61', accentInk: '#ebf5f2', glass: '#ffffff', bars: ['#35322b', '#60a192', '#bebbb4'] },
    dark: { bg: '#1a1916', ink: '#e6e4df', muted: '#a29e95', line: '#3d3a32', accent: '#90c6b9', accentInk: '#0b211c', glass: '#2d2a24', bars: ['#e6e4df', '#60a192', '#555047'] } },
  { name: '02 · Corners', ctl: 'corners', cap: 'none', radius: 999,
    pitch: 'Nothing in the middle at all. A thin progress line across the very top, a round play button bottom-left, full screen bottom-right. No subtitles: the voice carries it.',
    fonts: { display: f('Instrument Serif', 'Regular'), body: f('Instrument Sans', 'Regular'), label: f('Instrument Sans', 'Medium') },
    fontLine: 'Instrument Serif + Instrument Sans', paletteLine: 'Apothecary: iodine plum on warm grey',
    light: { bg: '#f1f0ee', ink: '#2b2925', muted: '#6d6a63', line: '#d6d4d0', accent: '#825172', accentInk: '#f7eef4', glass: '#ffffff', bars: ['#825172', '#a58ac5', '#cbc9c3'] },
    dark: { bg: '#191815', ink: '#ebe9e4', muted: '#9a9890', line: '#36332d', accent: '#c79abb', accentInk: '#2a1424', glass: '#2a2824', bars: ['#c79abb', '#a58ac5', '#48443c'] } },
  { name: '03 · Film subtitles', ctl: 'subtitle', cap: 'film', radius: 999,
    pitch: 'Reads like a film: subtitles centred near the bottom, two small round buttons tucked to the right, progress as a hairline under them. Good for sound-off viewing.',
    fonts: { display: f('Newsreader', 'Medium'), body: f('Libre Franklin', 'Regular'), label: f('Libre Franklin', 'Medium') },
    fontLine: 'Newsreader + Libre Franklin', paletteLine: 'Prairie: big sky blue, aspen',
    light: { bg: '#f4f5f4', ink: '#2e3336', muted: '#5d6468', line: '#d2d6d9', accent: '#2f6f9e', accentInk: '#eef5fb', glass: '#ffffff', bars: ['#2e3336', '#619cc8', '#73a164'] },
    dark: { bg: '#17191a', ink: '#e2e4e6', muted: '#959ca1', line: '#33373a', accent: '#8dbbe0', accentInk: '#0d2233', glass: '#26292b', bars: ['#e2e4e6', '#619cc8', '#73a164'] } },
  { name: '04 · Side rail', ctl: 'rail', cap: 'left', radius: 14,
    pitch: 'Beats are a column of dots on the right edge you can tap, like chapters. Play sits bottom-left with the subtitle beside it; full screen top-right.',
    fonts: { display: f('Familjen Grotesk', 'SemiBold'), body: f('Familjen Grotesk', 'Regular'), label: f('Familjen Grotesk', 'Medium') },
    fontLine: 'Familjen Grotesk', paletteLine: 'Prairie: winter dusk violet, frost',
    light: { bg: '#f3f3f5', ink: '#2c2b36', muted: '#615f70', line: '#d5d4dc', accent: '#625c89', accentInk: '#f4f3fa', glass: '#ffffff', bars: ['#625c89', '#92c1c6', '#c9c7d3'] },
    dark: { bg: '#18171d', ink: '#e4e3ea', muted: '#9a98a8', line: '#34323d', accent: '#a39dd0', accentInk: '#17151f', glass: '#272530', bars: ['#a39dd0', '#92c1c6', '#46434f'] } },
  { name: '05 · Stories', ctl: 'stories', cap: 'bottom', radius: 999,
    pitch: 'Like phone stories: segmented bars across the top, tap left or right side to go back or forward. Play and full screen sit small in the top-right. Feels native on a phone.',
    fonts: { display: f('Onest', 'SemiBold'), body: f('Onest', 'Regular'), label: f('Onest', 'Medium') },
    fontLine: 'Onest', paletteLine: 'Prairie: aspen green, canola',
    light: { bg: '#f4f5f2', ink: '#262b24', muted: '#5f665b', line: '#d3d8cf', accent: '#3f7a34', accentInk: '#eef7ec', glass: '#ffffff', bars: ['#3f7a34', '#73a164', '#c6c9a0'] },
    dark: { bg: '#161915', ink: '#e3e7e0', muted: '#97a092', line: '#30362d', accent: '#8fc37f', accentInk: '#10230b', glass: '#252a23', bars: ['#8fc37f', '#73a164', '#dac814'] } },
  { name: '06 · Inset card', ctl: 'dock', cap: 'bottom', radius: 22, card: true,
    pitch: 'The slide is one big rounded card with a soft margin, like a photo on a table. A slim dock under it holds play, the progress line and full screen.',
    fonts: { display: f('Young Serif', 'Regular'), body: f('Epilogue', 'Regular'), label: f('Epilogue', 'Medium') },
    fontLine: 'Young Serif + Epilogue', paletteLine: 'Apothecary: lavender oil, camphor',
    light: { bg: '#e7e6e2', card: '#f6f5f2', ink: '#34312c', muted: '#6a665e', line: '#d3d1cc', accent: '#6e5a96', accentInk: '#f4f1fa', glass: '#f6f5f2', bars: ['#6e5a96', '#a4c4a1', '#cfccc5'] },
    dark: { bg: '#121110', card: '#1f1d1a', ink: '#e8e6e1', muted: '#a09c93', line: '#38352f', accent: '#b9a3d6', accentInk: '#1d1529', glass: '#1f1d1a', bars: ['#b9a3d6', '#a4c4a1', '#4a463f'] } },
  { name: '07 · One button', ctl: 'ring', cap: 'bottom', radius: 999,
    pitch: 'The fewest controls possible: one round play button whose ring fills up as the reel plays, plus a small full screen button. Arrow keys and swipes still work.',
    fonts: { display: f('Funnel Display', 'SemiBold'), body: f('Funnel Sans', 'Regular'), label: f('Funnel Sans', 'Medium') },
    fontLine: 'Funnel Display + Funnel Sans', paletteLine: 'Apothecary: spruce, camphor',
    light: { bg: '#f2f4f2', ink: '#25302b', muted: '#5c6a63', line: '#d0d8d3', accent: '#304e4f', accentInk: '#eaf3f3', glass: '#ffffff', bars: ['#304e4f', '#a4c4a1', '#c5cdc8'] },
    dark: { bg: '#141816', ink: '#e1e8e4', muted: '#93a29b', line: '#2c3531', accent: '#9fd0c9', accentInk: '#0f2423', glass: '#232a27', bars: ['#9fd0c9', '#a4c4a1', '#3d4842'] } },
  { name: '08 · Today, softened', ctl: 'glass', cap: 'bottom', radius: 14,
    pitch: 'Today\'s slides with the tech stripped out: same bold bars and total box, but a friendly sans, softer corners, and one small glass pill bottom-right (play, 2 / 8, full screen).',
    fonts: { display: f('Commissioner', 'Bold'), body: f('Commissioner', 'Regular'), label: f('Commissioner', 'Medium') },
    fontLine: 'Commissioner', paletteLine: 'Synth panel: knob blue, patch yellow (softened)',
    light: { bg: '#f1f2f3', ink: '#24272a', muted: '#5f6367', line: '#d3d5d8', accent: '#2f5f9e', accentInk: '#eef4fb', glass: '#ffffff', bars: ['#24272a', '#4a7ec3', '#dcc300'] },
    dark: { bg: '#18191b', ink: '#eceef0', muted: '#989ca1', line: '#33363a', accent: '#8fb4e6', accentInk: '#0d1d33', glass: '#28292c', bars: ['#8fb4e6', '#4a7ec3', '#dcc300'] } },
];
let C, F;
const hex = h => { h = h.replace('#', ''); return { r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255 }; };
const solid = (h, o = 1) => [{ type: 'SOLID', color: hex(h), opacity: o }];
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
function E(p, x, y, d, fill, o = 1) { const n = figma.createEllipse(); n.resize(d, d); n.fills = solid(fill, o); p.appendChild(n); n.x = x; n.y = y; return n; }
function svg(p, s, x, y) { const n = figma.createNodeFromSvg(s); p.appendChild(n); n.x = x; n.y = y; return n; }
// --- slide content drawn straight onto the page (the page IS the slide) ---
function content(p, m, W, portrait, top) {
  const L = portrait ? 24 : 120, S = portrait ? .54 : 1;
  const k = portrait ? 1 : 1;
  let y = top;
  E(p, L, y + 6, portrait ? 8 : 12, m.accent);
  T(p, 'What TV costs a year now', { x: L + (portrait ? 16 : 24), y, font: F.label, size: portrait ? 13 : 19, color: m.muted });
  y += portrait ? 30 : 46;
  const t = T(p, 'Before: about $2,000', { x: L, y, font: F.display, size: portrait ? 44 : 76, color: m.ink, lh: 100, ls: -1.5, w: W - 2 * L });
  const i = t.characters.indexOf('$2,000'); t.setRangeFills(i, i + 6, solid(m.accent));
  y += t.height + (portrait ? 34 : 56);
  const rows = [['Telus TV (cancelled)', '$900', 1, '$75 a month'], ['Sportsnet+ alone', '$350', .39, 'per year'], ['Everything else: Apple One, Netflix, Prime…', '~$750', .83, 'estimate']];
  const maxW = portrait ? 200 : 880, bh = portrait ? 34 : 44;
  rows.forEach((r, j) => {
    T(p, r[0], { x: L, y, font: F.label, size: portrait ? 14 : 17, color: m.ink });
    y += portrait ? 24 : 30;
    const bw = maxW * r[2];
    R(p, { x: L, y, w: bw, h: bh, fill: m.bars[j], r: Math.min(C.radius, bh / 2) > 20 ? bh / 2 : Math.min(C.radius / 2, 8) });
    const a = T(p, r[1], { x: L + bw + (portrait ? 10 : 16), y: y + bh / 2 - (portrait ? 13 : 24), font: F.display, size: portrait ? 20 : 36, color: m.ink });
    T(p, r[3], { x: a.x + a.width + 8, y: a.y + a.height * .45, font: F.body, size: portrait ? 11 : 15, color: m.muted });
    y += bh + (portrait ? 26 : 30);
  });
  y += portrait ? 4 : 10;
  const bw = W - 2 * L, h = portrait ? 84 : 96;
  R(p, { x: L, y, w: bw, h, fill: m.ink, r: Math.min(C.radius, 18) });
  T(p, 'With Telus gone: about $1,100 a year.', { x: L + (portrait ? 18 : 32), y: y + (portrait ? 16 : 28), w: bw - (portrait ? 36 : 64), font: F.display, size: portrait ? 21 : 34, color: m.bg, lh: 115 });
  return y + h;
}
const CAP = 'Before, TV cost about two thousand dollars a year. Telus was nine hundred,';
function sub(p, m, x, y, w, size, align) {
  return T(p, CAP + ' Sportsnet plus alone is three fifty.', { x, y, w, font: F.body, size, color: m.ink, lh: 135, align });
}
function playIcon(p, m, x, y, d, filled) {
  if (filled !== false) E(p, x, y, d, m.accent);
  const c = filled === false ? m.ink : m.accentInk, s = d * .14, h = d * .36;
  R(p, { x: x + d / 2 - s * 1.5, y: y + (d - h) / 2, w: s, h, fill: c, r: 1 });
  R(p, { x: x + d / 2 + s * .5, y: y + (d - h) / 2, w: s, h, fill: c, r: 1 });
}
function fsIcon(p, m, x, y, d, ring) {
  if (ring) { const r = E(p, x, y, d, m.glass, .92); r.strokes = solid(m.line); r.strokeWeight = 1; }
  const s = Math.round(d * .4), o = (d - s) / 2, col = m.ink;
  svg(p, `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5" stroke="${col}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`, x + o, y + o);
}
function dots(p, m, x, y, gap, d, vertical) {
  for (let k = 0; k < 8; k++) {
    const on = k === 1, done = k < 1;
    const xx = vertical ? x : x + k * gap, yy = vertical ? y + k * gap : y;
    if (on && !vertical) R(p, { x: xx - 2, y: yy, w: d * 3, h: d, fill: m.accent, r: d });
    else E(p, xx, yy, on ? d * 1.6 : d, on ? m.accent : m.ink, done ? .7 : on ? 1 : .22);
  }
}
function controls(p, m, W, H, phone, capTop) {
  const ctl = C.ctl, M = phone ? 18 : 32;
  if (ctl === 'pill') {
    const pw = phone ? 250 : 300, ph = phone ? 52 : 56, x = (W - pw) / 2, y = H - ph - (phone ? 30 : 32);
    const pill = R(p, { x, y, w: pw, h: ph, fill: m.glass, r: ph / 2, o: .92 }); pill.strokes = solid(m.line); pill.strokeWeight = 1;
    playIcon(p, m, x + 6, y + 6, ph - 12);
    dots(p, m, x + ph + 18, y + ph / 2 - 4, phone ? 17 : 21, 8);
    fsIcon(p, m, x + pw - ph + 6, y + 6, ph - 12, false);
    if (C.cap === 'bottom') sub(p, m, phone ? 24 : 260, y - (phone ? 84 : 70), phone ? W - 48 : W - 520, phone ? 15 : 20, 'CENTER');
  } else if (ctl === 'corners') {
    R(p, { x: 0, y: 0, w: W, h: 3, fill: m.line }); R(p, { x: 0, y: 0, w: W * .19, h: 3, fill: m.accent });
    playIcon(p, m, M, H - M - (phone ? 56 : 60), phone ? 56 : 60);
    fsIcon(p, m, W - M - 44, H - M - 52, 44, true);
    if (phone) T(p, 'Swipe for the next part', { x: M + 70, y: H - M - 36, font: F.body, size: 12, color: m.muted });
  } else if (ctl === 'subtitle') {
    const y = H - (phone ? 170 : 112);
    sub(p, m, phone ? 24 : 300, y, phone ? W - 48 : W - 600, phone ? 15 : 22, 'CENTER');
    const by = phone ? H - 56 : y + 6;
    if (phone) { playIcon(p, m, W / 2 - 52, by - 6, 44); fsIcon(p, m, W / 2 + 8, by - 6, 44, true); }
    else { playIcon(p, m, W - 140, by, 44); fsIcon(p, m, W - 84, by, 44, true); }
    R(p, { x: phone ? 24 : 300, y: phone ? H - 80 : H - 30, w: phone ? W - 48 : W - 600, h: 2, fill: m.line });
    R(p, { x: phone ? 24 : 300, y: phone ? H - 80 : H - 30, w: (phone ? W - 48 : W - 600) * .19, h: 2, fill: m.accent });
  } else if (ctl === 'rail') {
    dots(p, m, W - (phone ? 18 : 40), phone ? 240 : H / 2 - 110, phone ? 26 : 30, 8, true);
    playIcon(p, m, M, H - M - 52, 52);
    sub(p, m, M + 70, H - M - 56, phone ? W - M - 100 : 640, phone ? 13 : 18);
    fsIcon(p, m, W - M - 40, phone ? 58 : M, 40, true);
  } else if (ctl === 'stories') {
    const top = phone ? 54 : 20, w = W - 2 * M, g = 5, sw = (w - 7 * g) / 8;
    for (let k = 0; k < 8; k++) { R(p, { x: M + k * (sw + g), y: top, w: sw, h: 3, fill: m.ink, o: .15, r: 2 }); if (k <= 1) R(p, { x: M + k * (sw + g), y: top, w: k ? sw * .45 : sw, h: 3, fill: m.ink, r: 2 }); }
    playIcon(p, m, W - M - 84, top + 16, 36, false); fsIcon(p, m, W - M - 40, top + 16, 36, false);
    sub(p, m, phone ? 24 : 260, H - (phone ? 110 : 96), phone ? W - 48 : W - 520, phone ? 15 : 20, 'CENTER');
    if (phone) T(p, 'Tap the sides to go back or forward', { x: 0, y: H - 34, w: W, font: F.body, size: 11, color: m.muted, align: 'CENTER' });
  } else if (ctl === 'dock') {
    const y = H - (phone ? 70 : 74);
    playIcon(p, m, M + 4, y + 8, 40);
    R(p, { x: M + 60, y: y + 27, w: W - 2 * M - 120, h: 3, fill: m.line, r: 2 }); R(p, { x: M + 60, y: y + 27, w: (W - 2 * M - 120) * .19, h: 3, fill: m.accent, r: 2 });
    T(p, '2 of 8', { x: M + 60, y: y + 38, font: F.label, size: 12, color: m.muted });
    fsIcon(p, m, W - M - 44, y + 8, 40, false);
  } else if (ctl === 'ring') {
    const d = phone ? 64 : 72, x = W - M - d, y = H - M - d;
    E(p, x, y, d, m.accent);
    svg(p, `<svg width="${d}" height="${d}" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg"><circle cx="36" cy="36" r="33" fill="none" stroke="${m.accentInk}" stroke-opacity=".25" stroke-width="4"/><path d="M36 3 A33 33 0 0 1 64.6 19.5" fill="none" stroke="${m.accentInk}" stroke-width="4" stroke-linecap="round"/></svg>`, x, y);
    playIcon(p, m, x + d * .2, y + d * .2, d * .6, false);
    p.children[p.children.length - 1].fills = solid(m.accentInk); p.children[p.children.length - 2].fills = solid(m.accentInk);
    fsIcon(p, m, x - 56, y + d / 2 - 22, 44, true);
    if (C.cap === 'bottom') { const s = sub(p, m, M, y + 4, phone ? W - 2 * M : 720, phone ? 14 : 19); if (phone) s.y = y - s.height - 18; }
  } else if (ctl === 'glass') {
    const pw = 170, ph = 48, x = W - M - pw, y = H - M - ph;
    const g = R(p, { x, y, w: pw, h: ph, fill: m.glass, r: ph / 2, o: .9 }); g.strokes = solid(m.line); g.strokeWeight = 1;
    playIcon(p, m, x + 5, y + 5, ph - 10);
    T(p, '2 / 8', { x: x + ph + 10, y: y + 14, font: F.label, size: 15, color: m.ink });
    fsIcon(p, m, x + pw - ph + 5, y + 5, ph - 10, false);
    for (let k = 0; k < 8; k++) R(p, { x: (W / 8) * k + 1, y: H - 4, w: W / 8 - 2, h: 4, fill: k <= 1 ? m.accent : m.ink, o: k <= 1 ? 1 : .12 });
    const s = sub(p, m, M, y - 2, phone ? W - 2 * M : 780, phone ? 13 : 19);
    if (phone) s.y = y - s.height - 16;
  }
}
function page(m, phone) {
  const W = phone ? 390 : 1440, H = phone ? 844 : 900;
  const fr = figma.createFrame(); fr.name = phone ? 'Phone · dark · 390' : 'Desktop · light · 1440';
  fr.resize(W, H); fr.fills = solid(m.bg); fr.clipsContent = true; if (phone) fr.cornerRadius = 44;
  let host = fr, HW = W;
  if (C.card) {
    const pad = phone ? 10 : 24, card = figma.createFrame(); card.name = 'Slide card';
    card.resize(W - 2 * pad, H - pad - (phone ? 84 : 98) - (phone ? 44 : 0)); card.fills = solid(m.card); card.cornerRadius = C.radius;
    fr.appendChild(card); card.x = pad; card.y = pad + (phone ? 44 : 0); host = card; HW = card.width;
  }
  if (phone) T(fr, '9:41', { x: 32, y: 16, font: F.label, size: 15, color: m.ink });
  const top = phone ? (C.ctl === 'stories' ? 120 : 100) : (C.ctl === 'stories' ? 100 : 90);
  content(host, m, HW, phone, C.card ? (phone ? 40 : 70) : top);
  if (C.card && C.cap === 'bottom') sub(host, m, phone ? 24 : 120, host.height - (phone ? 92 : 90), phone ? HW - 48 : 900, phone ? 13 : 19);
  controls(fr, m, W, H, phone);
  return fr;
}
const fams = new Map();
for (const s of SPECS) for (const k in s.fonts) fams.set(s.fonts[k].family + '|' + s.fonts[k].style, s.fonts[k]);
await Promise.all([...fams.values()].map(x => figma.loadFontAsync(x)));
const oldPg = figma.root.children.find(p => p.name.startsWith('Round 2')); if (oldPg) { await figma.setCurrentPageAsync(figma.root.children[0]); oldPg.remove(); }
figma.currentPage.name = 'Round 1 · techy (rejected)';
const pg = figma.createPage(); pg.name = 'Round 2 · warm, full-page';
await figma.setCurrentPageAsync(pg);
const out = [];
for (let IDX = 0; IDX < SPECS.length; IDX++) {
  C = SPECS[IDX]; F = C.fonts;
  const board = figma.createFrame(); board.name = C.name; board.resize(2000, 1150); board.fills = solid('#e9e9e7');
  board.x = (IDX % 2) * 2100; board.y = Math.floor(IDX / 2) * 1250;
  T(board, C.name, { x: 40, y: 30, font: F.display, size: 44, color: '#22211e' });
  T(board, C.pitch, { x: 40, y: 92, w: 1400, font: F.body, size: 18, color: '#45433e', lh: 135 });
  T(board, 'Fonts: ' + C.fontLine + '   ·   Palette: ' + C.paletteLine, { x: 40, y: 160, font: F.body, size: 14, color: '#6a675f' });
  const d = page(C.light, false); board.appendChild(d); d.x = 40; d.y = 210;
  const ph = page(C.dark, true); board.appendChild(ph); ph.x = 1540; ph.y = 210;
  out.push({ name: C.name, id: board.id });
}
return { page: pg.id, out };
