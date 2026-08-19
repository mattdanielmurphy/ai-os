---
title: "Resolve Staging Test Conflicts"
date: "2026-08-05"
conversation_id: "da0f1c7c-7fa2-4d4f-855e-b1d38acaa6c8"
source: "antigravity"
---

# Resolve Staging Test Conflicts

## User

Please resolve the merge conflict in /Users/matt/projects/jules-burner/tests/staging/staging.test.ts.

In lines 74-97:
Replace:
<<<<<<< HEAD
    let originalToken: string | undefined;

    beforeEach(() => {
      // Mock GITHUB_TOKEN to undefined to prevent real API calls and 'Bad Credentials' errors.
      const { config } = require("../../src/config");
      originalToken = config.GITHUB_TOKEN;
=======
    let originalGitHubToken: string | undefined;

    beforeEach(() => {
      originalGitHubToken = config.GITHUB_TOKEN;
>>>>>>> origin/main
      config.GITHUB_TOKEN = undefined;
    });

    afterEach(() => {
<<<<<<< HEAD
      const { config } = require("../../src/config");
      config.GITHUB_TOKEN = originalToken;
=======
      config.GITHUB_TOKEN = originalGitHubToken;
>>>>>>> origin/main
    });

With clean code:
    let originalGitHubToken: string | undefined;

    beforeEach(() => {
      originalGitHubToken = config.GITHUB_TOKEN;
      config.GITHUB_TOKEN = undefined;
    });

    afterEach(() => {
      config.GITHUB_TOKEN = originalGitHubToken;
    });

---

## Assistant

Created At: 2026-08-05T05:01:20-06:00
Completed At: 2026-08-05T05:01:20-06:00
File Path: `file:///Users/matt/projects/jules-burner/tests/staging/staging.test.ts`
Total Lines: 196
Total Bytes: 6781
Showing lines 70 to 100
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
70:     });
71:   });
72: 
73:   describe("UpstreamPRGate", () => {
74: <<<<<<< HEAD
75:     let originalToken: string | undefined;
76: 
77:     beforeEach(() => {
78:       // Mock GITHUB_TOKEN to undefined to prevent real API calls and 'Bad Credentials' errors.
79:       const { config } = require("../../src/config");
80:       originalToken = config.GITHUB_TOKEN;
81: =======
82:     let originalGitHubToken: string | undefined;
83: 
84:     beforeEach(() => {
85:       originalGitHubToken = config.GITHUB_TOKEN;
86: >>>>>>> origin/main
87:       config.GITHUB_TOKEN = undefined;
88:     });
89: 
90:     afterEach(() => {
91: <<<<<<< HEAD
92:       const { config } = require("../../src/config");
93:       config.GITHUB_TOKEN = originalToken;
94: =======
95:       config.GITHUB_TOKEN = originalGitHubToken;
96: >>>>>>> origin/main
97:     });
98: 
99:     test("blocks PR submission when staging checks fail", async () => {
100:       const validator = new StagingValidator();
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

Created At: 2026-08-05T05:01:22-06:00
Completed At: 2026-08-05T05:01:22-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/tests/staging/staging.test.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -71,14 +71,6 @@
   });
 
   describe("UpstreamPRGate", () => {
-<<<<<<< HEAD
-    let originalToken: string | undefined;
-
-    beforeEach(() => {
-      // Mock GITHUB_TOKEN to undefined to prevent real API calls and 'Bad Credentials' errors.
-      const { config } = require("../../src/config");
-      originalToken = config.GITHUB_TOKEN;
-=======
     let originalGitHubToken: string | undefined;
 
     beforeEach(() => {
@@ -85,4 +85,3 @@
->>>>>>> origin/main
       config.GITHUB_TOKEN = undefined;
     });
 
@@ -89,9 +89,4 @@
-<<<<<<< HEAD
-      const { config } = require("../../src/config");
-      config.GITHUB_TOKEN = originalToken;
-=======
       config.GITHUB_TOKEN = originalGitHubToken;
->>>>>>> origin/main
     });
 
     test("blocks PR submission when staging checks fail", async () => {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T05:01:23-06:00
Completed At: 2026-08-05T05:01:23-06:00
Message sent to "1e58bc1c-4200-4bb7-b5f1-004f6493d7a4".

The merge conflict in `/Users/matt/projects/jules-burner/tests/staging/staging.test.ts` has been resolved.

---
