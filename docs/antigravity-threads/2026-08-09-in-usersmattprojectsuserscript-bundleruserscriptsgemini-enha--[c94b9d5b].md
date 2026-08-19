---
title: "In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` (lines 533-563), replace target content:"
date: "2026-08-09"
conversation_id: "c94b9d5b-f89d-4146-9c20-855f1738b9f9"
source: "antigravity"
---

# In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` (lines 533-563), replace target content:

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` (lines 533-563), replace target content:

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
    
    /* Responsive adjustments for narrower viewports */
    @media (max-width: 1400px) {
        table th, table td {
            padding: 6px 10px !important;
            font-size: 14px !important;
        }
    }
```

with replacement:

```javascript
    /* Full-width breakout layout dynamically accounting for Gemini sidebar width */
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
