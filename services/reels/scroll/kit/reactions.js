// Reactions for the scroll-to-read page. Self-contained: reads the word spans index.html builds
// (w._block, w._b), so any document rendered by the page is reactable with no extra work.
// Gestures: long-press = pick a sentence, long-press again = widen; React mode = taps pick; margin dots (desktop) = paragraph.
(() => {
  const KEY = window.REEL ? "reel:" + REEL.id + ":reactions" : "scroll-read-reactions";
  const REACT = { love: "❤️", agree: "👍", no: "✕", confused: "❓" };
  const LEVELS = ["sentence", "paragraph", "all"];
  const text = document.getElementById("text");

  // Sentence ids per word, restarting in each block.
  const sentOf = [];
  blockStart.forEach((start, b) => {
    const end = b + 1 < blockStart.length ? blockStart[b + 1] : words.length;
    let s = 0;
    for (let i = start; i < end; i++) { words[i]._s = s; if (/[.!?]["'”’)]*$/.test(words[i].textContent)) s++; }
  });
  const wordsOf = (b, s) => words.filter(w => w._b === b && (s == null || w._s === s));
  const lastWord = list => list[list.length - 1];

  let store = {};            // key -> { b, s, level, reaction, comment }
  try { store = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch {}
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch {} };
  const keyOf = t => t.level === "all" ? "all" : t.level === "paragraph" ? `p${t.b}` : `s${t.b}.${t.s}`;
  const quoteOf = t => t.level === "all" ? "Whole report"
    : wordsOf(t.b, t.level === "sentence" ? t.s : null).map(w => w.textContent).join(" ");

  // ---- UI ----
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag); Object.assign(e, attrs); e.append(...kids); return e; };
  const modeBtn = el("button", { id: "rmode", textContent: "React", title: "React mode: taps pick a sentence instead of jumping" });
  modeBtn.setAttribute("aria-pressed", "false");
  const reviewBtn = el("button", { id: "rreview", textContent: "Review · 0" });
  document.body.append(el("div", { className: "rtop" }, [modeBtn, reviewBtn]));
  const hint = el("p", { className: "rhint", innerHTML: "React mode: tap a sentence to pick it.<br>Scrolling still works." });
  document.body.append(hint);

  const bar = el("div", { id: "rbar", hidden: true });
  const quote = el("span", { className: "quote" });
  const closeB = el("button", { className: "x", textContent: "Done", title: "Close" });
  const askB = el("button", { className: "askthis", textContent: "Ask", title: "Ask Claude about this", hidden: !window.reelAsk });
  askB.onclick = () => { commitComment(); window.reelAsk?.open({ quote: quoteOf(target) }); };
  addEventListener("reel-ask-ready", () => { askB.hidden = false; });
  const rowTop = el("div", { className: "row" }, [quote, askB, closeB]);
  const lv = el("div", { className: "row lv" });
  const lvBtns = LEVELS.map(l => { const b = el("button", { textContent: l === "all" ? "Whole report" : l[0].toUpperCase() + l.slice(1) }); b.onclick = () => pick({ ...target, level: l }); lv.append(b); return b; });
  const rr = el("div", { className: "row" });
  const rBtns = Object.entries(REACT).map(([k, e]) => { const b = el("button", { textContent: e, title: k }); b.onclick = () => toggleReact(k); rr.append(b); return [k, b]; });
  const ta = el("textarea", { placeholder: "Comment — type or dictate", rows: 2 });
  bar.append(rowTop, lv, rr, ta);
  document.body.append(bar);

  const sheet = el("div", { id: "rsheet", hidden: true });
  document.body.append(sheet);

  let target = null, reacting = false, wasPlaying = false;

  function clearPick() { document.querySelectorAll(".w.rpick").forEach(w => w.classList.remove("rpick")); }
  function pick(t) {
    commitComment();
    target = { b: t.b, s: t.s ?? 0, level: t.level };
    clearPick();
    if (target.level !== "all") wordsOf(target.b, target.level === "sentence" ? target.s : null).forEach(w => w.classList.add("rpick"));
    renderBar();
    bar.hidden = false;
  }
  function renderBar() {
    const rec = store[keyOf(target)] || {};
    quote.textContent = quoteOf(target);
    lvBtns.forEach((b, i) => b.setAttribute("aria-pressed", String(LEVELS[i] === target.level)));
    rBtns.forEach(([k, b]) => b.setAttribute("aria-pressed", String(rec.reaction === k)));
    ta.value = rec.comment || "";
  }
  function record() { const k = keyOf(target); return store[k] || (store[k] = { b: target.b, s: target.level === "sentence" ? target.s : null, level: target.level }); }
  function toggleReact(k) { const r = record(); r.reaction = r.reaction === k ? undefined : k; tidy(); renderBar(); }
  function commitComment() {
    if (!target) return;
    const v = ta.value.trim(), k = keyOf(target);
    if (v || store[k]) { record().comment = v || undefined; tidy(); }
  }
  function tidy() {   // drop empty records, save, redraw marks
    for (const k in store) if (!store[k].reaction && !store[k].comment) delete store[k];
    persist(); drawMarks();
  }
  function drawMarks() {
    document.querySelectorAll(".rbadge").forEach(n => n.remove());
    document.querySelectorAll(".w.rmark").forEach(w => w.classList.remove("rmark"));
    document.querySelectorAll(".rdot.on").forEach(d => d.classList.remove("on"));
    let n = 0;
    for (const k in store) {
      const r = store[k]; n++;
      if (r.level === "all") continue;
      const list = wordsOf(r.b, r.level === "sentence" ? r.s : null);
      list.forEach(w => w.classList.add("rmark"));
      const badge = el("span", { className: "rbadge", textContent: (REACT[r.reaction] || "") + (r.comment ? "💬" : "") });
      lastWord(list).after(badge);
      if (r.level === "paragraph") blockDots[r.b]?.classList.add("on");
    }
    reviewBtn.textContent = `Review · ${n}`;
  }

  // ---- Closing: dictation pauses the reel so the page doesn't run off while he talks ----
  closeB.onclick = () => { commitComment(); bar.hidden = true; target = null; clearPick(); };
  ta.addEventListener("keydown", e => e.stopPropagation());       // Space must type, not pause
  ta.addEventListener("focus", () => { wasPlaying = playing; if (playing) togglePlay(); });
  ta.addEventListener("blur", () => { commitComment(); if (wasPlaying && !playing) togglePlay(); wasPlaying = false; });

  // ---- Gesture A: long-press ----
  let press = null, suppressClick = false;
  text.addEventListener("pointerdown", e => {
    const w = e.target.closest(".w"); if (!w || e.button) return;
    press = { x: e.clientX, y: e.clientY, w, timer: setTimeout(() => {
      press = null; suppressClick = true; navigator.vibrate?.(12);
      const same = target && target.b === w._b && target.level === "sentence" && target.s === w._s;
      const sameP = target && target.b === w._b && target.level === "paragraph";
      pick(!target || (!same && !sameP) ? { b: w._b, s: w._s, level: "sentence" }
        : same ? { b: w._b, level: "paragraph" } : { b: w._b, level: "all" });
    }, 450) };
  });
  const cancel = () => { if (press) { clearTimeout(press.timer); press = null; } };
  text.addEventListener("pointermove", e => { if (press && Math.hypot(e.clientX - press.x, e.clientY - press.y) > 8) cancel(); });
  addEventListener("pointerup", cancel); addEventListener("pointercancel", cancel); addEventListener("scroll", cancel, { passive: true });
  text.addEventListener("contextmenu", e => { if (e.target.closest(".w")) e.preventDefault(); });

  // Capture phase: eat the click after a long-press, and in React mode turn taps into picks (no jump).
  text.addEventListener("click", e => {
    const w = e.target.closest(".w");
    if (suppressClick) { suppressClick = false; e.stopImmediatePropagation(); e.preventDefault(); return; }
    if (reacting && w) { e.stopImmediatePropagation(); e.preventDefault(); pick({ b: w._b, s: w._s, level: "sentence" }); }
  }, true);

  // ---- Gesture B: React mode ----
  modeBtn.onclick = () => { reacting = !reacting; modeBtn.setAttribute("aria-pressed", String(reacting)); document.body.classList.toggle("reacting", reacting); };

  // ---- Gesture C: margin dots (CSS shows them only on a fine pointer, wide screen) ----
  const blockDots = [];
  document.querySelectorAll("[data-read]").forEach((blk, b) => {
    if (blk.tagName === "SPAN") return;
    const d = el("button", { className: "rdot", title: "React to this paragraph" });
    d.setAttribute("aria-label", "React to this paragraph");
    d.onclick = e => { e.stopPropagation(); pick({ b, level: "paragraph" }); };
    blk.prepend(d); blockDots[b] = d;
  });

  // ---- Review & send ----
  const toMarkdown = () => {
    const items = Object.values(store).sort((a, b) => (a.level === "all" ? -1 : b.level === "all" ? 1 : a.b - b.b || (a.s ?? -1) - (b.s ?? -1)));
    if (!items.length) return "";
    return "# Reactions on “" + (document.title || "report") + "”\n\n" + items.map(r => {
      const q = quoteOf(r), tag = [REACT[r.reaction] && `${REACT[r.reaction]} ${r.reaction}`, r.comment && `comment: ${r.comment}`].filter(Boolean).join(" · ");
      return `- [${r.level}] ${r.level === "all" ? "" : "“" + q + "” "}— ${tag}`;
    }).join("\n") + "\n";
  };
  function openSheet() {
    commitComment();
    sheet.replaceChildren();
    const in_ = el("div", { className: "in" }, [el("h3", { textContent: "Your reactions" })]);
    const keys = Object.keys(store);
    if (!keys.length) in_.append(el("p", { className: "empty", textContent: "Nothing yet. Hold a sentence, or turn on React." }));
    keys.forEach(k => { const r = store[k];
      const rm = el("button", { textContent: "Remove" }); rm.onclick = () => { delete store[k]; tidy(); openSheet(); };
      in_.append(el("div", { className: "item" }, [
        el("div", { className: "meta" }, [el("span", { textContent: `${r.level} ${REACT[r.reaction] || ""}` }), rm]),
        ...(r.level === "all" ? [] : [el("q", { textContent: quoteOf(r) })]),
        ...(r.comment ? [el("div", { textContent: r.comment })] : [])]));
    });
    const copy = el("button", { textContent: "Copy all" });
    copy.onclick = async () => { const md = toMarkdown(); try { await navigator.clipboard.writeText(md); copy.textContent = "Copied ✓"; } catch { ta2.hidden = false; ta2.value = md; ta2.select(); copy.textContent = "Select and copy"; } };
    const back = el("button", { textContent: "Back to reading" }); back.onclick = () => { sheet.hidden = true; };
    const ta2 = el("textarea", { hidden: true, rows: 8 });
    ta2.style.cssText = "width:100%;font:12px var(--mono);background:var(--surface);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:8px";
    in_.append(ta2, el("div", { className: "acts" }, [copy, back]));
    sheet.append(in_); sheet.hidden = false;
  }
  reviewBtn.onclick = openSheet;
  addEventListener("keydown", e => { if (e.key === "Escape") { if (!sheet.hidden) sheet.hidden = true; else if (!bar.hidden) closeB.onclick(); } });

  drawMarks();
})();
