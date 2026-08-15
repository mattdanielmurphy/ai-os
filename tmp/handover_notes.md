# Handover Plan: Adapting gbrain Patterns to AI OS

This handover document summarizes the design patterns analyzed from the `gbrain` repository and outlines the goals for the next clean thread.

## Summary of Patterns to Adapt

### 1. Wiki-Link Markdown Graph
- **Concept:** Parse markdown files, contacts, and logs using Obsidian-style wikilinks (`[[Page Name]]`) and metadata frontmatter to build a zero-cost knowledge graph.
- **Goal:** Enable bi-directional page connections without databases or LLM extraction costs.

### 2. Conciseness Rule (filler reduction)
- **Concept:** Restructure prompt profiles to enforce a voice rule limiting commentary, updates, and verbose templates.
- **Goal:** Minimize token waste and improve clarity.

### 3. Visual 2D Output (SVG Charts)
- **Concept:** Write pure SVG strings programmatically to create visual dashboards (timelines, habit trackers) in markdown/HTML without frontend package dependencies.
- **Goal:** Introduce visual interfaces for tracking habits.

### 4. Clean Thread Handover Command
- **Concept:** Build a utility (e.g. `agy --handover` or a python script) that takes the current instructions, compiles a clean context markdown file, and launches a fresh orchestrator thread while closing the current one.
- **Goal:** Solve the context-bloat issue during planning-to-execution handovers.

---

## Action Items for Next Thread
1. **Implement `agy --handover` / Script:** Create the script to dump context and boot a fresh agy/Hermes thread.
2. **Refine Prompt Constraints:** Update the workspace `AGENTS.md` and global settings for strict conciseness.
3. **Habit Tracker Core:** Design the markdown-first structure using wikilinks for personal habit tracking.
