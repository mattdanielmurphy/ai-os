// Ask as you go: questions about the spot you're reading, answered by Claude inside the page.
// Backend: the claude.ai Artifact "sample" capability (the viewer's own Claude; the first question asks to allow it).
// Anywhere else the Ask button stays hidden. REEL.ask = { mode: "school" | "general", audience, rules } tunes the tutor.
(() => {
  const CFG = REEL.ask || {};
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag); Object.assign(e, attrs); e.append(...kids); return e; };

  // The sentence the highlight is on, from the player's word spans.
  function currentSentence() {
    const w = words[idx]; if (!w) return "";
    const list = words.filter(x => x._b === w._b), k = list.indexOf(w);
    let a = k, b = k;
    while (a > 0 && !/[.!?]["'”’)]*$/.test(list[a - 1].textContent)) a--;
    while (b < list.length - 1 && !/[.!?]["'”’)]*$/.test(list[b].textContent)) b++;
    return list.slice(a, b + 1).map(x => x.textContent).join(" ");
  }
  // What's on the page, so answers match the reel's examples and notation (formulas included).
  function pageText() {
    const main = document.getElementById("text").cloneNode(true);
    main.querySelectorAll(".after, .why, .rbadge, .rdot, .hint, .end").forEach(n => n.remove());
    return main.innerText.replace(/\n{3,}/g, "\n\n").slice(0, 24000);
  }

  const SCHOOL = `ACADEMIC INTEGRITY (strict, never broken, even if asked nicely or told it's fine):
- You may explain concepts, define symbols, walk through the reel's own examples, invent NEW examples of your own, and give hints.
- Never solve, symbolize, translate, prove or check anything that comes from a textbook practice exercise, an assignment, a quiz or an exam, and never write or fix work the student will hand in. If a question looks like one of those (it names an exercise or problem set, or it hands you a sentence or argument to symbolize or prove), say kindly in one line that you can't do that one for them, then explain the idea it tests using a different example you make up, and end with one short hint question that helps them do it themselves.
- If the student gives a sentence of their own to symbolize, coach rather than answer: break it into stepping stones and ask them to fill in the last step.`;

  const RULES = () => `You are a patient tutor built into an explainer page called "${REEL.title}".
${CFG.audience || "The reader is learning this for the first time."}
${CFG.mode === "school" ? SCHOOL : ""}
${CFG.rules || ""}
STYLE: plain everyday words; short (about 120 words unless they ask for more); one idea at a time; warm and encouraging, never condescending. Define every symbol the first time you use it. Use the same notation as the page. Light Markdown only: **bold**, short lists, and \`backticks\` around formulas. No headings.

THE PAGE THEY ARE READING:
<<<
${pageText()}
>>>`;

  // ---- UI ----
  const sheet = el("div", { id: "ask", hidden: true });
  sheet.setAttribute("role", "dialog"); sheet.setAttribute("aria-label", "Ask about this part");
  const about = el("div", { className: "about" });
  const closeB = el("button", { textContent: "Back to reading", title: "Close (Esc)" });
  const CHIPS = CFG.chips || ["Explain it more simply", "Give me another example", "What do the symbols mean?", "I'm lost: start from the basics"];
  const chips = el("div", { className: "row chips" }, CHIPS.map(c => { const b = el("button", { textContent: c }); b.onclick = () => send(c); return b; }));
  const thread = el("div", { className: "thread" });
  const past = el("details", { className: "past", hidden: true }, [el("summary", { textContent: "Earlier questions" })]);
  const ta = el("textarea", { placeholder: "Type or dictate a question…", rows: 2 });
  const sendB = el("button", { className: "send", textContent: "Ask ↵" });
  const stopB = el("button", { textContent: "Stop", hidden: true });
  const note = el("span", { className: "note" });
  const keys = el("span", { className: "keys", innerHTML: matchMedia("(hover: hover)").matches ? "<kbd>Enter</kbd> ask · <kbd>Shift</kbd>+<kbd>Enter</kbd> new line · <kbd>Esc</kbd> close" : "" });
  sheet.append(
    el("div", { className: "top" }, [el("div", { className: "row" }, [el("span", { className: "ttl", textContent: "Ask about this part" }), closeB]), about, chips]),
    el("div", { style: "overflow:auto;display:grid;align-content:start" }, [past, thread]),
    el("div", { className: "bottom" }, [ta, el("div", { className: "row" }, [note, keys, stopB, sendB])]));
  document.body.append(sheet);

  const btn = el("button", { id: "askBtn", textContent: "Ask", title: "Ask a question about this part (A)", hidden: true });
  document.querySelector(".ctl.l")?.append(btn);

  // ---- State: one conversation per open; finished ones are kept in this browser to look back on. ----
  let sample = null, turns = [], quote = "", ctl = null, wasPlaying = false, busy = false;
  const history = store.get("asked", []);
  function renderPast() {
    past.querySelectorAll("button").forEach(b => b.remove());
    past.hidden = !history.length;
    history.slice(-12).reverse().forEach(h => {
      const b = el("button", { textContent: h.q.length > 80 ? h.q.slice(0, 78) + "…" : h.q, title: "Show this answer again" });
      b.onclick = () => { thread.replaceChildren(el("div", { className: "qq", textContent: h.q }), answerEl(h.a)); about.textContent = h.quote || ""; };
      past.append(b);
    });
  }

  // Tiny Markdown: escape first, then **bold**, `code`, lists, paragraphs.
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  function md(src) {
    const inline = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>").replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>");
    const out = []; let list = null;
    for (const raw of src.split("\n")) {
      const line = raw.trimEnd(), m = line.match(/^\s*(?:[-*•]|(\d+)[.)])\s+(.*)$/);
      if (m) { const t = m[1] ? "ol" : "ul"; if (!list || list.t !== t) { if (list) out.push(`</${list.t}>`); out.push(`<${t}>`); list = { t }; } out.push(`<li>${inline(m[2])}</li>`); continue; }
      if (list) { out.push(`</${list.t}>`); list = null; }
      if (/^```/.test(line)) continue;
      if (line.trim()) out.push(`<p>${inline(line)}</p>`); else out.push("");
    }
    if (list) out.push(`</${list.t}>`);
    return out.join("").replace(/<\/p><p>/g, "</p><p>");
  }
  const answerEl = text => { const d = el("div", { className: "aa" }); d.innerHTML = md(text); return d; };

  function open({ quote: q } = {}) {
    if (!sample) return;
    quote = (q || currentSentence()).trim();
    about.textContent = quote ? "“" + quote + "”" : "This page";
    if (turns.length === 0) thread.replaceChildren();
    renderPast();
    wasPlaying = playing; if (playing) togglePlay();
    document.getElementById("rbar")?.setAttribute("hidden", "");
    sheet.hidden = false; note.textContent = "";
    setTimeout(() => ta.focus({ preventScroll: true }), 30);
  }
  function close() {
    if (busy) ctl?.abort();
    sheet.hidden = true; turns = []; thread.replaceChildren();
    if (wasPlaying && !playing) togglePlay();
    wasPlaying = false;
  }

  const COPY = {
    not_granted: "Asking is turned off for this page. You can allow it from the page's Permissions menu.",
    sampling_disabled: "Claude isn't available on this account right now.",
    rate_limited: "Too many questions at once, or you've hit a usage limit. Try again in a bit.",
    session_expired: "Please sign in to Claude again, then ask.",
    refused: "Claude couldn't answer that one. Try asking it another way.",
    empty_completion: "No answer came back. Try asking it a little differently.",
    prompt_too_large: "That was too long to send. Try a shorter question.",
  };
  async function send(text) {
    text = (text ?? ta.value).trim();
    if (!text || busy || !sample) return;
    ta.value = "";
    const first = turns.length === 0;
    const content = (first ? `They paused at this part: "${quote}"\n\nTheir question: ` : "") + text;
    turns.push({ role: "user", content });
    thread.append(el("div", { className: "qq", textContent: text }));
    const a = el("div", { className: "aa thinking", textContent: "Thinking…" });
    thread.append(a); a.scrollIntoView({ block: "end" });
    busy = true; sendB.disabled = true; stopB.hidden = false; note.textContent = "";
    ctl = new AbortController();
    try {
      const { text: answer, truncated } = await sample([{ role: "user", content: RULES() }, ...turns], {
        cache: false, signal: ctl.signal,
        onText: ({ text: t }) => { a.className = "aa"; a.innerHTML = md(t); thread.parentElement.scrollTop = thread.parentElement.scrollHeight; },
      });
      turns.push({ role: "assistant", content: answer });
      history.push({ q: text, a: answer, quote, at: Date.now() }); store.set("asked", history.slice(-60));
      if (truncated) note.textContent = "The answer was cut short. Ask for the rest.";
    } catch (e) {
      turns.pop();
      if (e?.code === "refused" || !e?.text) a.remove(); else { a.className = "aa"; a.innerHTML = md(e.text); }
      if (e?.code !== "cancelled") note.textContent = COPY[e?.code] || "Something went wrong reaching Claude. Try again.";
      if (["not_granted", "sampling_disabled", "not_declared", "capability_disabled", "capability_removed"].includes(e?.code)) { btn.hidden = true; }
    } finally {
      busy = false; sendB.disabled = false; stopB.hidden = true; ctl = null;
    }
  }

  btn.onclick = () => open();
  closeB.onclick = close;
  sendB.onclick = () => send();
  stopB.onclick = () => ctl?.abort();
  ta.addEventListener("keydown", e => { e.stopPropagation(); if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } if (e.key === "Escape") close(); });
  addEventListener("keydown", e => {
    if (e.target.closest("input, textarea, button")) return;
    if (e.key === "Escape" && !sheet.hidden) close();
    else if ((e.key === "a" || e.key === "A" || e.key === "?") && sheet.hidden && sample && !e.metaKey && !e.ctrlKey) { e.preventDefault(); open(); }
  });

  // Light up only where Claude can answer.
  (async () => {
    try { sample = window.claude ? await window.claude.use("sample") : null; } catch { sample = null; }
    if (!sample) return;
    btn.hidden = false; document.body.classList.add("can-ask");
    window.reelAsk = { open };
    document.querySelectorAll(".hint .askhint").forEach(n => n.hidden = false);
    dispatchEvent(new Event("reel-ask-ready"));
  })();
})();
