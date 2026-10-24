// ---- shared reel-concept builder (prepend SPEC as `const C = {...}` and IDX) ----
const hex = h => { h = h.replace('#', ''); return { r: parseInt(h.slice(0, 2), 16) / 255, g: parseInt(h.slice(2, 4), 16) / 255, b: parseInt(h.slice(4, 6), 16) / 255 }; };
const solid = (h, o = 1) => [{ type: 'SOLID', color: hex(h), opacity: o }];
const grad = (a, b) => ({ type: 'GRADIENT_LINEAR', gradientTransform: [[1, 0, 0], [0, 1, 0]], gradientStops: [{ position: 0, color: { ...hex(a), a: 1 } }, { position: 1, color: { ...hex(b), a: 1 } }] });
const F = C.fonts;
const need = new Map();
for (const k of Object.keys(F)) need.set(F[k].family + '|' + F[k].style, F[k]);
need.set('Hanken Grotesk|Regular', { family: 'Hanken Grotesk', style: 'Regular' });
await Promise.all([...need.values()].map(f => figma.loadFontAsync(f)));

function T(p, str, o) {
  const t = figma.createText();
  t.fontName = o.font; t.fontSize = o.size;
  t.characters = o.upper ? str.toUpperCase() : str;
  t.fills = solid(o.color, o.opacity ?? 1);
  if (o.ls) t.letterSpacing = { unit: 'PERCENT', value: o.ls };
  if (o.lh) t.lineHeight = { unit: 'PERCENT', value: o.lh };
  if (o.align) t.textAlignHorizontal = o.align;
  p.appendChild(t);
  if (o.w) { t.textAutoResize = 'HEIGHT'; t.resize(o.w, t.height); }
  t.x = o.x || 0; t.y = o.y || 0;
  return t;
}
function R(p, o) {
  const n = figma.createRectangle(); n.resize(o.w, o.h);
  n.fills = o.fill ? solid(o.fill, o.o ?? 1) : [];
  if (o.stroke) { n.strokes = solid(o.stroke, o.so ?? 1); n.strokeWeight = o.sw || 1; n.strokeAlign = 'INSIDE'; }
  n.cornerRadius = o.r || 0; p.appendChild(n); n.x = o.x; n.y = o.y; return n;
}
function E(p, x, y, d, fill) { const n = figma.createEllipse(); n.resize(d, d); n.fills = solid(fill); p.appendChild(n); n.x = x; n.y = y; return n; }
const U = s => C.upper ? s.toUpperCase() : s;
const MU = s => C.monoUpper === false ? s : s.toUpperCase();

