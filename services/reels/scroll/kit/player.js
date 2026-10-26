// Scroll-to-read reel player (from the pages "scroll-read" mockup, 2026-10-24), made reusable.
// The page sets window.REEL = { id, title, audio: { <block>: { src, marks } }, ask: {...}, next: {...} } before this runs.
// Narrated text: every [data-read] block. Shown-only extras: .f formulas, .key keys, .try checks (reading pauses at a check).
const REEL = window.REEL || { id: "reel", audio: {} };
const NS = "reel:" + REEL.id + ":";
const store = {
  get(k, d) { try { const v = localStorage.getItem(NS + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(NS + k, JSON.stringify(v)); } catch {} },
};

// Feel knobs: default, min, max, step live on the sliders below; values persist per browser, shared by every reel.
const T = { wpm: 310, thr: 16, pull: 1, fly: .13, fade: 70 };   // Matt's picks, 2026-10-24
const S = { voice: true, tuneOpen: false };
try {
  const saved = JSON.parse(localStorage.getItem("scroll-read-settings") || "{}");
  for (const k in T) if (typeof saved[k] === "number") T[k] = saved[k];
  for (const k in S) if (typeof saved[k] === "boolean") S[k] = saved[k];
} catch {}
const save = () => { try { localStorage.setItem("scroll-read-settings", JSON.stringify({ ...T, ...S })); } catch {} };

const $ = s => document.querySelector(s);
const dest = $("#dest"), stretch = $("#stretch"), blob = $("#blob"), centre = $("#centre"), pill = $("#pill"), bar = $("#bar");

// Wrap every word of each [data-read] block in a span.
const words = [];
const blockStart = [];
for (const el of document.querySelectorAll("[data-read]")) {
  const b = blockStart.length; blockStart.push(words.length);
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const n of nodes) {
    const frag = document.createDocumentFragment();
    for (const part of n.textContent.split(/([ \t\n]+)/)) {
      if (!part) continue;
      if (/^[ \t\n]+$/.test(part)) { frag.append(part); continue; }
      const s = document.createElement("span"); s.className = "w"; s.textContent = part;
      s.dataset.i = words.length; s._block = el; s._b = b; s._k = words.length - blockStart[b]; words.push(s); frag.append(s);
    }
    n.replaceWith(frag);
  }
}

// Checks: a .try after block b pauses the reading when block b ends, until it has been tried once.
// Quiz mode (2026-10-26): the first pick on each check is scored; a missed check is queued and comes back,
// options reshuffled, at the next empty <div class="try redo" data-id="…"> slot at least one section later;
// the end panel shows the score and lets the reader retry whatever is still missed.
const tries = {};                      // block index → .try element (or .redo slot)
{ let b = -1; for (const el of document.querySelectorAll("[data-read], .try")) { if (el.matches("[data-read]")) b++; else if (b >= 0 && !tries[b]) tries[b] = el; } }
const tried = new Set(store.get("tried", []));
const firstPick = store.get("first", {});  // check id → true/false on its first pick
const missed = store.get("missed", []); // ids still to come back, oldest first
const checkById = {}; for (const t of document.querySelectorAll(".try[data-id]:not(.redo)")) checkById[t.dataset.id] = t;
let waiting = null;                    // the .try the reading is paused at

