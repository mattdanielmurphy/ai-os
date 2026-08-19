---
title: "Update Table CSS Styles"
date: "2026-08-09"
conversation_id: "ad3febd2-7389-4763-9191-bf840119a9a6"
source: "antigravity"
---

# Update Table CSS Styles

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` lines 533-562, replace with:

```javascript
    /* Wide Breakout Table Container - Dynamic based on parent main area, avoiding body text max-width constraint */
    .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        box-sizing: border-box !important;
    }
    /* Allow the table container to break out of narrow message body bounds up to full main content width */
    model-response .table-block-component, model-response .horizontal-scroll-wrapper {
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
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
    
    /* Responsive adjustments for narrower viewports */
    @media (max-width: 1400px) {
        table th, table td {
            padding: 6px 10px !important;
            font-size: 14px !important; /* reduce font size slightly from default 17px */
            max-width: 160px !important; /* help trigger wrapping when space is constrained */
        }
    }
```

Use replace_file_content tool.

---