// ---------- slide ----------
function slide(m, portrait) {
  const s = m.slide || m;
  const W = portrait ? 720 : 1280, H = portrait ? 1040 : 720, L = portrait ? 56 : 104;
  const f = figma.createFrame(); f.name = portrait ? 'Slide · portrait' : 'Slide · landscape';
  f.resize(W, H); f.fills = solid(s.bg); f.clipsContent = true; f.cornerRadius = 0;
  if (C.pattern === 'grid') {
    for (let x = 40; x < W; x += 40) R(f, { x, y: 0, w: 1, h: H, fill: s.line, o: x % 200 === 0 ? .9 : .35 });
    for (let y = 40; y < H; y += 40) R(f, { x: 0, y, w: W, h: 1, fill: s.line, o: y % 200 === 0 ? .9 : .35 });
  }
  if (C.pattern === 'glow') {
    const g = figma.createEllipse(); g.resize(W * .9, H * .9); f.appendChild(g); g.x = W * .45; g.y = -H * .35;
    g.fills = [{ type: 'GRADIENT_RADIAL', gradientTransform: [[1, 0, 0], [0, 1, 0]], gradientStops: [{ position: 0, color: { ...hex(s.accent), a: .28 } }, { position: 1, color: { ...hex(s.accent), a: 0 } }] }];
  }
  const ls = portrait ? 1.35 : 1;
  // chip
  if (C.chip === 'prompt') T(f, '$ ch01 --what-tv-costs', { x: L, y: 70, font: F.mono, size: 17 * ls, color: s.accent });
  else {
    E(f, L, 76, 13 * ls, s.accent);
    T(f, MU('Ch 01 — What TV costs a year now'), { x: L + 26 * ls, y: 70, font: F.mono, size: 16 * ls, color: s.muted, ls: 4 });
  }
  // title
  const tt = U(C.title || 'Before: about $2,000');
  const tsize = (C.titleSize || 64) * (portrait ? 1.2 : 1);
  const t = T(f, tt, { x: L, y: portrait ? 118 : 112, font: F.display, size: tsize, color: s.ink, ls: C.titleLs || 0, lh: C.titleLh || 100, w: W - 2 * L });
  const i = tt.indexOf('$2,000');
  if (i >= 0) try { t.setRangeFills(i, i + 6, C.gradientWord ? [grad(s.g1, s.g2)] : solid(s.accent)); } catch (e) { t.setRangeFills(i, i + 6, solid(s.accent)); }
  // bars
  const rows = [['Telus TV (cancelled)', '$900', 630, '$75 a month'], ['Sportsnet+ alone', '$350', 245, 'per year'], ['Everything else: Apple One, Netflix, Prime…', '~$750', 525, 'estimate']];
  rows.forEach((r, k) => {
    const y = portrait ? 380 + k * 150 : 280 + k * 92;
    const bw = r[2] * (portrait ? .52 : 1), bh = portrait ? 54 : 40;
    T(f, MU(r[0]), { x: L, y: y - (portrait ? 34 : 26), font: F.mono, size: 14 * ls, color: s.ink, ls: 3 });
    const style = C.bar || 'solid';
    if (style === 'outline') R(f, { x: L, y, w: bw, h: bh, stroke: s.bars[k], sw: 2, r: C.radius });
    else if (style === 'thin') { R(f, { x: L, y: y + bh - 6, w: W - 2 * L - (portrait ? 160 : 260), h: 1, fill: s.line }); R(f, { x: L, y: y + bh - 8, w: bw, h: 6, fill: s.bars[k], r: 3 }); }
    else R(f, { x: L, y, w: bw, h: bh, fill: s.bars[k], r: C.radius });
    const a = T(f, r[1], { x: L + bw + 14, y: y + (style === 'thin' ? bh - 46 * ls : bh / 2 - 21 * ls), font: F.display, size: 34 * ls, color: s.ink });
    T(f, MU(r[3]), portrait ? { x: L, y: y + bh + 10, font: F.mono, size: 16, color: s.muted } : { x: a.x + a.width + 10, y: a.y + a.height - 22, font: F.mono, size: 13 * ls, color: s.muted });
  });
  // total
  const ty = portrait ? 840 : 568, th = portrait ? 140 : 92, tw = W - 2 * L;
  const tstr = 'With Telus gone: about $1,100 a year.';
  const tot = C.total || 'inverse';
  let tc = s.ink;
  if (tot === 'inverse') { R(f, { x: L, y: ty, w: tw, h: th, fill: s.ink, r: C.radius }); tc = s.bg; }
  if (tot === 'accent') { R(f, { x: L, y: ty, w: tw, h: th, fill: s.accent, r: C.radius }); tc = s.accentInk; }
  if (tot === 'outline') R(f, { x: L, y: ty, w: tw, h: th, stroke: s.accent, sw: 2, r: C.radius });
  if (tot === 'rule') R(f, { x: L, y: ty, w: tw, h: 1, fill: s.ink, o: .25 });
  T(f, tstr, { x: L + (tot === 'rule' ? 0 : 28), y: ty + (portrait ? 30 : 26), font: C.totalFont === 'body' ? F.strong : F.display, size: (C.totalSize || 32) * (portrait ? 1.15 : 1), color: tc, w: tw - 56 });
  return f;
}
function placeSlide(p, m, portrait, x, y, w) {
  const s = slide(m, portrait); p.appendChild(s); s.rescale(w / s.width); s.x = x; s.y = y;
  if (C.stage === 'framed') { s.strokes = solid((m.slide || m).line); s.strokeWeight = 2 / (w / (portrait ? 720 : 1280)); s.strokeAlign = 'INSIDE'; s.cornerRadius = C.radius; }
  if (C.stage === 'rounded') s.cornerRadius = C.radius;
  return s;
}