function shuffled(a) { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function sectionOf(el) { return [...document.querySelectorAll("#text > section")].indexOf(el.closest("section")); }
function scoreLine() {
  const ids = Object.keys(checkById), seen = ids.filter(i => i in firstPick), right = seen.filter(i => firstPick[i]);
  return { total: ids.length, seen: seen.length, right: right.length };
}
function updateScore() {
  const el = $("#score"); if (!el) return;
  const s = scoreLine(); el.hidden = !s.seen;
  el.textContent = s.right + " / " + s.seen + " right first try";
}
function record(id, ok) {
  if (!(id in firstPick)) { firstPick[id] = ok; store.set("first", firstPick); }
  if (!ok && !missed.includes(id)) missed.push(id);
  store.set("missed", missed); updateScore();
}
// Wires a check's options. again = true for comebacks and end-of-reel retries (they clear a miss when right).
function wire(t, again) {
  const id = t.dataset.of || t.dataset.id;
  const after = document.createElement("div"); after.className = "after"; after.hidden = true;
  const go = document.createElement("button"); go.textContent = "Continue reading ▸"; go.onclick = () => leaveTry(t);
  const ask = document.createElement("button"); ask.textContent = "Ask about this"; ask.className = "askthis";
  ask.onclick = () => window.reelAsk?.open({ quote: t.querySelector(".q")?.textContent || "" });
  if (t.closest("#end")) go.remove();
  after.append(go, ask); t.append(after);
  let picked = false;
  for (const o of t.querySelectorAll("button.opt")) o.onclick = () => {
    const ok = o.hasAttribute("data-ok");
    o.dataset.picked = ok ? "ok" : "no";
    if (!picked) {
      picked = true;
      if (again) { if (ok) { const i = missed.indexOf(id); if (i >= 0) missed.splice(i, 1); store.set("missed", missed); } else if (!missed.includes(id)) { missed.push(id); store.set("missed", missed); } updateScore(); }
      else record(id, ok);
    }
    t.querySelector(".why")?.remove();
    const why = document.createElement("p"); why.className = "why";
    why.innerHTML = (ok ? "<b>Yes.</b> " : "<b>Not quite.</b> ") + (o.dataset.why || "") + (ok ? "" : " <i>Try another option.</i>");
    o.after(why); after.hidden = false;
    go.textContent = ok ? "Continue reading ▸" : "Skip and keep reading ▸";
    if (!ok && !again && !t.closest("#end")) why.innerHTML += " <i>This one will come back later.</i>";
  };
}
// Fills a comeback slot with a fresh copy of the oldest missed check from an earlier section.
function cloneCheck(id, into) {
  const src = checkById[id]; if (!src) return null;
  into.innerHTML = ""; into.dataset.of = id; into.classList.add("back");
  const q = src.querySelector(".q").cloneNode(true); into.append(q);
  for (const o of shuffled(src.querySelectorAll("button.opt"))) { const c = o.cloneNode(true); delete c.dataset.picked; into.append(c); }
  wire(into, true); return into;
}
function fillRedo(slot) {
  if (slot.dataset.of) return true;
  const here = sectionOf(slot);
  const id = missed.find(m => checkById[m] && sectionOf(checkById[m]) < here);
  if (!id) return false;
  cloneCheck(id, slot); slot.hidden = false; return true;
}
for (const t of document.querySelectorAll(".try:not(.redo)")) wire(t, false);
for (const r of document.querySelectorAll(".try.redo")) r.hidden = true;

function endReview() {
  const box = $("#review"); if (!box) return;
  const s = scoreLine(); box.innerHTML = "";
  const h = document.createElement("p"); h.className = "tally";
  h.innerHTML = s.seen ? "<b>" + s.right + " of " + s.seen + "</b> right on the first try." : "";
  box.append(h);
  const left = missed.filter(id => checkById[id]);
  if (left.length) {
    const p = document.createElement("p"); p.className = "tally";
    p.textContent = left.length === 1 ? "One question still needs another go:" : left.length + " questions still need another go:";
    box.append(p);
    for (const id of left) { const d = document.createElement("div"); d.className = "try back"; box.append(d); cloneCheck(id, d); }
  } else if (s.seen) {
    const p = document.createElement("p"); p.className = "tally"; p.textContent = "Nothing left to redo. Nice.";
    box.append(p);
  }
}
updateScore();

let idx = 0, playing = true, acc = 0, ended = false;
const H = () => innerHeight;
const docRect = el => { const r = el.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height }; };

