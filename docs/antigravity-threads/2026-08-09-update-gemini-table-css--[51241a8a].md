---
title: "Update Gemini Table CSS"
date: "2026-08-09"
conversation_id: "51241a8a-5a16-4810-94f2-16e1616f27f0"
source: "antigravity"
---

# Update Gemini Table CSS

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`, replace:

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

with:

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
```

Use replace_file_content tool.

---

## Assistant

Created At: 2026-08-08T22:53:55-06:00
Completed At: 2026-08-08T22:53:55-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -530,20 +530,25 @@
         background: rgba(128, 128, 128, 0.4);
     }
 
-    /* Wide Breakout & Horizontally Scrollable Table Layout */
-    .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
+    /* Full-width and Compact Table Layout dynamically accounting for Gemini sidebar */
+    .horizontal-scroll-wrapper {
+        width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
+        max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
+        position: relative !important;
+        left: 50% !important;
+        transform: translateX(-50%) !important;
+        box-sizing: border-box !important;
+        padding: 0 48px !important;
         display: block !important;
-        width: 100% !important;
-        max-width: 100% !important;
         overflow-x: auto !important;
-        box-sizing: border-box !important;
-        -webkit-overflow-scrolling: touch !important;
+    }
+    .table-block-component, .table-block, .table-content {
+        width: auto !important;
+        max-width: 100% !important;
     }
     table {
-        display: table !important;
-        width: max-content !important;
-        min-width: 100% !important;
-        max-width: none !important;
+        width: auto !important;
+        max-width: 100% !important;
         border-collapse: collapse !important;
         table-layout: auto !important;
     }
@@ -550,7 +550,8 @@
         padding: 8px 12px !important;
-        white-space: nowrap !important;
-        width: auto !important;
-        min-width: 100px !important;
+        white-space: normal !important;
+        word-break: break-word !important;
+        width: auto !important;
+        min-width: 0 !important;
     }
     
     /* Responsive adjustments for narrower viewports */
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T22:53:55-06:00
Completed At: 2026-08-08T22:53:55-06:00
Message sent to "f95f31a6-4357-4258-ac44-542ff3de15f9".

---