// ---------- chrome ----------
const CAP = 'Before, TV cost about two thousand dollars a year. Telus was nine hundred, Sportsnet plus alone is three fifty, and the rest is roughly seven fifty.';
const SPOKEN = 'Before, TV cost about two thousand dollars a year. Telus was nine hundred,'.length;
function caption(p, m, x, y, w, size, font) {
  const t = T(p, (C.capPrefix || '') + CAP, { x, y, w, font: font || F.body, size, color: m.ink, lh: 135 });
  const off = (C.capPrefix || '').length;
  t.setRangeFills(off + SPOKEN, t.characters.length, solid(m.muted, .8));
  if (C.capPrefix) t.setRangeFills(0, off, solid(m.accent));
  return t;
}
function header(p, m, x, y, w, size) {
  T(p, MU('The pros, cons and options'), { x, y, font: F.mono, size: 12, color: m.muted, ls: 6 });
  return T(p, U('Is the cheap TV box worth it?'), { x, y: y + 24, w, font: F.display, size, color: m.ink, ls: C.titleLs || 0, lh: 105 });
}
function progress(p, m, x, y, w, style, small) {
  const n = 8, cur = 1, frac = .45;
  if (style === 'segments') {
    const g = 6, sw = (w - g * (n - 1)) / n;
    for (let k = 0; k < n; k++) {
      R(p, { x: x + k * (sw + g), y, w: sw, h: 5, fill: m.line, r: 3 });
      const fw = k < cur ? sw : k === cur ? sw * frac : 0;
      if (fw) R(p, { x: x + k * (sw + g), y, w: fw, h: 5, fill: m.accent, r: 3 });
    }
    T(p, '02 / 08', { x, y: y + 14, font: F.mono, size: 11, color: m.muted });
  } else if (style === 'line') {
    R(p, { x, y: y + 2, w, h: 1, fill: m.ink, o: .14 });
    const px = w * ((cur + frac) / n);
    R(p, { x, y: y + 1, w: px, h: 3, fill: m.ink, r: 2 });
    for (let k = 1; k < n; k++) R(p, { x: x + w * k / n, y: y - 3, w: 1, h: 11, fill: m.ink, o: .2 });
    T(p, '0:21', { x, y: y + 14, font: F.mono, size: 11, color: m.muted });
    T(p, '1:40', { x: x + w - 26, y: y + 14, font: F.mono, size: 11, color: m.muted });
  } else if (style === 'blocks') {
    const b = '■■' + '□□□□□□';
    const t = T(p, '[' + '■' + '▪' + '······' + ']  02/08   0:21 / 1:40', { x, y, font: F.mono, size: small ? 12 : 14, color: m.muted });
    t.setRangeFills(1, 3, solid(m.accent));
  } else if (style === 'ticks') {
    const sw = w / n;
    for (let k = 0; k < n; k++) {
      const done = k <= cur;
      T(p, String(k + 1).padStart(2, '0'), { x: x + k * sw, y, font: F.mono, size: small ? 11 : 13, color: done ? m.ink : m.muted, opacity: done ? 1 : .6 });
      R(p, { x: x + k * sw, y: y + 22, w: sw - 8, h: k === cur ? 3 : 1, fill: k < cur ? m.ink : k === cur ? m.accent : m.line });
    }
  }
}
function keycap(p, m, x, y, key, label) {
  const k = T(p, key, { x: x + 8, y: y + 5, font: F.mono, size: 11, color: m.ink });
  const r = R(p, { x, y, w: k.width + 16, h: 24, stroke: m.line, sw: 1, r: Math.min(C.radius, 6) || 0 });
  r.fills = solid(m.surface || m.bg);
  p.insertChild(p.children.indexOf(k), r);
  const l = T(p, label, { x: x + k.width + 24, y: y + 4, font: F.body, size: 13, color: m.muted });
  return l.x + l.width + 22;
}
function controls(p, m, x, y, style) {
  // primary pause button
  const bw = 104;
  R(p, { x, y: y - 6, w: bw, h: 36, fill: m.accent, r: C.btnRadius ?? C.radius });
  R(p, { x: x + 18, y: y + 5, w: 4, h: 14, fill: m.accentInk }); R(p, { x: x + 26, y: y + 5, w: 4, h: 14, fill: m.accentInk });
  T(p, C.btnUpper ? 'PAUSE' : 'Pause', { x: x + 40, y: y + 3, font: F.strong, size: 14, color: m.accentInk });
  let cx = x + bw + 24;
  const keys = [['Space', 'Pause'], ['← →', 'Beats'], ['R', 'Replay'], ['S', 'Pace: Normal'], ['F', 'Full screen']];
  if (style === 'text') {
    T(p, keys.map(k => '[' + k[0].toLowerCase() + '] ' + k[1].toLowerCase()).join('   '), { x: cx, y: y + 4, font: F.mono, size: 12, color: m.muted });
  } else for (const k of keys) cx = keycap(p, m, cx, y, k[0], k[1]);
}
function phoneControls(p, m, y) {
  R(p, { x: 20, y, w: 120, h: 44, fill: m.accent, r: C.btnRadius ?? C.radius });
  R(p, { x: 44, y: y + 15, w: 4, h: 14, fill: m.accentInk }); R(p, { x: 52, y: y + 15, w: 4, h: 14, fill: m.accentInk });
  T(p, C.btnUpper ? 'PAUSE' : 'Pause', { x: 66, y: y + 13, font: F.strong, size: 15, color: m.accentInk });
  R(p, { x: 152, y, w: 104, h: 44, stroke: m.line, r: C.btnRadius ?? C.radius });
  T(p, 'Pace: Normal', { x: 166, y: y + 14, font: F.body, size: 13, color: m.ink });
  T(p, 'Swipe ← → for beats\nTap a segment to jump', { x: 268, y: y + 4, font: F.body, size: 11, color: m.muted, lh: 130 });
}