function dur(i) {
  const t = words[i].textContent; let d = 60000 / T.wpm;
  d *= .7 + Math.min(t.length, 12) / 20;
  if (/[.!?]$/.test(t)) d *= 2.1; else if (/[,;:]$/.test(t)) d *= 1.5;
  if (words[i + 1] && words[i + 1]._block !== words[i]._block) d *= 1.6;
  return d;
}
function setIdx(i) {
  idx = Math.max(0, Math.min(words.length - 1, i));
  words.forEach((w, j) => w.classList.toggle("done", j < idx));
  bar.style.width = (idx / (words.length - 1) * 100) + "%";
  store.set("position", idx);
}
// True (and the reading stops) when block b is followed by a check not yet tried.
function gate(b) {
  const t = tries[b];
  if (!t) return false;
  if (t.classList.contains("redo")) { if (t._done || !fillRedo(t)) return false; }
  else if (tried.has(t.dataset.id)) return false;
  waiting = t; playing = false; syncPlay(); stopVoice();
  t.classList.add("waiting");
  const r = t.getBoundingClientRect();
  if (r.top < H() * .1 || r.bottom > H() * .9) { scrollTo({ top: scrollY + r.top - H() * .3, behavior: "smooth" }); }
  setTimeout(() => { expectedY = scrollY; }, 700);
  return true;
}
function leaveTry(t) {
  if (t.classList.contains("redo")) t._done = true; else { tried.add(t.dataset.id); store.set("tried", [...tried]); }
  t.classList.remove("waiting");
  if (waiting === t) {
    waiting = null;
    const b = +Object.keys(tries).find(k => tries[k] === t);
    if (b + 1 < blockStart.length) { setIdx(blockStart[b + 1]); acc = 0; playing = true; ended = false; syncPlay(); restartVoice(); }
    else finish();
  }
}

// ---- Scroll gestures. Any scroll we didn't cause ourselves is the reader's. ----
let g = null;
let touching = false, idleTimer = 0, expectedY = scrollY, following = false;
function gestureStart() { if (!g) g = { start: expectedY, snapped: false, t: 0 }; following = false; }
function gestureEnd() {
  if (!g) return;
  if (g.snapped) { setIdx(centreIdx()); acc = 0; restartVoice(); }
  g = null; expectedY = scrollY;
}
function armIdle() { clearTimeout(idleTimer); idleTimer = setTimeout(() => { if (!touching) gestureEnd(); }, 170); }
addEventListener("touchstart", e => { if (e.target.closest?.("#ask, #rbar, #rsheet, #tune")) return; touching = true; gestureStart(); armIdle(); }, { passive: true });
addEventListener("touchend", () => { touching = false; armIdle(); }, { passive: true });
addEventListener("touchcancel", () => { touching = false; armIdle(); }, { passive: true });
addEventListener("wheel", e => { if (e.target.closest?.("#ask, #rsheet")) return; gestureStart(); armIdle(); }, { passive: true });
let drag = null;
addEventListener("mousedown", e => {
  if (e.button !== 1) return;
  e.preventDefault();
  drag = { y: e.clientY }; touching = true; gestureStart(); document.body.classList.add("dragging");
});
addEventListener("mousemove", e => { if (!drag) return; scrollBy(0, drag.y - e.clientY); drag.y = e.clientY; armIdle(); });
function dragEnd() { if (!drag) return; drag = null; touching = false; document.body.classList.remove("dragging"); armIdle(); }
addEventListener("mouseup", e => { if (e.button === 1) dragEnd(); });
addEventListener("blur", dragEnd);
addEventListener("auxclick", e => { if (e.button === 1) e.preventDefault(); });
addEventListener("scroll", () => {
  if (!g && Math.abs(scrollY - expectedY) > 2) gestureStart();
  if (g) armIdle(); else expectedY = scrollY;
}, { passive: true });

function centreIdx() {
  const cy = H() / 2; let lo = 0, hi = words.length - 1;
  while (lo < hi) { const m = (lo + hi) >> 1; if (words[m].getBoundingClientRect().bottom < cy) lo = m + 1; else hi = m; }
  return lo;
}

