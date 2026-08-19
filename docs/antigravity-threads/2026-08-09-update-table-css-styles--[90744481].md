---
title: "Update Table CSS Styles"
date: "2026-08-09"
conversation_id: "90744481-d85d-451d-9c31-0dd6b66a6ef7"
source: "antigravity"
---

# Update Table CSS Styles

## User

In /Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js around lines 533-568, replace the table CSS section with:

```javascript
    /* Responsive Table Layout & Horizontal Scroll within Chat Container */
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

## Assistant

Created At: 2026-08-08T22:49:32-06:00
Completed At: 2026-08-08T22:49:32-06:00
File Path: `file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`
Total Lines: 1285
Total Bytes: 44696
Showing lines 530 to 570
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
530:         background: rgba(128, 128, 128, 0.4);
531:     }
532: 
533:     /* Responsive Table Container and Horizontal Scroll */
534:     .horizontal-scroll-wrapper, .table-block-component, .table-block, .table-content {
535:         width: 100% !important;
536:         max-width: 100% !important;
537:         overflow-x: auto !important;
538:         box-sizing: border-box !important;
539:     }
540:     table {
541:         width: max-content !important;
542:         min-width: 100% !important;
543:         max-width: none !important;
544:         border-collapse: collapse !important;
545:         table-layout: auto !important;
546:     }
547:     table th, table td {
548:         padding: 8px 12px !important;
549:         white-space: normal !important;
550:         word-break: break-word !important;
551:         width: auto !important;
552:         min-width: 80px !important;
553:     }
554:     
555:     /* Responsive adjustments for narrower viewports */
556:     @media (max-width: 1400px) {
557:         table th, table td {
558:             padding: 6px 10px !important;
559:             font-size: 14px !important; /* reduce font size slightly from default 17px */
560:             max-width: 160px !important; /* help trigger wrapping when space is constrained */
561:         }
562:     }
563: `
564: 
565: function appendStyle(styleEl) {
566: 	const doAppend = () => {
567: 		const target = document.head || document.documentElement || document.body
568: 		if (target) {
569: 			target.appendChild(styleEl)
570: 			return true
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

---