// ---------- desktop (light) ----------
function desktop(m) {
  const f = figma.createFrame(); f.name = 'Desktop · light · 1440'; f.resize(1440, 1040); f.fills = solid(m.bg); f.clipsContent = true;
  const L = C.layout;
  if (L === 'column') {
    T(f, MU('Reels'), { x: 40, y: 34, font: F.mono, size: 12, color: m.ink, ls: 6 });
    T(f, MU('04 · Dad\'s TV box'), { x: 1300, y: 34, font: F.mono, size: 12, color: m.muted, ls: 6 });
    header(f, m, 360, 104, 720, 38);
    placeSlide(f, m, false, 360, 214, 720);
    caption(f, m, 360, 652, 720, 19);
    progress(f, m, 360, 770, 720, 'line');
    controls(f, m, 360, 830, 'text');
  } else if (L === 'split') {
    header(f, m, 64, 44, 960, 40);
    R(f, { x: 64, y: 142, w: 1312, h: 3, fill: m.ink }); R(f, { x: 64, y: 148, w: 1312, h: 1, fill: m.ink });
    placeSlide(f, m, false, 64, 176, 960);
    R(f, { x: 1048, y: 176, w: 1, h: 540, fill: m.line });
    T(f, MU('Transcript'), { x: 1072, y: 176, font: F.mono, size: 12, color: m.muted, ls: 6 });
    const beats = [['01', 'Will the cheap box just work, the way Telus TV does? Not quite.', 'past'], ['02', CAP, 'now'], ['03', 'Four ways forward, in yearly costs.', 'next'], ['04', 'The appeal is easy to see.', 'next'], ['05', 'But it isn\'t Telus.', 'next']];
    let y = 206;
    for (const b of beats) {
      T(f, b[0], { x: 1072, y, font: F.mono, size: 12, color: b[2] === 'now' ? m.accent : m.muted });
      const t = T(f, b[1], { x: 1106, y: y - 3, w: 270, font: b[2] === 'now' ? F.strong : F.body, size: b[2] === 'now' ? 16 : 14, color: b[2] === 'next' ? m.muted : m.ink, lh: 135, opacity: b[2] === 'past' ? .55 : 1 });
      if (b[2] === 'now') { R(f, { x: 1060, y: y - 2, w: 3, h: t.height, fill: m.accent }); t.setRangeFills(SPOKEN, t.characters.length, solid(m.muted)); }
      y += t.height + 22;
    }
    R(f, { x: 64, y: 748, w: 1312, h: 1, fill: m.ink });
    progress(f, m, 64, 772, 960, 'ticks');
    controls(f, m, 64, 840, 'keys');
  } else if (L === 'poster') {
    placeSlide(f, m, false, 0, 0, 1440);
    caption(f, m, 64, 846, 900, 26, F.strong);
    T(f, MU('The pros, cons and options'), { x: 1040, y: 850, font: F.mono, size: 12, color: m.muted, ls: 6 });
    T(f, U('Is the cheap TV box worth it?'), { x: 1040, y: 874, w: 340, font: F.display, size: 26, color: m.ink, lh: 105 });
    progress(f, m, 64, 950, 600, 'blocks');
    controls(f, m, 64, 990, 'keys');
  } else if (L === 'captionHero') {
    header(f, m, 80, 56, 600, 22);
    caption(f, m, 80, 178, 560, 40, F.display);
    placeSlide(f, m, false, 700, 178, 660);
    progress(f, m, 700, 572, 660, 'segments');
    T(f, 'Up next · Four ways forward', { x: 700, y: 620, font: F.body, size: 15, color: m.muted });
    controls(f, m, 80, 940, 'keys');
  } else if (L === 'gallery') {
    R(f, { x: 160, y: 56, w: 1120, h: 680, fill: m.surface });
    placeSlide(f, m, false, 220, 92, 1000);
    T(f, MU('Reel 04 · The pros, cons and options'), { x: 160, y: 780, font: F.mono, size: 12, color: m.muted, ls: 4 });
    T(f, 'Is the cheap TV box worth it?', { x: 160, y: 804, w: 420, font: F.display, size: 40, color: m.ink, lh: 100 });
    caption(f, m, 640, 784, 640, 19);
    progress(f, m, 160, 920, 1120, 'ticks');
    controls(f, m, 160, 980, 'keys');
  } else { // stack
    header(f, m, 170, 40, 1100, 34);
    placeSlide(f, m, false, 170, 140, 1100);
    caption(f, m, 170, 790, 1100, 21);
    progress(f, m, 170, 886, 1100, C.progress || 'segments');
    controls(f, m, 170, 950, C.controls || 'keys');
  }
  return f;
}
// ---------- phone (dark) ----------
function phone(m) {
  const f = figma.createFrame(); f.name = 'Phone · dark · 390'; f.resize(390, 844); f.fills = solid(m.bg); f.clipsContent = true; f.cornerRadius = 44;
  T(f, '9:41', { x: 32, y: 16, font: { family: 'Hanken Grotesk', style: 'Regular' }, size: 15, color: m.ink });
  if (C.layout === 'poster') {
    placeSlide(f, m, true, 0, 54, 390);
    caption(f, m, 20, 630, 350, 16, F.strong);
    progress(f, m, 20, 722, 350, 'blocks', true);
  } else if (C.layout === 'captionHero') {
    T(f, MU('The pros, cons and options'), { x: 20, y: 56, font: F.mono, size: 10, color: m.muted, ls: 6 });
    caption(f, m, 20, 78, 350, 21, F.display);
    placeSlide(f, m, true, 20, 300, 350);
    progress(f, m, 20, 818 - 52 - 30, 350, 'segments');
  } else {
    T(f, MU('The pros, cons and options'), { x: 20, y: 58, font: F.mono, size: 10, color: m.muted, ls: 6 });
    T(f, U('Is the cheap TV box worth it?'), { x: 20, y: 76, w: 350, font: F.display, size: 22, color: m.ink, lh: 105 });
    placeSlide(f, m, true, 20, 116, 350);
    caption(f, m, 20, 636, 350, 15);
    progress(f, m, 20, 728, 350, { split: 'ticks', gallery: 'ticks', column: 'line' }[C.layout] || C.progress || 'segments', true);
  }
  phoneControls(f, m, 776);
  return f;
}