// ---- Narration: recorded at build time (Speechify, word timings), shipped with the page. ----
const audio = new Audio(); audio.preload = "auto";
let clipBlock = -1, clipTimes = null;
const norm = w => w.toLowerCase().replace(/[^a-z0-9]/g, "");
function align(b, marks) {
  const n = (b + 1 < blockStart.length ? blockStart[b + 1] : words.length) - blockStart[b], t = []; let j = 0;
  for (let k = 0; k < n; k++) {
    const w = norm(words[blockStart[b] + k].textContent); let hit = -1;
    if (w) for (let m = j; m < Math.min(j + 4, marks.length); m++) { const v = norm(marks[m].w); if (v && (v === w || w.startsWith(v) || v.startsWith(w))) { hit = m; break; } }
    if (hit >= 0) { t.push(marks[hit].s); j = hit + 1; } else t.push(null);
  }
  return t.map((x, k) => x ?? t.slice(0, k).reverse().find(v => v != null) ?? 0);
}
const clips = new Map();
function fetchBlock(b) {
  if (!clips.has(b)) {
    const a = REEL.audio?.[b];
    clips.set(b, a ? Promise.resolve({ src: a.src, t: align(b, a.marks) }) : Promise.reject(new Error("no recording")));
    clips.get(b).catch(() => {});
  }
  return clips.get(b);
}
const VOICE_TITLE = "Narration recorded with a Speechify voice. Off: the highlight still reads at your speed.";
function voiceNote(msg) { const l = $("#voice").parentElement; l.dataset.note = msg || ""; l.title = msg || VOICE_TITLE; }
const voiceOn = () => $("#voice").checked;
function stopVoice() { audio.pause(); clipBlock = -1; }
let voiceGen = 0;
async function restartVoice() {
  stopVoice(); const gen = ++voiceGen;
  if (!voiceOn() || !playing || ended) return;
  const w = words[idx]; let clip;
  try { clip = await fetchBlock(w._b); voiceNote(); }
  catch (e) { voiceNote("Voice unavailable here: reading silently"); return; }
  if (gen !== voiceGen) return;
  clipBlock = w._b; clipTimes = clip.t; audio.playbackRate = Math.min(2, Math.max(.5, T.wpm / 230));
  const seek = () => {
    if (gen !== voiceGen) return;
    audio.currentTime = Math.max(0, clip.t[w._k] - .05); audio.playbackRate = Math.min(2, Math.max(.5, T.wpm / 230));
    audio.play().catch(e => { if (e.name === "NotAllowedError") waitForTap(); else { clipBlock = -1; voiceNote("Voice unavailable here: reading silently"); } });
  };
  if (audio.getAttribute("src") === clip.src && audio.readyState >= 1) seek();
  else { audio.src = clip.src; audio.addEventListener("loadedmetadata", seek, { once: true }); }
  if (w._b + 1 < blockStart.length) fetchBlock(w._b + 1).catch(() => {});
}
let tapWait = null;
function waitForTap() {
  if (tapWait) return;
  playing = false; syncPlay(); stopVoice(); voiceNote("Tap anywhere to start reading");
  tapWait = e => {
    removeEventListener("pointerdown", tapWait, true); removeEventListener("keydown", tapWait, true); tapWait = null; voiceNote();
    if (e.target.closest?.("button, input, label, #tune, #ask, textarea")) return;
    if (e.type === "keydown" && e.code === "Space") return;
    playing = true; syncPlay(); setTimeout(restartVoice, 0);
  };
  addEventListener("pointerdown", tapWait, true); addEventListener("keydown", tapWait, true);
}
audio.onended = () => {
  if (clipBlock < 0) return;
  const done = clipBlock, next = done + 1;
  if (gate(done)) return;
  if (next >= blockStart.length) return finish();
  setIdx(blockStart[next]); acc = 0; restartVoice();
};
const voiceDriving = () => clipBlock >= 0 && !audio.paused;
function voiceTick() {
  if (!voiceDriving() || g?.snapped) return;
  const t = clipTimes, now = audio.currentTime + .04;
  let k = 0; while (k + 1 < t.length && t[k + 1] <= now) k++;
  const j = blockStart[clipBlock] + k;
  if (j !== idx) { setIdx(j); acc = 0; }
}

