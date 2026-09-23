# query_aios Recovery and AI-OS Controls

- Corrected `--recover`: it previously let an empty prompt bypass validation, generated a new session, and contacted Perplexity. Queries now write atomic pending/completed state beside requested outputs; recovery verifies the output SHA-256 and prints only a completed saved result. It refuses to dispatch a second query.
- Updated the planner skill to keep waiting on the original CLI process and use `--recover` only for completed saved output.
- Added fixed-provider `/api/companion/show` and `/api/companion/hide` routes to the companion server. Show opens a decorated, centered 1120x780 Perplexity or Gemini window; Gemini remains lazily created. Hide preserves both windows and the app process.
- Replaced the Hammerspoon-branded menu-bar icon with a gear and added AI-OS Controls actions for Open Perplexity, Open Gemini, and Hide Companion. Existing module and Hammerspoon actions remain available. On initial API failure, Hammerspoon kickstarts `aios-server` and retries once.
- Recorded the separate Bartender replacement/custom expandable menu-bar idea in `PROJECT_BOARD.md`.
- Validation: `node --check scripts/query_aios.js`, `luac -p modules/menu_bar.lua`, and `cargo check -p query-aios-companion` passed. The Rust check reports two existing `objc` macro `cargo-clippy` cfg warnings. Release build and live reload are pending.
