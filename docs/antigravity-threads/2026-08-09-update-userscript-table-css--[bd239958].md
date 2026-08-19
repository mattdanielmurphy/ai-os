---
title: "Update Userscript Table CSS"
date: "2026-08-09"
conversation_id: "bd239958-60dd-4b39-868e-97671fa45cbe"
source: "antigravity"
---

# Update Userscript Table CSS

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` around lines 533-570, replace the table CSS section with:

```javascript
    /* Centered Table & Responsive Breakout Layout */
    .horizontal-scroll-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        position: relative !important;
        box-sizing: border-box !important;
        display: flex !important;
        justify-content: center !important;
        overflow-x: auto !important;
        margin: 16px 0 !important;
    }

    @media (min-width: 1024px) {
        .horizontal-scroll-wrapper {
            width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
            max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            padding: 0 48px !important;
        }
    }

    .table-block-component, .table-block, .table-content {
        width: auto !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }

    table {
        width: auto !important;
        max-width: none !important;
        margin: 0 auto !important;
        border-collapse: collapse !important;
        table-layout: auto !important;
    }

    table th, table td {
        padding: 8px 12px !important;
        white-space: normal !important;
        overflow-wrap: break-word !important;
        word-break: normal !important;
        width: auto !important;
        min-width: 120px !important;
    }

    /* Responsive adjustments for narrower viewports */
    @media (max-width: 1400px) {
        table th, table td {
            padding: 6px 10px !important;
            font-size: 14px !important;
            min-width: 100px !important;
        }
    }
```

Use replace_file_content tool.

---

## Assistant

Created At: 2026-08-09T02:44:00-06:00
Completed At: 2026-08-09T02:44:00-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1292
Total Bytes: 44911
Showing lines 533 to 570
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
533:     /* Full-width and Compact Table Layout dynamically accounting for Gemini sidebar */
534:     .horizontal-scroll-wrapper {
535:         width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
536:         max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
537:         position: relative !important;
538:         left: 50% !important;
539:         transform: translateX(-50%) !important;
540:         box-sizing: border-box !important;
541:         padding: 0 48px !important;
542:         display: block !important;
543:         overflow-x: auto !important;
544:     }
545:     .table-block-component, .table-block, .table-content {
546:         width: auto !important;
547:         max-width: 100% !important;
548:     }
549:     table {
550:         width: auto !important;
551:         max-width: 100% !important;
552:         border-collapse: collapse !important;
553:         table-layout: auto !important;
554:     }
555:     table th, table td {
556:         padding: 8px 12px !important;
557:         white-space: normal !important;
558:         word-break: break-word !important;
559:         width: auto !important;
560:         min-width: 0 !important;
561:     }
562:     
563:     /* Responsive adjustments for narrower viewports */
564:     @media (max-width: 1400px) {
565:         table th, table td {
566:             padding: 6px 10px !important;
567:             font-size: 14px !important;
568:         }
569:     }
570: `
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-09T02:44:03-06:00
Completed At: 2026-08-09T02:44:03-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -530,36 +530,51 @@
         background: rgba(128, 128, 128, 0.4);
     }
 
-    /* Full-width and Compact Table Layout dynamically accounting for Gemini sidebar */
+    /* Centered Table & Responsive Breakout Layout */
     .horizontal-scroll-wrapper {
-        width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
-        max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
+        width: 100% !important;
+        max-width: 100% !important;
         position: relative !important;
-        left: 50% !important;
-        transform: translateX(-50%) !important;
-        box-sizing: border-box !important;
-        padding: 0 48px !important;
-        display: block !important;
+        box-sizing: border-box !important;
+        display: flex !important;
+        justify-content: center !important;
         overflow-x: auto !important;
-    }
+        margin: 16px 0 !important;
+    }
+
+    @media (min-width: 1024px) {
+        .horizontal-scroll-wrapper {
+            width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
+            max-width: calc(100vw - var(--mat-sidenav-content-left-margin, 280px)) !important;
+            left: 50% !important;
+            transform: translateX(-50%) !important;
+            padding: 0 48px !important;
+        }
+    }
+
     .table-block-component, .table-block, .table-content {
         width: auto !important;
         max-width: 100% !important;
-    }
+        margin: 0 auto !important;
+    }
+
     table {
         width: auto !important;
-        max-width: 100% !important;
+        max-width: none !important;
+        margin: 0 auto !important;
         border-collapse: collapse !important;
         table-layout: auto !important;
     }
+
     table th, table td {
         padding: 8px 12px !important;
         white-space: normal !important;
-        word-break: break-word !important;
-        width: auto !important;
-        min-width: 0 !important;
-    }
-    
+        overflow-wrap: break-word !important;
+        word-break: normal !important;
+        width: auto !important;
+        min-width: 120px !important;
+    }
+
     /* Responsive adjustments for narrower viewports */
     @media (max-width: 1400px) {
         table th, table td {
@@ -566,4 +566,5 @@
             font-size: 14px !important;
+            min-width: 100px !important;
         }
     }
 `
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-09T02:44:03-06:00
Completed At: 2026-08-09T02:44:03-06:00
Message sent to "f95f31a6-4357-4258-ac44-542ff3de15f9".

The CSS section in `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` has been successfully updated as requested.

---
