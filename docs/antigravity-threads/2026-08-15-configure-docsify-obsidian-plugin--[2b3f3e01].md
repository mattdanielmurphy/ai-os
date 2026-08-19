---
title: "Configure Docsify Obsidian Plugin"
date: "2026-08-15"
conversation_id: "2b3f3e01-1541-4542-a918-3d3602c17838"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw + 2px); bottom: 0; padding: 2.5rem 2rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update the following files in `/Users/matt/projects/ai-os/wiki-engine`:

1. Update `/Users/matt/projects/ai-os/wiki-engine/index.html`:
Add a Docsify plugin to parse Obsidian wikilinks (`[[target|label]]` and `[[target]]`) in `hook.beforeEach` and strip YAML frontmatter.

The full `index.html` content should be:
```html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI-OS Knowledge Base</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="description" content="AI-OS Local Knowledge Base & Wiki">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
  
  <!-- Theme: docsify-themeable or dark/light system theme -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/docsify-themeable@0/dist/css/theme-simple.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/docsify-themeable@0/dist/css/theme-simple-dark.css" media="(prefers-color-scheme: dark)">
  
  <style>
    :root {
      --base-font-size: 15px;
      --theme-color: #3b82f6;
      --sidebar-width: 280px;
    }
    .markdown-section {
      max-width: 900px;
    }
  </style>
</head>
<body>
  <div id="app">Loading knowledge base...</div>
  <script>
    window.$docsify = {
      name: 'AI-OS Wiki',
      repo: '',
      homepage: 'content/index.md',
      loadSidebar: true,
      auto2top: true,
      subMaxLevel: 3,
      search: {
        maxAge: 86400000,
        paths: 'auto',
        placeholder: 'Search notes...',
        noData: 'No results found',
        depth: 3
      },
      copyCode: {
        buttonText: 'Copy',
        errorText: 'Error',
        successText: 'Copied',
      },
      plugins: [
        function(hook, vm) {
          hook.beforeEach(function(content) {
            // Strip YAML frontmatter if present
            content = content.replace(/^---[\s\S]*?---\n*/, '');

            // Convert Obsidian-style wikilinks: [[target|label]] or [[target]]
            return content.replace(/\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]/g, function(match, target, label) {
              var cleanTarget = target.trim();
              var displayLabel = (label || cleanTarget).trim();

              if (cleanTarget.endsWith('/')) {
                cleanTarget += 'index';
              }

              var href = cleanTarget;
              if (!href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('/')) {
                if (!href.startsWith('content/')) {
                  href = 'content/' + href;
                }
              }
              if (!href.endsWith('.md') && !href.includes('#') && !href.startsWith('http')) {
                href += '.md';
              }

              return '[' + displayLabel + '](' + href + ')';
            });
          });
        }
      ]
    }
  </script>
  <!-- Docsify Core & Plugins -->
  <script src="https://cdn.jsdelivr.net/npm/docsify@4/lib/docsify.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/docsify@4/lib/plugins/search.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/docsify-copy-code/dist/docsify-copy-code.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/docsify-themeable@0/dist/js/docsify-themeable.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-bash.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-javascript.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-json.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-python.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1/components/prism-markdown.min.js"></script>
</body>
</html>
```

2. Update `/Users/matt/projects/ai-os/wiki-engine/content/index.md`:
Convert the raw Obsidian links to clean standard markdown links so they work everywhere:
```markdown

# 🧠 Unified Knowledge Hub

Welcome to the central wiki. All documentation, personal notes, system specifications, and project concepts are cross-linked across the 6 core domains.

---

## 📂 Documentation Domains

### 1. ⚡ [AI-OS Framework & Core System](content/AI-OS/active/AG_CONTEXT.md)
Core system architecture, agent protocols, CLI tools, memory schemas, and execution workflows for `ai-os`.
- [AG_CONTEXT — System Overview](content/AI-OS/active/AG_CONTEXT.md)
- [FEATURES — Core Capabilities](content/AI-OS/active/FEATURES.md)
- [VISION — Product Roadmap](content/AI-OS/active/VISION.md)
- [MEMORY — Agent Memory Specs](content/AI-OS/active/MEMORY.md)

---

### 2. 👤 [Me & Life](content/Personal/index.md)
Personal bio, life planning, financial goals, health, and personal philosophy.
- [Habits Design](content/Personal/Habits%20Design.md)
- [Health & Fitness — Climbing & Weight Loss](content/Personal/Health%20&%20Fitness/Climbing%20Training,%20Weight%20Loss,%20and%20Grip.md)

---

### 3. 💻 [Mac System Specs & Environment](content/Personal/Mac/macOS%20Environment.md)
macOS system specs, launch agents (`la`), installed packages, Hammerspoon configs, and hardware environment.
- [macOS Environment Overview](content/Personal/Mac/macOS%20Environment.md)
- [System Automations & LaunchAgents](content/Personal/Mac/Automations/Scripts/Network%20Location%20Automation.md)

---

### 4. 💡 [Personal Notes & Creative Ideas](content/Personal/Ideas/YouTube%20Scripts.md)
Thoughts, creative writing, course notes, daily notes, and raw ideas.
- [YouTube Video Scripts](content/Personal/Ideas/YouTube%20Scripts.md)
- [AI Dev Rules & Monorepo Architecture](content/Personal/AI%20Dev%20Rules%20&%20Monorepo%20Architecture.md)

---

### 5. 🎯 [Project Concepts & PRDs](content/Personal/Development/AI%20Training,%20local%20models,%20hosting.md)
High-level product specs, product requirement documents (PRDs), and design concepts for projects before/during code creation.

---

### 6. 🛠️ [Implementations & Code Notes](content/Personal/Development/Personal%20AI%20System.md)
Implementation notes, code architecture, and internal dev logs.
- [Personal AI System](content/Personal/Development/Personal%20AI%20System.md)
- [Color Palette & Coolors](content/Personal/Development/Color%20Palette%20&%20Coolors.md)

---

## 🔍 Features
- **Global Search**: Press `Cmd + K` or click the search icon to search across all notes.
- **Bi-Directional WikiLinks**: Supports `[[Note Name]]` and `[[Target|Alias]]` links dynamically.
- **Cross-Domain Navigation**: Browse seamlessly between AI-OS architecture and personal notes.
```

</span>



<span title="Responded at 6:37am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The requested updates have been applied to the files in `/Users/matt/projects/ai-os/wiki-engine`:

1.  **Updated `index.html`**: Added the Docsify plugin in the `hook.beforeEach` function to strip YAML frontmatter and convert Obsidian-style wikilinks (`[[target|label]]` and `[[target]]`) to standard Markdown links.
2.  **Updated `content/index.md`**: Replaced all raw Obsidian links with standard Markdown links as specified.

The changes are complete.

**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~40k | 1:35am 🔴 (expired) | ~40k / ~403k 🟢 | 109, 20 🔬, 16 📤 |


| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~40k | 1:35am 🔴 (expired) | ~40k / ~403k 🟢 | 109, 20 🔬, 16 📤 |

</span>



</span>

</span>