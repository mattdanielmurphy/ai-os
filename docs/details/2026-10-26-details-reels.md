# Details files as scroll-to-read reels

## 01:40 One command publishes a details file as a reel

Matt asked for one script agents call with their details file that publishes it as a scroll-to-read reel on mattmurphy.ca at /claude/<project>/<thread>, public but hidden from search, and returns the link. Every reply's Details line should then carry that reel link. He then added that the reels must pick up any change he makes to the scroll-to-read player, old reels included.

---

### The command

Agents run `pages reel <details.md> --project <project> --thread <thread>`. It prints one line, the reel's link, for example https://mattmurphy.ca/claude/everything/details-reels. The project defaults to "everything" and the thread defaults to the file name without its date, so `pages reel ~/projects/ai-os/docs/details/2026-10-26-details-reels.md` is enough in the Everything project. Running it again updates the same reel.

It lives in the pages tool (`~/projects/pages/reel.ts`), next to `pages md`, and reuses its website publishing: the reel is written into the mattmurphy.ca repo under `public/claude/<project>/<thread>/`, committed on its own and pushed, and Vercel puts it live in about a minute.

---

### Player updates reach every reel

A reel page holds only its text. In its head it loads one script, `player/player.js`, straight from the deployed scroll-read page on matt-pages.vercel.app. That loader pulls in the look, the controls, the voice and the reactions. So when Matt changes scroll-read and runs `pages deploy`, every reel, old ones included, gets the new player on its next load. Vercel serves these files with no long cache, so there is no stale copy.

To make that possible I split scroll-read into its text (`site/scroll-read/index.html`) and a shared player folder (`site/scroll-read/player/`: `player.js`, `reel.js`, `player.css`, `reactions.js`, `reactions.css`). The scroll-read page itself now uses the same loader, so it is the reference reel.

Side fix: the deployed scroll-read page was missing its reactions script (a 404), because Vite drops plain script files it doesn't bundle. The build now copies such files as they are, so reactions work on the public page again.

---

### Voice on reels

The read-aloud voice runs on matt-pages.vercel.app. For a reel on mattmurphy.ca, the player asks the voice server by the reel's address, and the server reads the text from that live page itself. It only accepts addresses under mattmurphy.ca/claude/, so it can only ever speak text that is really published there; it is not an open text-to-speech service. Voice is cached as before, so each paragraph costs one Speechify call ever.

---

### Secrets and privacy

Before publishing, the script scans the file for anything that looks like a secret: API keys (OpenAI, Anthropic, Google, GitHub, AWS, Slack, Stripe), bearer tokens, JWTs, private keys, passwords inside URLs, and lines like `SOMETHING_TOKEN = value`. If it finds one, it refuses to publish and lists the line numbers and kinds, never the values. It also hides email addresses and phone numbers in the published copy.

Privacy risk: details files describe Matt's life and work, and reels are public to anyone with the link. The link is unguessable only in the sense that it isn't listed anywhere; the address pattern /claude/<project>/<thread> is readable and thread names are guessable. Search engines are kept out with a noindex tag and header. Agents should keep private life details (health, money, other people's personal matters) out of details files, or skip the reel for that reply.

---

### The rule now asks for it

The details-file rule in `.rules/core_safety.md` (compiled into every agent's rules) and Matt's `~/.claude/CLAUDE.md` now say: after appending to the details file, run `pages reel` and add `· [reel](<link>#section)` to the Details line, between the file link and the "on Mac" link. Code sessions use `--project code`. If a reply's details hold private life details, the agent skips the reel and says so.

---

### Tested

I checked the scroll-read page locally and on its public link, and this reel on mattmurphy.ca, in a muted headless Chrome: words wrap, controls and reactions appear, a #section link starts reading at that section, and the voice plays on both sites. A test file with a fake GitHub token was refused with its line number and nothing was published. The noindex header is on.

---

### What I rejected

- Copying the player into each reel: simplest, but Matt explicitly wants player updates to reach old reels.
- Hosting reels on matt-pages.vercel.app: the voice would be same-site, but Matt asked for mattmurphy.ca addresses.
- Sending the text to the voice server from the browser: that would turn it into an open text-to-speech service anyone could spend credits on.

---

### Untested or risky

- Cloud sessions without Matt's Mac can't run `pages reel` (it needs the mattmurphy.ca repo and push access). They skip the reel link and keep the plain Details link.
- Deploying scroll-read also redeployed every page from the working tree, including uncommitted changes to tv-box from Oct 24 (only on its unlisted matt-pages link, not mattmurphy.ca/tv-box).

---

### How to undo

Remove a reel by deleting `public/claude/<project>/<thread>/` in `~/projects/mattmurphy.ca` and pushing. The rule change is in ai-os `.rules/core_safety.md` ("Every reply has a details file behind it"); revert that commit to drop the reel link from replies.
