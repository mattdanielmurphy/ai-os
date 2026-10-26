// Headless, muted check of a built scroll reel (out/<id>/test.html), with a fake Claude for the Ask sheet.
// Run: scroll/test.sh <id>. Never open reels in the Claude browser pane.
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const id = process.argv[2], dir = path.join(__dirname, 'out', id), shots = path.join(__dirname, 'out', id, 'shots');
fs.mkdirSync(shots, { recursive: true });
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
(async () => {
  const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const b = await chromium.launch({ executablePath: fs.existsSync(mac) ? mac : undefined, headless: true, args: ['--mute-audio', '--autoplay-policy=no-user-gesture-required'] });
  const ctx = await b.newContext({ viewport: { width: 1100, height: 900 } });
  // Fake viewer runtime: sample() streams a canned answer and keeps what it was sent.
  await ctx.addInitScript(() => {
    window.__sent = [];
    const sample = async (input, opts) => {
      window.__sent.push(input);
      await new Promise(r => setTimeout(r, 150));
      const t = 'Think of **∀** as “for all”. Try `∀x (D(x) → B(x))`:\n- one\n- two';
      opts?.onText?.({ text: t, delta: t });
      return { text: t, truncated: false, modelTierApplied: 'default' };
    };
    window.claude = { use: async n => (n === 'sample' ? sample : null) };
  });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await p.goto('file://' + path.join(dir, 'test.html'));
  await p.waitForTimeout(800);
  const info = await p.evaluate(() => ({ words: words.length, blocks: blockStart.length, tries: Object.keys(tries).length, audio: Object.keys(REEL.audio || {}).length, ask: !document.getElementById('askBtn').hidden }));
  console.log(JSON.stringify(info));
  ok(info.words > 100, 'words wrapped');
  ok(info.ask, 'Ask button shown when Claude is available');

  // Voice: check one recorded block loads and plays (muted).
  if (info.audio) {
    const dur = await p.evaluate(async () => { const a = new Audio(REEL.audio[0].src); await new Promise((r, j) => { a.onloadedmetadata = r; a.onerror = j; }); return a.duration; }).catch(e => 'error ' + e);
    ok(typeof dur === 'number' && dur > 0.5, 'first block audio loads (' + dur + ' s)');
  }

  // Start reading (tap), then race ahead silently until the first check pauses it.
  await p.evaluate(() => { document.getElementById('voice').checked = false; T.wpm = 6000; });
  await p.mouse.click(550, 300);
  await p.waitForFunction(() => waiting || null, null, { timeout: 20000 }).catch(() => {});
  const w = await p.evaluate(() => waiting && waiting.dataset.id);
  ok(!!w, 'reading paused at the first check: ' + w);
  await p.evaluate(() => waiting.querySelector('button.opt[data-ok]').click());
  ok(await p.evaluate(() => !!waiting.querySelector('.why') && !waiting.querySelector('.after').hidden), 'check shows why + continue');
  await p.evaluate(() => waiting.querySelector('.after button').click());
  ok(await p.evaluate(() => playing && !waiting), 'continue resumes reading');

  // Ask sheet.
  await p.evaluate(() => { T.wpm = 300; });
  await p.click('#askBtn');
  ok(await p.evaluate(() => !document.getElementById('ask').hidden && !playing), 'Ask opens and pauses');
  await p.fill('#ask textarea', 'what does the upside down A mean?');
  await p.keyboard.press('Enter');
  await p.waitForFunction(() => document.querySelector('#ask .aa b'), null, { timeout: 5000 }).catch(() => {});
  const sent = await p.evaluate(() => window.__sent[0]);
  ok(Array.isArray(sent) && /ACADEMIC INTEGRITY/.test(sent[0].content) && /They paused at this part/.test(sent[1].content), 'prompt carries the integrity rules and the current sentence');
  ok(await p.evaluate(() => !!document.querySelector('#ask .aa code') && !!document.querySelector('#ask .aa li')), 'answer rendered with formulas and list');
  await p.screenshot({ path: path.join(shots, 'desk-ask.png') });
  await p.click('#ask .top button');
  ok(await p.evaluate(() => document.getElementById('ask').hidden && playing), 'closing resumes reading');

  // Phone, light and dark.
  for (const scheme of ['light', 'dark']) {
    const q = await b.newPage({ viewport: { width: 390, height: 844 }, colorScheme: scheme, isMobile: true, hasTouch: true });
    await q.goto('file://' + path.join(dir, 'test.html'));
    await q.waitForTimeout(600);
    const over = await q.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(over <= 0, scheme + ' phone: no sideways scroll (' + over + ')');
    await q.evaluate(() => document.querySelector('.try').scrollIntoView({ block: 'center' }));
    await q.screenshot({ path: path.join(shots, 'phone-' + scheme + '.png') });
    await q.close();
  }
  ok(errs.length === 0, 'no page errors ' + errs.join(' | '));
  await b.close();
})().catch(e => { console.log('FAIL ' + e); process.exitCode = 1; });