function finish() { ended = true; playing = false; endReview(); $("#end").hidden = false; setIdx(words.length - 1); words.at(-1).classList.add("done"); syncPlay(); stopVoice(); }
function syncPlay() { $("#play").textContent = playing ? "❚❚" : "▶"; $("#play").setAttribute("aria-label", playing ? "Pause" : "Play"); }
function togglePlay() {
  if (ended) return again();
  if (waiting && !playing) return leaveTry(waiting);
  playing = !playing; syncPlay();
  if (playing) restartVoice(); else stopVoice();
}
function again() { ended = false; $("#end").hidden = true; setIdx(0); acc = 0; playing = true; syncPlay(); scrollTo(0, 0); expectedY = scrollY; restartVoice(); }

// ---- Frame loop: advance reading, auto-follow, place the blob. ----
let sl = 0, bx = 0, by = 0, bw = 0, bh = 0, last = performance.now(), first = true;
function frame(now) {
  const dt = Math.min(64, now - last); last = now;
  const thrPx = T.thr / 100 * H();
  const guarding = g && playing && !ended;
  if (g && !guarding) g.t = 0;
  if (guarding) {
    const d = scrollY - g.start; g.t = Math.min(1, Math.abs(d) / thrPx);
    if (!g.snapped && Math.abs(d) >= thrPx) { g.snapped = true; navigator.vibrate?.(8); stopVoice(); }
  }

  voiceTick();
  if (playing && !ended && !g?.snapped && !voiceDriving()) {
    acc += dt;
    while (playing && acc >= dur(idx)) {
      acc -= dur(idx);
      if (idx >= words.length - 1) { finish(); break; }
      if (words[idx + 1]._b !== words[idx]._b && gate(words[idx]._b)) { acc = 0; break; }
      setIdx(idx + 1);
    }
  }

  if (!g && playing) {
    const r = words[idx].getBoundingClientRect();
    if (r.top > H() * .64 || r.bottom < H() * .16) following = true;
    if (following) {
      const target = scrollY + r.top - H() * .4, next = scrollY + (target - scrollY) * .09;
      if (Math.abs(target - scrollY) < 1.5) following = false;
      else { scrollTo(0, Math.round(next)); expectedY = scrollY; }
    }
  }

  let k = .32, tx, ty, tw, th, pullLen = 0;
  if (g?.snapped) {
    const r = docRect(words[centreIdx()]); [tx, ty, tw, th] = [r.x, r.y, r.w, r.h]; k = T.fly;
  } else {
    const r = docRect(words[idx]); [tx, ty, tw, th] = [r.x, r.y, r.w, r.h];
    if (guarding) {
      const s2 = g.t * g.t; tw *= 1 - .14 * s2; tx += r.w * .07 * s2; k = .45;
      pullLen = (scrollY + H() / 2 - (r.y + r.h / 2)) * T.pull * s2 * .8;
    }
  }
  const padX = 6, padY = 2; tx -= padX; ty -= padY; tw += padX * 2; th += padY * 2;
  if (first) { bx = tx; by = ty; bw = tw; bh = th; first = false; }
  const kk = 1 - Math.pow(1 - k, dt / 16.7);
  bx += (tx - bx) * kk; by += (ty - by) * kk; bw += (tw - bw) * kk; bh += (th - bh) * kk;
  blob.style.transform = `translate(${bx}px, ${by}px)`; blob.style.width = bw + "px"; blob.style.height = bh + "px";
  const arrived = Math.max(0, 1 - Math.hypot(tx - bx, ty - by, tw - bw) / T.fade);
  blob.style.opacity = `calc(var(--blob-op) * ${(.78 + .22 * arrived).toFixed(3)})`;
  document.body.classList.toggle("speaking", voiceDriving());
  const strain = guarding && !g.snapped ? g.t * g.t : 0;
  blob.style.filter = strain ? `saturate(${1 - .45 * strain}) brightness(${1 + .12 * strain})` : "";

  sl += (pullLen - sl) * kk;
  const len = Math.abs(sl);
  if (strain > .01 && len > 3) {
    const down = sl > 0, tip = Math.max(.12, .5 - .35 * strain);
    const w = bw * (1 - .3 * strain), x = bx + (bw - w) / 2, y = down ? by + bh - 2 : by - len + 2;
    stretch.style.transform = `translate(${x}px, ${y}px)`; stretch.style.width = w + "px"; stretch.style.height = len + "px";
    const a = (1 - tip) / 2 * 100, b = 100 - a;
    stretch.style.clipPath = down ? `polygon(0 0, 100% 0, ${b}% 100%, ${a}% 100%)` : `polygon(${a}% 0, ${b}% 0, 100% 100%, 0 100%)`;
    stretch.style.setProperty("--dir", down ? "180deg" : "0deg");
    stretch.style.opacity = (.16 + .3 * strain).toFixed(3);
  } else stretch.style.opacity = 0;

  if (strain > .02) {
    const d = docRect(words[centreIdx()]), pad = 6;
    dest.style.transform = `translate(${d.x - pad}px, ${d.y - 2}px)`; dest.style.width = d.w + pad * 2 + "px"; dest.style.height = d.h + 4 + "px";
    dest.style.opacity = Math.min(1, .1 + strain).toFixed(3); dest.style.borderStyle = strain > .7 ? "solid" : "dashed";
  } else dest.style.opacity = 0;

  const vis = guarding ? (g.snapped ? 1 : g.t) : 0;
  centre.style.opacity = vis * .7; pill.style.opacity = guarding && g.t > .05 ? 1 : 0;
  if (guarding) { pill.classList.toggle("snap", g.snapped); pill.textContent = g.snapped ? "let go · lift to resume here" : `pull ${Math.round(g.t * 100)}%`; }

  requestAnimationFrame(frame);
}

