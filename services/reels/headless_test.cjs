const { chromium } = require('playwright-core');
// Headless, muted check of a built reel: loads it, presses Play, prints the mix (music gain, voice time) each second.
// Run via test.sh, never in the Claude browser pane (opening a reel there hung two sessions, 2026-10-23).
const url = 'file://' + process.argv[2] + '?mute';
(async () => {
  const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true,
    args: ['--mute-audio', '--autoplay-policy=no-user-gesture-required', '--disable-extensions', '--no-first-run'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  const t0 = Date.now(); await p.goto(url, { timeout: 30000 }); console.log('loaded ms', Date.now() - t0);
  await p.waitForTimeout(500);
  const btn = await p.$('#start'); console.log('start button', !!btn);
  await p.evaluate(() => document.getElementById('play').click());
  for (let k = 0; k < (+process.argv[3] || 20); k++) { await p.waitForTimeout(1000); console.log(k + 1, JSON.stringify(await p.evaluate(() => window.reelMix && window.reelMix()))); }
  // flash check: on a new slide, the last part must stay hidden for the first frames (it reveals later)
  console.log('flash', JSON.stringify(await p.evaluate(() => new Promise(done => {
    document.getElementById('next').click();
    const last = [...document.querySelectorAll('#slide .rv')].pop(), seen = [];
    const t0 = performance.now();
    (function f() { seen.push(+getComputedStyle(last).opacity); performance.now() - t0 < 300 ? requestAnimationFrame(f) : done({ maxOpacity: Math.max(...seen), frames: seen.length }); })();
  }))));
  const v = await p.$('#voice');
  if (v) { const names = []; for (let k = 0; k < 3; k++) { await v.click(); names.push(await v.textContent()); } console.log('voices', JSON.stringify(names)); }
  console.log('fits', JSON.stringify(await p.evaluate(() => ({ page: document.documentElement.scrollHeight, viewport: innerHeight }))));
  console.log('errors', JSON.stringify(errs));
  await Promise.race([b.close(), new Promise(r => setTimeout(r, 3000))]); // close can stall; never let it hold the run
  process.exit(0);
})().catch(e => { console.log('FAIL', e.message); process.exit(1); });
