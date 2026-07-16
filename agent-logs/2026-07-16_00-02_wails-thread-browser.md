# Agent Log - 2026-07-16 Wails Thread Browser

## Goal
Create a Wails application inside `/Users/matt/projects/ai-os` called `thread-browser` to allow search and display of interactive chat history threads.
- Do not use Tailwind. Use Mantine UI components.
- Support fast search through titles and messages.
- Order threads using a multi-dimensional relevance + recency weighting system.
- Render thread messages as markdown.
- Provide buttons to reveal files locally and open links on the web.
- Fallback gracefully to scanning directory files directly in Go if the Hermes SQLite FTS5 database is missing/uninstalled.

## User Feedback & Decisions
- Recommended searching the Hermes SQLite database (`~/.hermes/state.db`) for FTS5 trigram performance.
- User added a constraint: fallback to directory file scanning if Hermes isn't installed.

## Changes Made
- Scaffolded Wails project `thread-browser` with React-TS template.
- Implemented `app.go` with pure Go SQLite (`modernc.org/sqlite`) FTS trigram scoring search combined with started_at time for recency scoring.
- Added in-memory background scanning cache fallback in Go that reads files from `~/.gemini/antigravity-cli/brain` and `~/.gemini/antigravity-ide/brain` directly if state.db is missing.
- Designed frontend in `App.tsx` and `styles.scss` using Mantine UI v9 components, dynamic search debouncing, and collapsible tool output elements.
- Logged new feature to `FEATURES.md`.

## What Worked
- SQLite FTS5/Trigram search is extremely fast (<0.1s) and scores match the legacy Rust implementation.
- Fallback scanning handles parent-child thread tracing correctly in Go.
- `wails build` compiled the project successfully on macOS.

## What Didn't Work / Known Issues
- Initial compilation failed due to unused Go imports `io` and `time` in `app.go`; fixed by removing them.

## Architecture Notes
- Using pure Go sqlite library `modernc.org/sqlite` instead of CGO-based `github.com/mattn/go-sqlite3` prevents compilation failures on environments lacking gcc.