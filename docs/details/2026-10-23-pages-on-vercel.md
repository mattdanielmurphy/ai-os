# Pages on Vercel (2026-10-23)

## 22:58 Pages tool built and made the default

Ask (via coordinator, replacing the "Vite instead of HTML artifacts" idea): every page or tool agents make becomes a Vercel deploy with live reload locally, public by default at an unguessable UUID URL, with an "Add to my website" button that publishes to mattmurphy.ca the way /tv-box was done. Make it the global default.

---

### One project holds every page

New private repo `~/projects/pages` (github.com/mattdanielmurphy/pages). Each page is `site/<name>/` (a Vite root) with `page.json` holding its UUID and title. Rejected: one Vercel project per page (slow, clutters his Vercel dashboard); keeping pages inside ai-os (it's not a website and ai-os is busy).

---

### Public links are unguessable

One Vercel project `matt-pages`; `pages deploy` builds every page into `/<uuid>/` using the Build Output API and runs `vercel deploy --prebuilt --prod`. Production alias `matt-pages.vercel.app` is public (deployment protection only covers preview URLs). Root and `/<name>/` are 404; every response has `X-Robots-Tag: noindex`; `robots.txt` disallows all; pages get a noindex meta. Tested with curl: both pages 200, root 404, no-slash path 308s to the slash path. Risk: anyone with a link can open it, so no secrets in pages.

---

### Live reload at pages.test

One Vite dev server for all pages on 127.0.0.1:5199, puma-dev `pages.test`, kept alive by launchd `ca.mattmurphy.pages-dev`. Tested headless: editing a page reloaded it through pages.test within 2.5 s. http://pages.test/ lists pages.

---

### Add to my website button

Dev-only toolbar (system colours, no palette colours invented): Copy public link, Deploy, Add to my website, ×. Publish rebuilds the page with base `/<slug>/`, copies it to `mattmurphy.ca/public/<slug>/`, adds the `/slug` rewrite to `vercel.json` (tv-box pattern), commits only those paths and pushes `main`. Refuses a slug that already exists and isn't this page. Tested: republishing tv-box was a byte-identical no-op; a full commit+push ran against a throwaway clone of the site, not the live site. Not tested: clicking the button on the live site itself (needs a real page Matt wants published). The button only exists locally, not on the public Vercel copy (that would need auth on a public page).

---

### Made it the default

Rule "Web Pages Live on Vercel, Not Artifacts" in `.rules/core_safety.md` (compiled), a line in `~/.claude/CLAUDE.md`, memory `pages-on-vercel`, reels and ui-mixer READMEs now publish via `pages`. Exception kept: pages needing Artifact runtime features (shared db, viewer identity) stay Artifacts.

Undo: `launchctl bootout gui/$(id -u)/ca.mattmurphy.pages-dev`, revert the rule commit, delete the `matt-pages` Vercel project.
