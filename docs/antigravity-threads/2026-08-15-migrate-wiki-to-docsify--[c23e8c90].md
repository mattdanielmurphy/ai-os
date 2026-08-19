---
title: "Migrate Wiki To Docsify"
date: "2026-08-15"
conversation_id: "c23e8c90-c986-4adc-87cb-227d09d3a77c"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; width: 100cqw; max-width: 100cqw; min-width: 100%; position: absolute; top: 0; left: calc(50% - 50cqw + 2px); bottom: 0; padding: 2.5rem 2rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 15, 2026</span>

<span style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; margin-top: 8px; overflow-wrap: anywhere; word-break: break-word;">

<span title="Sent at " style="display: block; width: fit-content; max-width: 80%; min-width: 0; margin-left: auto; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

You are a leaf file editor. Replace Quartz with Docsify for the ai-os-wiki knowledge base engine.

Perform the following tasks:

1. Create `/Users/matt/projects/ai-os/wiki-engine/index.html` with a complete, modern, standalone Docsify setup:
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
        successText: 'Copied'
      }
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

2. Create `/Users/matt/projects/ai-os/wiki-engine/_sidebar.md`:
```markdown

* **AI-OS**
  * [Overview](content/index.md)
  * [Active Architecture](content/AI-OS/active/AG_CONTEXT.md)
  * [Features](content/AI-OS/active/FEATURES.md)
  * [Vision](content/AI-OS/active/VISION.md)
  * [Memory & Protocols](content/AI-OS/active/MEMORY.md)
  * [Model Roster](content/AI-OS/active/model-roster.md)
  * [Universal Agent Framework](content/AI-OS/active/universal-agent-framework.md)

* **Personal**
  * [Habits Design](content/Personal/Habits%20Design.md)
  * [Mac Environment](content/Personal/Mac/macOS%20Environment.md)
  * [Network Location](content/Personal/Mac/Automations/Scripts/Network%20Location%20Automation.md)
  * [YouTube Scripts](content/Personal/Ideas/YouTube%20Scripts.md)
```

3. Update `/Users/matt/projects/ai-os/bin/ai-os-wiki` to:
```bash

#!/usr/bin/env bash
export PATH="/Users/matt/.bun/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export AI_OS_HOME="/Users/matt/projects/ai-os"
echo "[ai-os wiki] Starting Docsify Wiki web server on http://localhost:3333..."
cd "$AI_OS_HOME/wiki-engine" || exit 1
exec python3 -m http.server 3333 --bind 127.0.0.1
```

4. Update `/Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist`:
```xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.matt.agent.ai-os-wiki</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/matt/projects/ai-os/bin/ai-os-wiki</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/matt/projects/ai-os/wiki-engine</string>
    <key>StandardOutPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/ai-os-wiki.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/ai-os-wiki.log</string>
    <key>ProcessType</key>
    <string>Background</string>
    <key>Nice</key>
    <integer>5</integer>
</dict>
</plist>
```

</span>



<span title="Responded at 6:23am" style="display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; overflow-wrap: anywhere; word-break: break-word; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 16px 20px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

Tasks completed:
1. Created Docsify [`index.html`](file:///Users/matt/projects/ai-os/wiki-engine/index.html) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/wiki-engine/index.html) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/wiki-engine/index.html).
2. Created [`_sidebar.md`](file:///Users/matt/projects/ai-os/wiki-engine/_sidebar.md) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/wiki-engine/_sidebar.md) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/wiki-engine/_sidebar.md).
3. Updated the [`ai-os-wiki`](file:///Users/matt/projects/ai-os/bin/ai-os-wiki) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/ai-os/bin/ai-os-wiki) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/projects/ai-os/bin/ai-os-wiki) launch script.
4. Updated the LaunchAgent [`com.matt.agent.ai-os-wiki.plist`](file:///Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist) [](http://127.0.0.1:8643/open_zed?path=/Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist) [](http://127.0.0.1:8643/open_finder?path=/Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist).

The wiki is configured to serve on `http://localhost:3333`.

**Thread Metrics:**

| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~36k | 1:25am 🔴 (expired) | ~36k / ~403k 🟢 | 109, 20 🔬, 16 📤 |


| Total Tokens | Cache Expiry | Financial Rotation | Perplexity Quota |
| :--- | :--- | :--- | :--- |
| ~36k | 1:25am 🔴 (expired) | ~36k / ~403k 🟢 | 109, 20 🔬, 16 📤 |

</span>



</span>

</span>