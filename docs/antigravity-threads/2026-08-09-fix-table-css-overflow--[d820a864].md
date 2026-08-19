---
title: "Fix Table CSS Overflow"
date: "2026-08-09"
conversation_id: "d820a864-b60a-48b6-aa48-5b80c3485a91"
source: "antigravity"
---

# Fix Table CSS Overflow

## User

In /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js, update the table CSS block (around lines 533-568) to remove viewport breaks/overflow caused by setting fixed `100vw` layout.

Specifically, replace:
```css
    /* Full-width and Compact Table Layout */
    .horizontal-scroll-wrapper {
        max-width: 100vw !important;
        overflow-x: auto !important;
        display: block !important;
        box-sizing: border-box !important;
        padding: 0 16px !important;
    }
    .table-block-component, .table-block, .table-content {
        width: max-content !important;
        min-width: 100% !important;
        box-sizing: border-box !important;
    }
    table {
        width: auto !important;
        max-width: none !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }
```
with:
```css
    /* Responsive Table Container and Horizontal Scroll */
    .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        box-sizing: border-box !important;
    }
    table {
        width: max-content !important;
        min-width: 100% !important;
        max-width: none !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }
```

Use replace_file_content tool to edit `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`.

---

## Assistant

Created At: 2026-08-08T22:49:29-06:00
Completed At: 2026-08-08T22:49:29-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -530,21 +530,16 @@
         background: rgba(128, 128, 128, 0.4);
     }
 
-    /* Full-width and Compact Table Layout */
-    .horizontal-scroll-wrapper {
-        max-width: 100vw !important;
+    /* Responsive Table Container and Horizontal Scroll */
+    .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
+        width: 100% !important;
+        max-width: 100% !important;
         overflow-x: auto !important;
-        display: block !important;
-        box-sizing: border-box !important;
-        padding: 0 16px !important;
-    }
-    .table-block-component, .table-block, .table-content {
+        box-sizing: border-box !important;
+    }
+    table {
         width: max-content !important;
         min-width: 100% !important;
-        box-sizing: border-box !important;
-    }
-    table {
-        width: auto !important;
         max-width: none !important;
         border-collapse: collapse !important;
         table-layout: auto !important;
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

---
