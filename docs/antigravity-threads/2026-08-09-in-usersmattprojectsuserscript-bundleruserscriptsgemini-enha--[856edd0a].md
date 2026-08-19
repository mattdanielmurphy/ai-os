---
title: "In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`:"
date: "2026-08-09"
conversation_id: "856edd0a-9df3-4686-b364-06495f2f8487"
source: "antigravity"
---

# In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`:

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`:

Find the exact lines:
```javascript
    /* Expanded Table Container - Fills Available Main Chat Area */
    .horizontal-scroll-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        box-sizing: border-box !important;
        margin: 16px 0 !important;
    }
    .table-block-component, .table-block, .table-content {
        width: max-content !important;
        min-width: 100% !important;
        box-sizing: border-box !important;
    }
    table {
        width: max-content !important;
        min-width: 100% !important;
        max-width: none !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }
    table th, table td {
        padding: 8px 12px !important;
        white-space: normal !important;
        word-break: break-word !important;
        width: auto !important;
        min-width: 80px !important;
    }
```

and replace them with:
```javascript
    /* Wide Breakout & Horizontally Scrollable Table Layout */
    .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
        display: block !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        box-sizing: border-box !important;
        -webkit-overflow-scrolling: touch !important;
    }
    table {
        display: table !important;
        width: max-content !important;
        min-width: 100% !important;
        max-width: none !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }
    table th, table td {
        padding: 8px 12px !important;
        white-space: nowrap !important;
        width: auto !important;
        min-width: 100px !important;
    }
```

Use replace_file_content tool.

---
