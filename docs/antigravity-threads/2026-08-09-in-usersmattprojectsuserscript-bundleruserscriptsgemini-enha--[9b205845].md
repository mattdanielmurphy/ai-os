---
title: "In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` lines 533-563, replace the table CSS section with:"
date: "2026-08-09"
conversation_id: "9b205845-abb0-429d-b56a-4c230a9f75a2"
source: "antigravity"
---

# In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` lines 533-563, replace the table CSS section with:

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` lines 533-563, replace the table CSS section with:

```javascript
    /* Full-width and Compact Table Layout dynamically accounting for Gemini sidebar */
    .horizontal-scroll-wrapper {
        width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
        max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
        position: relative !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        box-sizing: border-box !important;
        padding: 0 48px !important;
        display: block !important;
        overflow-x: auto !important;
    }
    .table-block-component, .table-block, .table-content {
        width: auto !important;
        max-width: 100% !important;
    }
    table {
        width: auto !important;
        max-width: 100% !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }
    table th, table td {
        padding: 8px 12px !important;
        white-space: normal !important;
        word-break: break-word !important;
        width: auto !important;
        min-width: 0 !important;
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
