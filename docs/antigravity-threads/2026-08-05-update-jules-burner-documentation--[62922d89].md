---
title: "Update Jules Burner Documentation"
date: "2026-08-05"
conversation_id: "62922d89-f6dd-4ac6-bbbd-546a3a207c12"
source: "antigravity"
---

# Update Jules Burner Documentation

## User

Please resolve the merge conflict in /Users/matt/projects/jules-burner/README.md.

Replace the entire content with:
# Jules Burner

![System Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## Jules Burner Core Loop Architecture

The Jules Burner operates via an automated, local daemon built in TypeScript using Bun, which coordinates remote Google Cloud execution via the Jules CLI. The core dispatch loop (`Dispatcher`) executes the following steps continuously:

1. **Quota & Throttle Check**: Verifies that daily task quota limits have not been reached.
2. **Task Discovery**: Obtains a candidate task (e.g., a micro-bounty or an open-source contribution task).
3. **Staging Fork Preparation**: Determines a safe staging fork repository to prevent public PR spam and isolate execution.
4. **Firewall Safety Validation**: Validates the task against safety guardrails to prevent abuse or unauthorized actions.
5. **Prompt Packaging**: Packages the task description and instructions into a prompt file for Jules.
6. **Jules CLI Invocation**: Executes `jules remote new` to trigger the remote Jules execution asynchronously on Google VMs.
7. **Record & Jitter**: Logs the task dispatch and applies mathematical jitter (randomized delay) before the next cycle to prevent heuristic bot detection.
8. **Loop**: Sleeps for the specified jitter or interval duration before starting the next dispatch cycle.

This automated pipeline maximizes unused compute value while ensuring safety, throttling, and compliance.

---

## Assistant

Created At: 2026-08-05T05:01:57-06:00
Completed At: 2026-08-05T05:01:57-06:00
File Path: `file:///Users/matt/projects/jules-burner/README.md`
Total Lines: 26
Total Bytes: 1670
Showing lines 1 to 26
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: <<<<<<< HEAD
2: # Jules Burner
3: 
4: ![System Status](https://img.shields.io/badge/status-active-brightgreen.svg)
5: 
6: ## Jules Burner Core Loop Architecture
7: 
8: The Jules Burner operates via an automated, local daemon built in TypeScript using Bun, which coordinates remote Google Cloud execution via the Jules CLI. The core dispatch loop (`Dispatcher`) executes the following steps continuously:
9: 
10: 1. **Quota & Throttle Check**: Verifies that daily task quota limits have not been reached.
11: 2. **Task Discovery**: Obtains a candidate task (e.g., a micro-bounty or an open-source contribution task).
12: 3. **Staging Fork Preparation**: Determines a safe staging fork repository to prevent public PR spam and isolate execution.
13: 4. **Firewall Safety Validation**: Validates the task against safety guardrails to prevent abuse or unauthorized actions.
14: 5. **Prompt Packaging**: Packages the task description and instructions into a prompt file for Jules.
15: 6. **Jules CLI Invocation**: Executes `jules remote new` to trigger the remote Jules execution asynchronously on Google VMs.
16: 7. **Record & Jitter**: Logs the task dispatch and applies mathematical jitter (randomized delay) before the next cycle to prevent heuristic bot detection.
17: 8. **Loop**: Sleeps for the specified jitter or interval duration before starting the next dispatch cycle.
18: 
19: This automated pipeline maximizes unused compute value while ensuring safety, throttling, and compliance.
20: =======
21: # Test Repository
22: 
23: This is a simple test repository used for verifying agent capabilities and environment setup.
24: It contains basic configuration files like `.gitignore` and serves as a sandbox for basic operations.
25: >>>>>>> origin/main
26: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T05:01:59-06:00
Completed At: 2026-08-05T05:01:59-06:00
Created file file:///Users/matt/projects/jules-burner/README.md with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T05:01:59-06:00
Completed At: 2026-08-05T05:01:59-06:00
Message sent to "1e58bc1c-4200-4bb7-b5f1-004f6493d7a4".

---
