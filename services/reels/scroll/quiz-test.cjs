// Headless, muted check of quiz mode in a built scroll reel: scoring, a missed check coming back at a later
// slot with reshuffled options, and the end review. Run: NODE_PATH=<dir with playwright-core> node quiz-test.cjs <id>
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path');
const id = process.argv[2], dir = path.join(__dirname, 'out', id);
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
(async () => {
  const mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const b = await chromium.launch({ executablePath: fs.existsSync(mac) ? mac : undefined, headless: true, args: ['--mute-audio'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + path.join(dir, 'test.html'));
  await p.waitForTimeout(500);
  await p.evaluate(() => { document.getElementById('voice').checked = false; T.wpm = 20000; });
  await p.mouse.click(500, 300);
  // Walk the whole reel: miss the first normal check, get every other one right, note what each gate was.
  const log = []; let missedId = null;
  for (let n = 0; n < 80; n++) {
    const r = await p.waitForFunction(() => (waiting && 'w') || (ended && 'e') || null, null, { timeout: 30000 }).catch(() => null);
    if (!r) { log.push('timeout'); break; }
    const st = await p.evaluate(() => ended ? { end: true } : { id: waiting.dataset.id, of: waiting.dataset.of || null, back: waiting.classList.contains('back') });
    if (st.end) break;
    log.push(st.of ? 'redo:' + st.of : st.id);
    const wrong = !missedId && !st.of;
    if (wrong) missedId = st.id;
    await p.evaluate(w => { const o = waiting.querySelector(w ? 'button.opt:not([data-ok])' : 'button.opt[data-ok]'); o.click(); }, wrong);
    await p.evaluate(() => waiting.querySelector('.after button').click());
  }
  console.log(log.join(' > '));
  ok(log.includes('redo:' + missedId), 'missed check ' + missedId + ' came back at a later slot');
  ok(log.filter(x => x.startsWith('redo:')).length === 1, 'only the missed check comes back, once (passed comeback clears it)');
  const s = await p.evaluate(() => ({ score: document.getElementById('score').textContent, end: !document.getElementById('end').hidden, tally: document.querySelector('#review .tally')?.textContent, left: document.querySelectorAll('#review .try').length, total: Object.keys(checkById).length }));
  console.log(JSON.stringify(s));
  ok(s.end, 'end panel shown');
  ok(new RegExp('^' + (s.total - 1) + ' / ' + s.total).test(s.score), 'score counts first picks only: ' + s.score);
  ok(s.left === 0, 'nothing left to redo after passing the comeback');
  // Second pass: a fresh page that misses two checks and never gets a comeback right shows them in the end review.
  const q = await b.newPage(); await q.goto('file://' + path.join(dir, 'test.html'));
  await q.evaluate(() => { localStorage.clear(); document.getElementById('voice').checked = false; T.wpm = 20000; });
  await q.reload(); await q.waitForTimeout(300);
  await q.evaluate(() => { document.getElementById('voice').checked = false; T.wpm = 20000; });
  await q.mouse.click(500, 300);
  for (let n = 0; n < 80; n++) {
    const r = await q.waitForFunction(() => (waiting && 'w') || (ended && 'e') || null, null, { timeout: 30000 }).catch(() => null);
    if (!r || await q.evaluate(() => ended)) break;
    await q.evaluate(() => { const o = waiting.querySelector('button.opt:not([data-ok])'); o.click(); waiting.querySelector('.after button').click(); });
  }
  const s2 = await q.evaluate(() => ({ left: document.querySelectorAll('#review .try').length, missed: missed.length }));
  ok(s2.left === s2.missed && s2.left > 0, 'all-wrong run lists every missed check in the end review (' + s2.left + ')');
  await q.evaluate(() => document.querySelector('#review .try button.opt[data-ok]').click());
  ok(await q.evaluate(() => missed.length) === s2.missed - 1, 'getting one right in the end review clears it');
  for (const scheme of ['light', 'dark']) {
    const m = await b.newPage({ viewport: { width: 390, height: 844 }, colorScheme: scheme, isMobile: true, hasTouch: true });
    await m.goto('file://' + path.join(dir, 'test.html')); await m.waitForTimeout(300);
    await m.evaluate(() => { finish(); document.getElementById('end').scrollIntoView(); });
    const over = await m.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    ok(over <= 0, scheme + ' phone: no sideways scroll on the end review (' + over + ')');
    await m.screenshot({ path: path.join(dir, 'shots', 'end-' + scheme + '.png') });
  }
  ok(errs.length === 0, 'no page errors ' + errs.join(' | '));
  await b.close();
})().catch(e => { console.log('FAIL ' + e); process.exitCode = 1; });