// ---------- board ----------
const board = figma.createFrame(); board.name = C.name; board.resize(2030, 1300); board.fills = solid('#e8e9e8');
board.x = (IDX % 2) * 2130; board.y = Math.floor(IDX / 2) * 1400;
T(board, C.name, { x: 40, y: 32, font: F.display, size: 44, color: '#1c1d1c' });
T(board, C.pitch, { x: 40, y: 94, w: 1400, font: F.body, size: 18, color: '#3d3f3d', lh: 135 });
T(board, 'Fonts: ' + C.fontLine + '   ·   Palette: ' + C.paletteLine, { x: 40, y: 150, font: { family: 'Hanken Grotesk', style: 'Regular' }, size: 14, color: '#5d605d' });
const d = desktop(C.light); board.appendChild(d); d.x = 40; d.y = 210;
const ph = phone(C.dark); board.appendChild(ph); ph.x = 1560; ph.y = 210;
T(board, 'Desktop · light', { x: 40, y: 1262, font: { family: 'Hanken Grotesk', style: 'Regular' }, size: 13, color: '#5d605d' });
T(board, 'Phone · dark', { x: 1560, y: 1064, font: { family: 'Hanken Grotesk', style: 'Regular' }, size: 13, color: '#5d605d' });
return { boardId: board.id, desktopId: d.id, phoneId: ph.id };
