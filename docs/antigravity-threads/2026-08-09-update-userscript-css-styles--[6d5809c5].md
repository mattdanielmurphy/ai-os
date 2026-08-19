---
title: "Update Userscript CSS Styles"
date: "2026-08-09"
conversation_id: "6d5809c5-a277-4ecb-9b04-df678b539508"
source: "antigravity"
---

# Update Userscript CSS Styles

## User

In `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` around lines 533-568, update the CSS block:

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

Use `replace_file_content` targeting exact lines in `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`.

---

## Assistant

Created At: 2026-08-08T22:53:01-06:00
Completed At: 2026-08-08T22:53:01-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1291
Total Bytes: 44869
Showing lines 530 to 570
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
530:         background: rgba(128, 128, 128, 0.4);
531:     }
532: 
533:     /* Expanded Table Container - Fills Available Main Chat Area */
534:     .horizontal-scroll-wrapper {
535:         width: 100% !important;
536:         max-width: 100% !important;
537:         overflow-x: auto !important;
538:         box-sizing: border-box !important;
539:         margin: 16px 0 !important;
540:     }
541:     .table-block-component, .table-block, .table-content {
542:         width: max-content !important;
543:         min-width: 100% !important;
544:         box-sizing: border-box !important;
545:     }
546:     table {
547:         width: max-content !important;
548:         min-width: 100% !important;
549:         max-width: none !important;
550:         border-collapse: collapse !important;
551:         table-layout: auto !important;
552:     }
553:     table th, table td {
554:         padding: 8px 12px !important;
555:         white-space: normal !important;
556:         word-break: break-word !important;
557:         width: auto !important;
558:         min-width: 80px !important;
559:     }
560:     
561:     /* Responsive adjustments for narrower viewports */
562:     @media (max-width: 1400px) {
563:         table th, table td {
564:             padding: 6px 10px !important;
565:             font-size: 14px !important; /* reduce font size slightly from default 17px */
566:             max-width: 160px !important; /* help trigger wrapping when space is constrained */
567:         }
568:     }
569: `
570: 
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-08T22:53:04-06:00
Completed At: 2026-08-08T22:53:04-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -530,8 +530,9 @@
         background: rgba(128, 128, 128, 0.4);
     }
 
-    /* Expanded Table Container - Fills Available Main Chat Area */
-    .horizontal-scroll-wrapper {
+    /* Wide Breakout & Horizontally Scrollable Table Layout */
+    .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
+        display: block !important;
         width: 100% !important;
         max-width: 100% !important;
         overflow-x: auto !important;
@@ -538,11 +538,7 @@
-        margin: 16px 0 !important;
-    }
-    .table-block-component, .table-block, .table-content {
-        width: max-content !important;
-        min-width: 100% !important;
-        box-sizing: border-box !important;
+        -webkit-overflow-scrolling: touch !important;
     }
     table {
+        display: table !important;
         width: max-content !important;
         min-width: 100% !important;
         max-width: none !important;
@@ -550,10 +550,9 @@
     }
     table th, table td {
         padding: 8px 12px !important;
-        white-space: normal !important;
-        word-break: break-word !important;
+        white-space: nowrap !important;
         width: auto !important;
-        min-width: 80px !important;
+        min-width: 100px !important;
     }
     
     /* Responsive adjustments for narrower viewports */
@@ -560,7 +560,6 @@
         table th, table td {
             padding: 6px 10px !important;
-            font-size: 14px !important; /* reduce font size slightly from default 17px */
-            max-width: 160px !important; /* help trigger wrapping when space is constrained */
+            font-size: 14px !important;
         }
     }
 `
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T22:53:05-06:00
Completed At: 2026-08-08T22:53:05-06:00
Message sent to "f95f31a6-4357-4258-ac44-542ff3de15f9".

The CSS block in `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js` has been updated as requested.

---