// ---- Controls ----
$("#play").onclick = togglePlay;
$("#again").onclick = again;
$("#voice").checked = S.voice;
$("#voice").onchange = () => { S.voice = $("#voice").checked; save(); restartVoice(); };
$("#text").addEventListener("click", e => {
  const w = e.target.closest(".w"); if (!w) return;
  if (waiting) { waiting.classList.remove("waiting"); waiting = null; }
  setIdx(+w.dataset.i); acc = 0; ended = false; $("#end").hidden = true; if (!playing) { playing = true; syncPlay(); } restartVoice();
});
addEventListener("keydown", e => {
  if (e.target.closest("input, button, textarea")) return;
  if (e.code === "Space") { e.preventDefault(); togglePlay(); }
});
const showTune = open => { $("#tune").hidden = !open; $("#tuneBtn").setAttribute("aria-expanded", open); };
showTune(S.tuneOpen);
$("#tuneBtn").onclick = () => { S.tuneOpen = $("#tune").hidden; save(); showTune(S.tuneOpen); };
const fmt = { wpm: v => v + " wpm", thr: v => v + "%", pull: v => (+v).toFixed(2), fly: v => (+v).toFixed(2), fade: v => v + " px" };
for (const key of Object.keys(T)) {
  const input = $("#" + key), out = $("#" + key + "V");
  input.value = T[key]; out.textContent = fmt[key](T[key]);
  input.oninput = () => { T[key] = +input.value; out.textContent = fmt[key](T[key]); save();
    if (key === "wpm") audio.playbackRate = Math.min(2, Math.max(.5, T.wpm / 230)); };
}
addEventListener("resize", () => { expectedY = scrollY; });

// Pick up where the reader left off.
let resumeAt = Math.min(words.length - 1, Math.max(0, parseInt(store.get("position", 0)) || 0));
setIdx(resumeAt);
const placeResume = () => { if (resumeAt) { scrollTo(0, Math.max(0, docRect(words[idx]).y - H() * .4)); expectedY = scrollY; } first = true; };
placeResume(); document.fonts?.ready.then(placeResume);
if (S.voice) waitForTap();
requestAnimationFrame(frame);
