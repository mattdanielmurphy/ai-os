# VSCode Extension Transition Plan

## The Breakthrough
During development of the custom Tauri-based desktop GUI for **AI OS**, a fundamental shift in strategy occurred. Building a desktop shell from scratch introduces unnecessary friction with terminal stability, rendering window layouts, input editors, and markdown previews. 

Instead of maintaining a custom Tauri app, the project is pivoting to a **VSCode Extension** architecture. This avoids the need to fork VSCode (which would be an overwhelmingly massive maintenance burden) while unlocking the following native capabilities:
- **Stable Terminal Integrations**: Standard VSCode terminals are robust, well-maintained, and support all keybindings natively.
- **Markdown & Output Rendering**: Built-in previewing, rich syntax styling, and interactive notebooks or panels.
- **Full-featured Editor Inputs**: Prompts can be composed using the rich editor environment (autocomplete, dynamic linting, text wrapping, automatic lists, and indent controls).
- **Extension Ecosystem**: Easy integration with other tools, file pickers, Git widgets, and workspace search features.

---

## Workspace Directory Organization
To support this fresh direction without deleting history or legacy work, the workspace has been reorganized:

```
ai-os/
├── docs/                             # Consolidated documentation & notes
│   ├── AG_CONTEXT.md
│   ├── FEATURES.md
│   ├── MEMORY.md
│   ├── VISION.md
│   ├── Nimbalyst Integration.md
│   ├── in-progress and todo.md
│   ├── Feat: Multi-Phase Gemini Web...
│   ├── the-4-phase-pipeline.md
│   └── vscode-transition-plan.md     # This file
├── legacy-tauri-gui/                 # Archived desktop GUI code
│   ├── src/
│   ├── src-tauri/
│   ├── index.html
│   ├── package.json
│   └── ...
├── bin/                              # Active orchestration CLI binaries
├── scripts/                          # Script runners & helpers
├── .agents/                          # Agent workspace profiles
├── .vscode/                          # Local editor workspace settings
├── README.md                         # Project status and general info
└── todo.md                           # Core todo ledger
```

---

## Migration Roadmap

### Phase 1: Exploration of Extension Boundaries
- Investigate VSCode Extension API limits for running/connecting to local terminal shells, wrapping active terminals, and intercepting inputs.
- Determine whether to implement a **Webview Panel** (React/TS), a **Custom Text Editor** editor flow, or utilize the new **VSCode Chat / Language Model APIs**.

### Phase 2: Integration of CLI Orchestration
- Bind the existing backend CLI layers (`bin/ai-os`, `scripts/`) to the extension host.
- Leverage the existing telemetry engine (`scripts/telemetry_db.py`) to show runtime usage and cost tracking in the editor status bar or panel.
